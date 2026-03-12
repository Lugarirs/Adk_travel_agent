"""
Hotel Agent - Specialist for hotel search, comparison, and booking queries.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

GEMINI_MODEL = "gemini-2.0-flash"


# ── Tools ──────────────────────────────────────────────────────────────────────

def search_hotels(
    city: str,
    check_in: str,
    check_out: str,
    guests: int = 2,
    budget_per_night: str = "any",
) -> dict:
    """
    Search for available hotels in a city.

    Args:
        city: Destination city name (e.g. "Paris")
        check_in: Check-in date in YYYY-MM-DD format
        check_out: Check-out date in YYYY-MM-DD format
        guests: Number of guests (default 2)
        budget_per_night: Budget range like "budget", "mid-range", "luxury", or "any"

    Returns:
        A dictionary with available hotels and pricing.
    """
    # Mock hotel data — replace with real API (Booking.com, Expedia, etc.)
    from datetime import datetime
    nights = (datetime.strptime(check_out, "%Y-%m-%d") - datetime.strptime(check_in, "%Y-%m-%d")).days

    hotels = [
        {
            "hotel_id": "H001",
            "name": "Hotel Le Marais",
            "category": "mid-range",
            "stars": 3,
            "rating": 8.4,
            "reviews": 2341,
            "price_per_night": 145,
            "total_price": 145 * nights,
            "currency": "USD",
            "location": "Le Marais, Central Paris",
            "distance_to_center": "0.8 km",
            "amenities": ["Free WiFi", "Breakfast included", "24h reception"],
            "room_type": "Standard Double",
        },
        {
            "hotel_id": "H002",
            "name": "Ibis Paris Gare de Lyon",
            "category": "budget",
            "stars": 2,
            "rating": 7.6,
            "reviews": 5210,
            "price_per_night": 85,
            "total_price": 85 * nights,
            "currency": "USD",
            "location": "12th Arrondissement",
            "distance_to_center": "2.1 km",
            "amenities": ["Free WiFi", "On-site restaurant", "Metro nearby"],
            "room_type": "Standard Room",
        },
        {
            "hotel_id": "H003",
            "name": "Hôtel Plaza Athénée",
            "category": "luxury",
            "stars": 5,
            "rating": 9.5,
            "reviews": 980,
            "price_per_night": 1200,
            "total_price": 1200 * nights,
            "currency": "USD",
            "location": "Avenue Montaigne, 8th Arrondissement",
            "distance_to_center": "1.2 km",
            "amenities": [
                "Spa & pool", "Michelin-star restaurant", "Butler service",
                "Free WiFi", "Airport transfer", "Concierge",
            ],
            "room_type": "Deluxe Room",
        },
        {
            "hotel_id": "H004",
            "name": "Citadines Bastille Paris",
            "category": "mid-range",
            "stars": 3,
            "rating": 8.1,
            "reviews": 1872,
            "price_per_night": 130,
            "total_price": 130 * nights,
            "currency": "USD",
            "location": "Bastille, 11th Arrondissement",
            "distance_to_center": "1.5 km",
            "amenities": ["Kitchenette", "Free WiFi", "Laundry", "Gym"],
            "room_type": "Studio Apartment",
        },
    ]

    # Filter by budget if specified
    budget_map = {
        "budget": ["budget"],
        "mid-range": ["mid-range"],
        "luxury": ["luxury"],
        "any": ["budget", "mid-range", "luxury"],
    }
    allowed = budget_map.get(budget_per_night.lower(), ["budget", "mid-range", "luxury"])
    filtered = [h for h in hotels if h["category"] in allowed]

    return {
        "status": "success",
        "search": {
            "city": city,
            "check_in": check_in,
            "check_out": check_out,
            "nights": nights,
            "guests": guests,
            "budget_filter": budget_per_night,
        },
        "hotels": filtered,
    }


def get_hotel_details(hotel_id: str) -> dict:
    """
    Get detailed information about a specific hotel.

    Args:
        hotel_id: The unique hotel identifier from search results

    Returns:
        Detailed hotel info including policies, nearby attractions, and room options.
    """
    details = {
        "H001": {
            "hotel_id": "H001",
            "name": "Hotel Le Marais",
            "description": "A charming boutique hotel nestled in the historic Le Marais district, steps from the Pompidou Centre and Place des Vosges.",
            "check_in_time": "15:00",
            "check_out_time": "11:00",
            "cancellation": "Free cancellation up to 48 hours before check-in",
            "parking": "No on-site parking. Public parking 200m away ($25/day)",
            "breakfast": "Continental breakfast included ($0 extra)",
            "pets": "Pets not allowed",
            "nearby": ["Pompidou Centre (5 min walk)", "Place des Vosges (8 min walk)", "Marais restaurants"],
        },
        "H003": {
            "hotel_id": "H003",
            "name": "Hôtel Plaza Athénée",
            "description": "Iconic Parisian palace hotel on the most glamorous avenue in Paris, legendary for its red geranium facade and Dior Spa.",
            "check_in_time": "15:00",
            "check_out_time": "12:00",
            "cancellation": "Free cancellation up to 7 days before check-in",
            "parking": "Valet parking available ($60/day)",
            "breakfast": "À la carte breakfast ($65/person)",
            "pets": "Pets welcome (up to 5kg)",
            "nearby": ["Eiffel Tower (15 min walk)", "Champs-Élysées (5 min walk)", "Seine River (10 min walk)"],
        },
    }
    return details.get(
        hotel_id,
        {"status": "error", "message": f"Hotel {hotel_id} not found."},
    )


# ── Agent definition ───────────────────────────────────────────────────────────

hotel_agent = LlmAgent(
    name="HotelAgent",
    model=GEMINI_MODEL,
    description=(
        "Specialist agent for finding and comparing hotels and accommodation. "
        "Handles hotel searches, room types, pricing, amenities, cancellation policies, "
        "and local area information for any destination."
    ),
    instruction="""
You are an expert hotel and accommodation specialist. Your sole responsibility is
to help travelers find the perfect place to stay.

When helping users:
1. Always use search_hotels to find available properties.
2. Present options organized by value: budget, mid-range, and luxury tiers.
3. Highlight star rating, guest review score, location, and total cost for the stay.
4. Use get_hotel_details when the user wants more info about a specific property.
5. Point out standout features — e.g., "Breakfast included saves ~$30/day per person."
6. Give location context: proximity to main attractions, public transport, etc.
7. Mention cancellation policies proactively — this matters to travelers.

Always calculate the TOTAL price for the full stay (not just per night).
Format results as a numbered list with clear tiers.
""",
    tools=[
        FunctionTool(search_hotels),
        FunctionTool(get_hotel_details),
    ],
    output_key="hotel_results",
)
