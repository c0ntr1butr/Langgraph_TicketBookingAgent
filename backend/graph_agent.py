from typing import TypedDict, Optional, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from mock_data import TICKETS, BOOKINGS
import json
import re


class BookingState(TypedDict):
    user_message: str
    source: Optional[str]
    destination: Optional[str]
    date: Optional[str]
    travel_type: Optional[str]
    max_price: Optional[int]
    selected_ticket_id: Optional[str]
    passenger_name: Optional[str]
    passenger_age: Optional[int]
    passenger_phone: Optional[str]
    search_results: List[Dict[str, Any]]
    response: str
    intent: str


llm = ChatOllama(
    model="llama3.2",
    temperature=0.1,
)


def extract_json_from_text(text: str) -> dict:
    """
    Ollama sometimes returns extra text around JSON.
    This function extracts the first JSON object safely.
    """
    try:
        return json.loads(text)
    except Exception:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            return {}

    return {}


def extract_details(state: BookingState) -> BookingState:
    message = state["user_message"]
    lower_msg = message.lower()

    # ---------- Rule-based fallback extraction ----------
    if "bengaluru" in lower_msg or "bangalore" in lower_msg:
        state["source"] = "Bengaluru"

    if "hyderabad" in lower_msg:
        state["destination"] = "Hyderabad"

    if "train" in lower_msg:
        state["travel_type"] = "train"
    elif "bus" in lower_msg:
        state["travel_type"] = "bus"
    elif "flight" in lower_msg:
        state["travel_type"] = "flight"

    if "tomorrow" in lower_msg or "tmrw" in lower_msg:
        state["date"] = "2026-06-25"

    price_match = re.search(r"under\s+(\d+)", lower_msg)
    if price_match:
        state["max_price"] = int(price_match.group(1))

    # Supports date format: 25-06-2026
    date_match = re.search(r"(\d{2})-(\d{2})-(\d{4})", lower_msg)
    if date_match:
        day, month, year = date_match.groups()
        state["date"] = f"{year}-{month}-{day}"

    # Supports date format: 2026-06-25
    iso_date_match = re.search(r"(\d{4})-(\d{2})-(\d{2})", lower_msg)
    if iso_date_match:
        state["date"] = iso_date_match.group(0)

    ticket_match = re.search(r"(TRN|BUS|FLT)\d+", message.upper())
    if ticket_match:
        state["selected_ticket_id"] = ticket_match.group(0)

    phone_match = re.search(r"\b\d{10}\b", message)
    if phone_match:
        state["passenger_phone"] = phone_match.group(0)

    age_match = re.search(r"age\s*(\d+)", lower_msg)
    if age_match:
        state["passenger_age"] = int(age_match.group(1))

    name_match = re.search(r"for\s+([A-Za-z]+)", message)
    if name_match:
        state["passenger_name"] = name_match.group(1)

    if "book" in lower_msg or state["selected_ticket_id"]:
        state["intent"] = "book"
    elif "find" in lower_msg or "search" in lower_msg:
        state["intent"] = "search"

    # ---------- LLM extraction ----------
    prompt = f"""
Extract ticket booking details from this user message.

User message: {message}

Current date is 2026-06-24.
If user says tomorrow or tmrw, use 2026-06-25.

Return ONLY valid JSON with these keys:
source, destination, date, travel_type, max_price, selected_ticket_id,
passenger_name, passenger_age, passenger_phone, intent.

intent should be one of:
search, book, general.

Rules:
- Convert Bangalore to Bengaluru.
- Date format must be YYYY-MM-DD.
- If not found, use null.
- max_price should be number or null.
- passenger_age should be number or null.
"""

    try:
        result = llm.invoke(prompt).content
        data = extract_json_from_text(result)
    except Exception:
        data = {}

    # Only overwrite fallback values if LLM found something useful
    if data.get("source"):
        state["source"] = data.get("source")

    if data.get("destination"):
        state["destination"] = data.get("destination")

    if data.get("date"):
        state["date"] = data.get("date")

    if data.get("travel_type"):
        state["travel_type"] = data.get("travel_type")

    if data.get("max_price"):
        state["max_price"] = data.get("max_price")

    if data.get("selected_ticket_id"):
        state["selected_ticket_id"] = data.get("selected_ticket_id")

    if data.get("passenger_name"):
        state["passenger_name"] = data.get("passenger_name")

    if data.get("passenger_age"):
        state["passenger_age"] = data.get("passenger_age")

    if data.get("passenger_phone"):
        state["passenger_phone"] = data.get("passenger_phone")

    if data.get("intent"):
        state["intent"] = data.get("intent")

    return state


def decide_next_step(state: BookingState) -> str:
    if state["intent"] == "book" or state["selected_ticket_id"]:
        return "book"

    if state["source"] and state["destination"] and state["date"]:
        return "search"

    return "ask_missing"


