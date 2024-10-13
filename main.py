import asyncio
import json
import os
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from inference import get_response
import logging

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


def extract_response_data(obj):
    if isinstance(obj, Response):
        return {
            "status_code": obj.status_code,
            "headers": dict(obj.headers),
            "body": obj.body.decode() if hasattr(obj, 'body') and obj.body else str(obj)
        }
    elif hasattr(obj, 'to_dict'):
        return obj.to_dict()
    elif hasattr(obj, '__dict__'):
        return {k: str(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
    else:
        return {"content": str(obj)}

@app.post("/api/post_query")
async def post_query(query: Query):
    try:
        embedding = generate_embedding(query.query)
        context = search_pinecone(embedding)
        response = get_response(query.query + "\n\nContext:\n" + "\n".join(context))

        async def generate():
            if hasattr(response, '__iter__'):
                for part in response:
                    try:
                        if isinstance(part, dict):
                            yield json.dumps(part) + "\n"
                        elif isinstance(part, str):
                            yield json.dumps({"content": part}) + "\n"
                        elif isinstance(part, Response):
                            yield json.dumps(extract_response_data(part)) + "\n"
                            break  # Stop iteration if we encounter a Response object
                        else:
                            yield json.dumps(extract_response_data(part)) + "\n"
                    except Exception as e:
                        logger.error(f"Error serializing part: {e}")
                        yield json.dumps({"error": f"Error serializing response part: {str(e)}"}) + "\n"
            else:
                yield json.dumps(extract_response_data(response)) + "\n"
            yield json.dumps({"end": True}) + "\n"  # Signal the end of the stream

        return StreamingResponse(generate(), media_type="application/x-ndjson")

    except Exception as e:
        logger.error(f"Error in post_query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/store_answer")
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)

# uvicorn main:app --reload --port 8090

# import os
# from fastapi import FastAPI, HTTPException
# from fastapi.responses import StreamingResponse, JSONResponse
# from pydantic import BaseModel
# from dotenv import load_dotenv
# from pinecone import Pinecone, ServerlessSpec
# from openai import OpenAI
# import inference
# import time

# from inference import get_response

# load_dotenv()

# app = FastAPI()

# # Initialize Pinecone
# pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
# index_name = "quickstart"

# # Check if the index exists, create it if it doesn't
# if index_name not in pc.list_indexes().names():
#     pc.create_index(
#         name=index_name,
#         dimension=1536,
#         metric="cosine",
#         spec=ServerlessSpec(cloud="aws", region="us-east-1"),
#     )
#     print(f"Index '{index_name}' created successfully.")
# else:
#     print(f"Index '{index_name}' already exists.")

# index = pc.Index(index_name)

# # Initialize OpenAI client
# openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# class Query(BaseModel):
#     query: str


# class Answer(BaseModel):
#     answer: str


# def generate_embedding(text: str):
#     response = openai_client.embeddings.create(
#         model="text-embedding-ada-002", input=text
#     )
#     return response.data[0].embedding


# def search_pinecone(embedding):
#     results = index.query(vector=embedding, top_k=5, include_metadata=True)
#     return [match.metadata.get("text", "") for match in results.matches]

# class ChatCompletionRequest(BaseModel):
#     messages: list
#     model: str
#     max_tokens: int = 2048
#     stream: bool = False

# @app.post("/chat/completions")
# async def post_query(request: ChatCompletionRequest):
#     try:
#         query = next((msg['content'] for msg in reversed(request.messages) if msg['role'] == 'user'), None)
#         print("Query:", query)
#         embedding = generate_embedding(query)
#         context = search_pinecone(embedding)

#         response = get_response(query + "\n\nContext:\n" + "\n".join(context))
#         _response = max(
#             (message["content"] for message in response.messages if message["content"]),
#             key=len,
#             default="",
#         )

#         store_answer(query, _response)

#         openai_response = {
#             "id": "chatcmpl-" + os.urandom(12).hex(),
#             "object": "chat.completion",
#             "created": int(time.time()),
#             "model": request.model,
#             "choices": [{
#                 "index": 0,
#                 "message": {
#                     "role": "assistant",
#                     "content": _response
#                 },
#                 "finish_reason": "stop"
#             }],
#             "usage": {
#                 "prompt_tokens": len(query.split()),
#                 "completion_tokens": len(_response.split()),
#                 "total_tokens": len(query.split()) + len(_response.split())
#             }
#         }

#         print("Response:", openai_response)
#         return JSONResponse(content=openai_response, media_type="application/json")

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @app.post("/store_answer")
# async def store_answer_endpoint(query: Query, answer: Answer):
#     try:
#         store_answer(query.query, answer.answer)
#         return {"message": "Answer stored successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# def store_answer(question: str, answer: str):
#     embedding = generate_embedding(answer)
#     index.upsert(
#         vectors=[
#             {
#                 "id": f"q_{hash(question)}",
#                 "values": embedding,
#                 "metadata": {"text": answer, "question": question},
#             }
#         ]
#     )


# @app.get("/test")
# async def test_endpoint():
#     return {"message": "Server is running"}


# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)

# # uvicorn main:app --reload --port 8090


