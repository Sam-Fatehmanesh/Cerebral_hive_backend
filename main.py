import os
import pprint
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
import inference
import time
import asyncio
import json

from inference import get_response

load_dotenv()

app = FastAPI()

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = "quickstart"

# Check if the index exists, create it if it doesn't
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
    print(f"Index '{index_name}' created successfully.")
else:
    print(f"Index '{index_name}' already exists.")

index = pc.Index(index_name)

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class Query(BaseModel):
    query: str


class Answer(BaseModel):
    answer: str


def generate_embedding(text: str):
    response = openai_client.embeddings.create(
        model="text-embedding-ada-002", input=text
    )
    return response.data[0].embedding


def search_pinecone(embedding):
    results = index.query(vector=embedding, top_k=5, include_metadata=True)
    return [match.metadata.get("text", "") for match in results.matches]

class ChatCompletionRequest(BaseModel):
    messages: list
    model: str
    max_tokens: int = 2048
    stream: bool = False

@app.post("/chat/completions")
async def post_query(request: ChatCompletionRequest):
    try:
        query = next((msg['content'] for msg in reversed(request.messages) if msg['role'] == 'user'), None)
        print("Query:", query)
        embedding = generate_embedding(query)
        context = search_pinecone(embedding)

        response = get_response(query + "\n\nContext:\n" + "\n".join(context))
        
        async def generate():
            full_response = ""
            for message in response.messages:
                if message["content"]:
                    chunk = {
                        "id": "chatcmpl-" + os.urandom(12).hex(),
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "model": request.model,
                        "choices": [{
                            "index": 0,
                            "delta": {
                                "role": "assistant",
                                "content": message["content"]
                            },
                            "finish_reason": None
                        }]
                    }
                    yield f"data: {json.dumps(chunk)}\n\n"
                    full_response += message["content"]
                    await asyncio.sleep(0.01)
            
            # Store the answer after generating the full response
            store_answer(query, full_response)
            
            yield "data: [DONE]\n\n"

        if request.stream:
            return StreamingResponse(generate(), media_type="text/event-stream")
        else:
            _response = max(
                (message["content"] for message in response.messages if message["content"]),
                key=len,
                default="",
            )

            # Store the answer for non-streaming response
            store_answer(query, _response)

            openai_response = {
                "id": "chatcmpl-" + os.urandom(12).hex(),
                "object": "chat.completion",
                "created": int(time.time()),
                "model": request.model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": _response
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": len(query.split()),
                    "completion_tokens": len(_response.split()),
                    "total_tokens": len(query.split()) + len(_response.split())
                }
            }

            return JSONResponse(content=openai_response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/store_answer")
async def store_answer_endpoint(query: Query, answer: Answer):
    try:
        store_answer(query.query, answer.answer)
        return {"message": "Answer stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def store_answer(question: str, answer: str):
    embedding = generate_embedding(answer)
    index.upsert(
        vectors=[
            {
                "id": f"q_{hash(question)}",
                "values": embedding,
                "metadata": {"text": answer, "question": question},
            }
        ]
    )


@app.get("/test")
async def test_endpoint():
    return {"message": "Server is running"}


def print_vector_db_contents():
    print("Contents of the Pinecone Vector Database:")
    try:
        # Get index statistics
        stats = index.describe_index_stats()
        print(f"Total vectors: {stats.total_vector_count}")
        print(f"Dimension: {stats.dimension}")

        # Fetch all vectors
        fetch_response = index.query(
            vector=[0.0] * stats.dimension,  # dummy vector
            top_k=stats.total_vector_count,
            include_values=True,
            include_metadata=True
        )
        
        if not fetch_response.matches:
            print("No vectors found in the database.")
            return

        for match in fetch_response.matches:
            print(f"\nID: {match.id}")
            print("Metadata:")
            pprint.pprint(match.metadata)
            print("Vector (first 5 elements):")
            print(match.values[:5])
            print("-" * 50)
    except Exception as e:
        print(f"An error occurred while fetching vector database contents: {e}")
        print("Index description:")
        pprint.pprint(index.describe_index_stats().to_dict())
        
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)

# uvicorn main:app --reload --port 8090
