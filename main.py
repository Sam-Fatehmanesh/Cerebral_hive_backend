import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI

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
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        ) 
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
    response = openai_client.embeddings.create(model="text-embedding-ada-002", input=text)
    return response.data[0].embedding

def search_pinecone(embedding):
    results = index.query(
        vector=embedding,
        top_k=5,
        include_metadata=True
    )
    return [match.metadata.get('text', '') for match in results.matches]

@app.post("/api/get_context")
async def get_context(query: Query):
    try:
        # Generate embedding for the query
        embedding = generate_embedding(query.query)
        
        # Search Pinecone for relevant context
        context = search_pinecone(embedding)
        
        return {"context": context}
    
    except Exception as e:
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
        vectors=[{
            "id": f"q_{hash(question)}",
            "values": embedding,
            "metadata": {
                "text": answer,
                "question": question
            }
        }]
    )

@app.get("/test")
async def test_endpoint():
    return {"message": "Server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)

# uvicorn main:app --reload --port 8084 