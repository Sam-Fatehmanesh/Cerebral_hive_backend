import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx
import pinecone
from openai import OpenAI

load_dotenv()

app = FastAPI()

# Initialize Pinecone
pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENVIRONMENT"))
index = pinecone.Index(os.getenv("PINECONE_INDEX_NAME"))

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Query(BaseModel):
    query: str
    continue_api_key: str
    role_id: str  # Add role_id to the query model

async def generate_embedding(text: str):
    response = await openai_client.embeddings.create(model="text-embedding-ada-002", input=text)
    return response.data[0].embedding

async def search_pinecone(embedding, role_id):
    results = index.query(
        vector=embedding,
        top_k=5,
        include_metadata=True,
        filter={"role_id": role_id}  # Add filter for role_id
    )
    return [match.metadata.text for match in results.matches]

@app.post("/api/query")
async def query_api(query: Query):
    try:
        # Generate embedding for the query
        embedding = await generate_embedding(query.query)
        
        # Search Pinecone for relevant context within the same role
        context = await search_pinecone(embedding, query.role_id)
        
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
        
        # Store the answer in Pinecone with role_id
        await store_answer(query.query, answer, query.role_id)
        
        return continue_response.json()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def store_answer(question: str, answer: str, role_id: str):
    embedding = await generate_embedding(answer)
    index.upsert(
        vectors=[{
            "id": f"q_{hash(question)}_{role_id}",
            "values": embedding,
            "metadata": {
                "text": answer,
                "question": question,
                "role_id": role_id
            }
        }]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)