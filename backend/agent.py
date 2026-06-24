from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from tools import search_tickets, book_ticket

SYSTEM_INSTRUCTION = """
You are an AI ticket booking assistant.

You help users search and book train, bus, or flight tickets.

Current date is 2026-06-24.

Rules:
1. Collect source, destination, travel date, travel type, and budget if provided.
2. Use search_tickets to find available options.
3. Do not book unless user clearly confirms.
4. Before booking, collect passenger name, age, phone number, and selected ticket_id.
5. Keep responses short and clear.
"""

llm = ChatOllama(
    model="llama3.2",
    temperature=0.2,
)

agent = create_react_agent(
    model=llm,
    tools=[search_tickets, book_ticket],
    prompt=SYSTEM_INSTRUCTION,
)


def run_agent(message: str) -> str:
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": message,
                }
            ]
        }
    )

    return result["messages"][-1].content