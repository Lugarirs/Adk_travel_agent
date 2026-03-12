"""
Flight Agent - Specialist for flight search and booking queries.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

GEMINI_MODEL = "gemini-2.0-flash"


# ── Tools ──────────────────────────────────────────────────────────────────────

def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str = "",
    passengers: int = 1,
) -> dict:
    """
    Search for available flights between two cities.

    Args:
        origin: Departure city or airport code (e.g. "New York" or "JFK")
        destination: Arrival city or airport code (e.g. "Paris" or "CDG")
        departure_date: Date in YYYY-MM-DD format
        return_date: Return date in YYYY-MM-DD format (empty for one-way)
        passengers: Number of passengers (default 1)

    Returns:
        A dictionary with available flight options and prices.
    """
    # Mock flight data — replace with real API (Amadeus, Skyscanner, etc.)
    trip_type = "Round-trip" if return_date else "One-way"
    return {
        "status": "success",
        "search": {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "return_date": return_date or "N/A",
            "passengers": passengers,
            "trip_type": trip_type,
        },
        "flights": [
            {
                "flight_id": "FL001",
                "airline": "Air France",
                "flight_number": "AF 007",
                "departure": f"{departure_date} 08:30",
                "arrival": f"{departure_date} 22:15",
                "duration": "7h 45m",
                "stops": "Non-stop",
                "price_per_person": 620,
                "total_price": 620 * passengers,
                "currency": "USD",
                "class": "Economy",
            },
            {
                "flight_id": "FL002",
                "airline": "Delta Airlines",
                "flight_number": "DL 401",
                "departure": f"{departure_date} 11:00",
                "arrival": f"{departure_date} 23:50",
                "duration": "8h 50m",
                "stops": "1 stop (London)",
                "price_per_person": 480,
                "total_price": 480 * passengers,
                "currency": "USD",
                "class": "Economy",
            },
            {
                "flight_id": "FL003",
                "airline": "Air France",
                "flight_number": "AF 009",
                "departure": f"{departure_date} 16:45",
                "arrival": f"{departure_date} 06:30+1",
                "duration": "7h 45m",
                "stops": "Non-stop",
                "price_per_person": 1250,
                "total_price": 1250 * passengers,
                "currency": "USD",
                "class": "Business",
            },
        ],
    }


def get_flight_details(flight_id: str) -> dict:
    """
    Get detailed information about a specific flight.

    Args:
        flight_id: The unique flight identifier from search results

    Returns:
        Detailed flight information including baggage policy and amenities.
    """
    details = {
        "FL001": {
            "flight_id": "FL001",
            "airline": "Air France",
            "baggage": {"carry_on": "1 x 12kg", "checked": "1 x 23kg included"},
            "meals": "Full meal service included",
            "entertainment": "Seatback screens with movies & music",
            "wifi": "Available ($12/flight)",
            "cancellation": "Free cancellation within 24 hours of booking",
            "seat_map": "3-3-3 configuration, 31 inch pitch",
        },
        "FL002": {
            "flight_id": "FL002",
            "baggage": {"carry_on": "1 x 10kg", "checked": "Not included (add $45)"},
            "meals": "Snacks only",
            "entertainment": "Streaming to personal device",
            "wifi": "Available ($8/flight)",
            "cancellation": "Non-refundable, changes $75",
            "layover": "2h 15m in London Heathrow (LHR), Terminal 5",
        },
    }
    return details.get(
        flight_id,
        {"status": "error", "message": f"Flight {flight_id} not found."},
    )


# ── Agent definition ───────────────────────────────────────────────────────────

flight_agent = LlmAgent(
    name="FlightAgent",
    model=GEMINI_MODEL,
    description=(
        "Specialist agent for finding and comparing flights. "
        "Handles flight searches, pricing, schedules, baggage policies, "
        "and flight details between any two cities or airports."
    ),
    instruction="""
You are an expert flight booking assistant. Your sole responsibility is to help
users find the best flights for their trip.

When helping users:
1. Always use the search_flights tool to find available options.
2. Present results in a clear, easy-to-compare format with prices, duration, and stops.
3. Highlight the best value and best comfort options.
4. Use get_flight_details when the user wants more info on a specific flight.
5. Provide practical tips (e.g., best time to book, baggage advice).
6. Always mention the total price for all passengers, not just per-person price.

Format flight results as a numbered list with key details on each line.
Be concise but thorough — travelers need accurate info to make decisions.
""",
    tools=[
        FunctionTool(search_flights),
        FunctionTool(get_flight_details),
    ],
    output_key="flight_results",
)
