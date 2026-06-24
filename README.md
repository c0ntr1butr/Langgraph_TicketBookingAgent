# LangGraph Ticket Booking Agent

An AI-powered ticket booking assistant built using **LangGraph, Ollama, FastAPI, and React**.

The agent takes natural language travel requests, understands the user’s requirements, searches mock ticket data, suggests available options, confirms passenger details, creates a dummy booking, and displays a booking confirmation.

## Features

* Natural language ticket search
* Extracts source, destination, date, travel type, and budget
* Supports train, bus, and flight mock ticket data
* Uses LangGraph for state-based workflow
* Uses Ollama local LLM instead of paid OpenAI API
* FastAPI backend
* React + Vite frontend chat UI
* Dummy booking confirmation generation
* Local mock data storage

## Tech Stack

### Backend

* Python
* FastAPI
* LangGraph
* LangChain Ollama
* Ollama / Llama 3.2

### Frontend

* React
* Vite
* Axios
* CSS

## Project Structure

```text
Langgraph_TicketBookingAgent/
│
├── backend/
│   ├── main.py
│   ├── graph_agent.py
│   ├── mock_data.py
│   ├── schemas.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── App.css
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
└── README.md
```

## Current Limitation

This project currently uses mock ticket data. It does not access live platforms like IRCTC, RedBus, or flight booking websites.

The current version demonstrates the agent workflow using dummy ticket data. In the future, this can be upgraded by integrating authorized travel APIs, payment gateway verification, and real booking providers.

## How It Works

```text
User input
   ↓
LangGraph workflow
   ↓
Extract travel details
   ↓
Check missing information
   ↓
Search mock ticket data
   ↓
Suggest ticket options
   ↓
Collect passenger details
   ↓
Generate dummy booking confirmation
```

## Example Search Query

```text
Find me a train from Bangalore to Hyderabad tomorrow under 1500
```

## Example Booking Query

```text
Book TRN101 for Praneeth, age 23, phone 9999999999
```

## Example Output

```text
Booking confirmed!

Booking ID: BK0001
Ticket: TRN101
Passenger: Praneeth
Operator: Vande Bharat Express
Route: Bengaluru → Hyderabad
Date: 2026-06-25
Departure: 18:30
Arrival: 06:00
Price: ₹1450
Status: CONFIRMED
```

## Run Backend

```bash
cd backend
source .venv/bin/activate
python3 -m uvicorn main:app --reload --port 8000
```

Backend runs at:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

```text
http://localhost:5173
```

## Future Improvements

* Add persistent booking storage using JSON, SQLite, or PostgreSQL
* Add login/signup
* Add real travel APIs
* Add Razorpay payment gateway test flow
* Add booking history
* Add email/WhatsApp ticket confirmation
* Add live flight search using authorized APIs
* Add session memory for multi-turn conversations

## Important Note

This project is built for learning and demonstration purposes. It does not perform real ticket booking on IRCTC, RedBus, airlines, or any live travel platform.