def ask_missing_details(state: BookingState) -> BookingState:
    missing = []

    if not state["source"]:
        missing.append("source city")

    if not state["destination"]:
        missing.append("destination city")

    if not state["date"]:
        missing.append("travel date")

    state["response"] = "Please provide " + ", ".join(missing) + " to search tickets."

    return state


def search_tickets_node(state: BookingState) -> BookingState:
    results = []

    for ticket in TICKETS:
        if state["source"] and ticket["source"].lower() != state["source"].lower():
            continue

        if state["destination"] and ticket["destination"].lower() != state["destination"].lower():
            continue

        if state["date"] and ticket["date"] != state["date"]:
            continue

        if state["max_price"] and ticket["price"] > int(state["max_price"]):
            continue

        if state["travel_type"] and ticket["type"].lower() != state["travel_type"].lower():
            continue

        if ticket["seats_available"] <= 0:
            continue

        results.append(ticket)

    state["search_results"] = results

    if not results:
        state["response"] = "No matching tickets found."
        return state

    lines = ["I found these options:\n"]

    for ticket in results:
        lines.append(
            f"{ticket['ticket_id']} - {ticket['operator']} ({ticket['type']})\n"
            f"{ticket['source']} → {ticket['destination']}\n"
            f"Date: {ticket['date']}, Departure: {ticket['departure_time']}\n"
            f"Arrival: {ticket['arrival_time']}\n"
            f"Price: ₹{ticket['price']}, Seats: {ticket['seats_available']}\n"
        )

    lines.append("Reply with the ticket ID and passenger details to book.")
    lines.append("Example: Book TRN101 for Praneeth, age 23, phone 9999999999")

    state["response"] = "\n".join(lines)

    return state


def book_ticket_node(state: BookingState) -> BookingState:
    if not state["selected_ticket_id"]:
        state["response"] = "Please provide the ticket ID you want to book."
        return state

    if not state["passenger_name"] or not state["passenger_age"] or not state["passenger_phone"]:
        state["response"] = (
            "Please provide passenger name, age, and phone number to confirm booking.\n"
            "Example: Book TRN101 for Praneeth, age 23, phone 9999999999"
        )
        return state

    ticket = None

    for item in TICKETS:
        if item["ticket_id"] == state["selected_ticket_id"]:
            ticket = item
            break

    if not ticket:
        state["response"] = "Ticket not found."
        return state

    if ticket["seats_available"] <= 0:
        state["response"] = "No seats available for this ticket."
        return state

    ticket["seats_available"] -= 1

    booking = {
        "booking_id": f"BK{len(BOOKINGS) + 1:04d}",
        "ticket_id": ticket["ticket_id"],
        "passenger_name": state["passenger_name"],
        "passenger_age": state["passenger_age"],
        "passenger_phone": state["passenger_phone"],
        "operator": ticket["operator"],
        "source": ticket["source"],
        "destination": ticket["destination"],
        "date": ticket["date"],
        "departure_time": ticket["departure_time"],
        "arrival_time": ticket["arrival_time"],
        "price": ticket["price"],
        "status": "CONFIRMED",
    }

    BOOKINGS.append(booking)

    state["response"] = (
        f"Booking confirmed!\n\n"
        f"Booking ID: {booking['booking_id']}\n"
        f"Ticket: {booking['ticket_id']}\n"
        f"Passenger: {booking['passenger_name']}\n"
        f"Operator: {booking['operator']}\n"
        f"Route: {booking['source']} → {booking['destination']}\n"
        f"Date: {booking['date']}\n"
        f"Departure: {booking['departure_time']}\n"
        f"Arrival: {booking['arrival_time']}\n"
        f"Price: ₹{booking['price']}\n"
        f"Status: {booking['status']}"
    )

    return state


workflow = StateGraph(BookingState)

workflow.add_node("extract_details", extract_details)
workflow.add_node("ask_missing", ask_missing_details)
workflow.add_node("search", search_tickets_node)
workflow.add_node("book", book_ticket_node)

workflow.set_entry_point("extract_details")

workflow.add_conditional_edges(
    "extract_details",
    decide_next_step,
    {
        "ask_missing": "ask_missing",
        "search": "search",
        "book": "book",
    },
)

workflow.add_edge("ask_missing", END)
workflow.add_edge("search", END)
workflow.add_edge("book", END)

app_graph = workflow.compile()


def run_graph_agent(message: str) -> str:
    initial_state: BookingState = {
        "user_message": message,
        "source": None,
        "destination": None,
        "date": None,
        "travel_type": None,
        "max_price": None,
        "selected_ticket_id": None,
        "passenger_name": None,
        "passenger_age": None,
        "passenger_phone": None,
        "search_results": [],
        "response": "",
        "intent": "general",
    }

    result = app_graph.invoke(initial_state)
    return result["response"]