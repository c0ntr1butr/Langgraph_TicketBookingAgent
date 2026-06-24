from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schemas import ChatRequest
from graph_agent import run_graph_agent

app = FastAPI(title="AI Ticket Booking Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "AI Ticket Booking Agent is running"}


@app.post("/chat")
def chat(request: ChatRequest):
    try:
        response = run_graph_agent(request.message)
        return {"success": True, "response": response}
    except Exception as e:
        return {"success": False, "error": str(e)}