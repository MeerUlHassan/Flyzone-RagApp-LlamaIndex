from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import uvicorn
from flyzone_rag import get_answer_with_memory  

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    retrieved_nodes: List[str]

# API Endpoint
@app.post("/query", response_model=QueryResponse, tags=["RAG"])
async def query_rag(request: QueryRequest):
    retrieved_nodes, answer = get_answer_with_memory(request.query)
    return QueryResponse(
        answer=str(answer),
        retrieved_nodes=[str(node) for node in retrieved_nodes]
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
