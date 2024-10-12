import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI

load_dotenv()

app = FastAPI()

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = "quickstart"
pc.create_index(
    name=index_name,
    dimension=1536,
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    ) 
)
index = pc.Index(index_name)

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Query(BaseModel):
    query: str
    continue_api_key: str

async def generate_embedding(text: str):
    response = await openai_client.embeddings.create(model="text-embedding-ada-002", input=text)
    return response.data[0].embedding

async def search_pinecone(embedding):
    results = index.query(
        vector=embedding,
        top_k=5,
        include_metadata=True
    )
    return [match.metadata.text for match in results.matches]

@app.post("/api/query")
async def query_api(query: Query):
    try:
        # Generate embedding for the query
        embedding = await generate_embedding(query.query)
        
        # Search Pinecone for relevant context
        context = await search_pinecone(embedding)
        
        # Forward request to Continue API with added context
        async with httpx.AsyncClient() as client:
            continue_response = await client.post(
                "https://continue.dev/api/query",
                json={
                    "query": query.query,
                    "context": context,
                    "apiKey": query.continue_api_key
                }
            )
        
        # Extract the answer from the Continue API response
        answer = continue_response.json()["answer"]
        
        # Store the answer in Pinecone
        await store_answer(query.query, answer)
        
        return continue_response.json()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def store_answer(question: str, answer: str):
    embedding = await generate_embedding(answer)
    index.upsert(
        vectors=[{
            "id": f"q_{hash(question)}",
            "values": embedding,
            "metadata": {
                "text": answer,
                "question": question
            }
        }]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)