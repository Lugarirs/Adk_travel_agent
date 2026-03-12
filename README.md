# ✈️ ARIA — Travel Concierge

A full-service AI travel planning app built with **Google ADK**, **Gemini 3.1 Flash Lite**, and **FastAPI**.

## Architecture

```
TravelConcierge  (Root Orchestrator — ARIA)
├── FlightAgent       → search_flights, get_flight_details
├── HotelAgent        → search_hotels, get_hotel_details
└── ActivitiesAgent   → search_activities, get_local_tips
```

## Project Structure

```
travel_concierge/
├── main.py               # FastAPI server + SSE streaming
├── agent.py              # Root concierge agent
├── flight_agent.py       # Flight specialist
├── hotel_agent.py        # Hotel specialist
├── activities_agent.py   # Activities specialist
├── __init__.py
├── requirements.txt
├── render.yaml           # Render deployment config
└── static/
    └── index.html        # Frontend UI
```

## Local Development

```bash
# 1. Create and activate virtualenv
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your API key
echo "GOOGLE_API_KEY=your_key_here" > .env

# 4. Run
python main.py
# → http://localhost:8000
```

## Deploy to Render

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Render auto-detects `render.yaml`
5. Add `GOOGLE_API_KEY` in Environment Variables
6. Click **Deploy** 🚀

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | ✅ | Google AI Studio API key |

Get a free key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)