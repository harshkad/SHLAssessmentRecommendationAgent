from fastapi import FastAPI

from app.models import ChatRequest

from app.rag import generate_reply


app = FastAPI()


@app.get("/health")
def health():

    return {
        "status": "ok"
    }


@app.post("/chat")
def chat(request: ChatRequest):

    result = generate_reply(
        [m.dict() for m in request.messages]
    )

    return result