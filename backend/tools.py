from langchain.tools import tool
from mock_data import TICKETS, BOOKINGS
import json


@tool
def search_tickets(query: str) -> str:
    """
    Search available tickets.
    Input must be JSON string with source, destination, date, optional max_price, optional travel_type.
    """

    try:
        data = json.loads(query)
    except Exception:
        return "Invalid JSON input."

    source = data.get("source", "").lower()
    destination = data.get("destination", "").lower()
    date = data.get("date")
    max_price = data.get("max_price")
    travel_type = data.get("travel_type")

    results = []

    for ticket in TICKETS:
        if ticket["source"].lower() != source:
            continue
        if ticket["destination"].lower() != destination:
            continue
        if ticket["date"] != date:
            continue
        if max_price and ticket["price"] > int(max_price):
            continue
        if travel_type and ticket["type"].lower() != travel_type.lower():
            continue
        if ticket["seats_available"] <= 0:
            continue

        results.append(ticket)

    if not results:
        return "No matching tickets found."

    return json.dumps(results, indent=2)


@tool
def book_ticket(query: str) -> str:
    """
    Book a ticket.
    Input must be JSON string with ticket_id, passenger_name, passenger_age, passenger_phone.
    """

    try:
        data = json.loads(query)
    except Exception:
        return "Invalid JSON input."

    ticket_id = data.get("ticket_id")

    ticket = None
    for item in TICKETS:
        if item["ticket_id"] == ticket_id:
            ticket = item
            break

    if not ticket:
        return "Ticket not found."

    if ticket["seats_available"] <= 0:
        return "No seats available."

    ticket["seats_available"] -= 1

    booking = {
        "booking_id": f"BK{len(BOOKINGS) + 1:04d}",
        "ticket_id": ticket_id,
        "passenger_name": data.get("passenger_name"),
        "passenger_age": data.get("passenger_age"),
        "passenger_phone": data.get("passenger_phone"),
        "operator": ticket["operator"],
        "source": ticket["source"],
        "destination": ticket["destination"],
        "date": ticket["date"],
        "departure_time": ticket["departure_time"],
        "price": ticket["price"],
        "status": "CONFIRMED",
    }

    BOOKINGS.append(booking)

    return json.dumps(booking, indent=2)