"""
Activities Agent - Specialist for local experiences, tours, and attractions.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

GEMINI_MODEL = "gemini-2.0-flash"


# ── Tools ──────────────────────────────────────────────────────────────────────

def search_activities(
    city: str,
    interests: str = "general sightseeing",
    duration_days: int = 3,
    travel_style: str = "balanced",
) -> dict:
    """
    Search for activities, tours, and attractions in a city.

    Args:
        city: Destination city (e.g. "Paris")
        interests: Comma-separated interests (e.g. "art, history, food, adventure")
        duration_days: Number of days available for activities
        travel_style: "budget", "balanced", or "premium"

    Returns:
        A curated list of activities and experiences.
    """
    # Mock activity data — replace with Viator, GetYourGuide API, etc.
    activities = [
        {
            "activity_id": "A001",
            "name": "Eiffel Tower Summit Guided Tour",
            "category": "Landmark",
            "duration": "2.5 hours",
            "price": 65,
            "currency": "USD",
            "rating": 9.2,
            "reviews": 18400,
            "description": "Skip-the-line access to the Eiffel Tower summit with an expert guide.",
            "highlights": ["Skip-the-line tickets", "Summit access", "Panoramic views", "Guide included"],
            "best_for": "First-time visitors",
            "booking_required": True,
            "style": "balanced",
        },
        {
            "activity_id": "A002",
            "name": "Louvre Museum Self-Guided Visit",
            "category": "Museum & Art",
            "duration": "3-4 hours",
            "price": 22,
            "currency": "USD",
            "rating": 9.0,
            "reviews": 52000,
            "description": "Explore the world's largest art museum at your own pace.",
            "highlights": ["Mona Lisa", "Venus de Milo", "Ancient Egypt wing", "Free audio guide app"],
            "best_for": "Art & history lovers",
            "booking_required": True,
            "style": "budget",
        },
        {
            "activity_id": "A003",
            "name": "Seine River Dinner Cruise",
            "category": "Food & Dining",
            "duration": "2 hours",
            "price": 95,
            "currency": "USD",
            "rating": 8.7,
            "reviews": 7200,
            "description": "Romantic evening cruise along the Seine with a 3-course French dinner.",
            "highlights": ["3-course dinner", "Live music", "Views of Notre-Dame & Louvre", "Welcome drink"],
            "best_for": "Couples & special occasions",
            "booking_required": True,
            "style": "premium",
        },
        {
            "activity_id": "A004",
            "name": "Montmartre & Sacré-Cœur Walking Tour",
            "category": "Neighbourhood Tour",
            "duration": "3 hours",
            "price": 18,
            "currency": "USD",
            "rating": 9.4,
            "reviews": 11000,
            "description": "Explore bohemian Montmartre with a local guide — artists, cafes, and the iconic basilica.",
            "highlights": ["Sacré-Cœur Basilica", "Artist quarter", "Vineyard", "Local café stop"],
            "best_for": "Culture & photography lovers",
            "booking_required": False,
            "style": "budget",
        },
        {
            "activity_id": "A005",
            "name": "French Cooking Class in a Parisian Kitchen",
            "category": "Food & Cooking",
            "duration": "3.5 hours",
            "price": 120,
            "currency": "USD",
            "rating": 9.6,
            "reviews": 3400,
            "description": "Learn to cook classic French dishes with a professional chef, then enjoy your meal.",
            "highlights": ["Market visit", "Chef instruction", "3 dishes", "Wine pairing", "Recipe booklet"],
            "best_for": "Foodies & hands-on experiences",
            "booking_required": True,
            "style": "premium",
        },
        {
            "activity_id": "A006",
            "name": "Versailles Palace Day Trip",
            "category": "Day Trip",
            "duration": "Full day (8 hours)",
            "price": 55,
            "currency": "USD",
            "rating": 9.1,
            "reviews": 21000,
            "description": "Guided day trip to the Palace of Versailles including gardens and Hall of Mirrors.",
            "highlights": ["Hall of Mirrors", "Royal Gardens", "Grand Trianon", "Skip-the-line"],
            "best_for": "History buffs",
            "booking_required": True,
            "style": "balanced",
        },
    ]

    return {
        "status": "success",
        "search": {
            "city": city,
            "interests": interests,
            "duration_days": duration_days,
            "travel_style": travel_style,
        },
        "activities": activities,
        "suggested_itinerary_tip": (
            f"For {duration_days} days in {city}, we recommend mixing 1 major landmark, "
            "1 neighbourhood tour, 1 food experience, and 1 day trip for a well-rounded visit."
        ),
    }


def get_local_tips(city: str) -> dict:
    """
    Get insider local tips and practical travel advice for a city.

    Args:
        city: Destination city name

    Returns:
        Local tips covering transport, dining, culture, and money-saving advice.
    """
    tips_db = {
        "paris": {
            "city": "Paris",
            "transport": [
                "Buy a Navigo Easy card for unlimited metro/bus rides (~€16.90/week)",
                "The metro runs until ~01:15 on weekdays and ~02:15 on weekends",
                "RER B connects CDG airport to city center in 35 min for €11.80",
            ],
            "dining": [
                "Lunch menus ('formule') at sit-down restaurants offer 2-3 courses for €12-18",
                "Avoid restaurants directly on major tourist squares — walk one block back",
                "Supermarkets (Monoprix, Carrefour City) have excellent wine and cheese for picnics",
            ],
            "culture": [
                "Most national museums are free on the first Sunday of the month",
                "Greet shopkeepers with 'Bonjour' when entering — it's expected etiquette",
                "Tipping is appreciated but not mandatory (round up or leave 5-10% max)",
            ],
            "best_times": "April–June and September–October for mild weather and fewer crowds.",
            "avoid": "July–August peak crowds and heat. Book everything in advance if you must go.",
        }
    }
    city_key = city.lower()
    return tips_db.get(
        city_key,
        {
            "city": city,
            "tips": [
                "Check local tourism board website for up-to-date events",
                "Download Google Maps offline for the city before you arrive",
                "Learn a few basic phrases in the local language — locals appreciate the effort",
            ],
        },
    )


# ── Agent definition ───────────────────────────────────────────────────────────

activities_agent = LlmAgent(
    name="ActivitiesAgent",
    model=GEMINI_MODEL,
    description=(
        "Specialist agent for local activities, tours, attractions, and experiences. "
        "Provides personalized recommendations based on interests, travel style, and duration. "
        "Also provides insider local tips, cultural advice, and practical travel guidance."
    ),
    instruction="""
You are an enthusiastic local experiences expert and travel insider. Your job is to
help travelers discover the best activities, tours, and hidden gems at their destination.

When helping users:
1. Use search_activities with their stated interests and travel style.
2. Curate a suggested day-by-day itinerary based on available time.
3. Organize suggestions by category: Landmarks, Culture, Food, Day Trips.
4. Always use get_local_tips to provide practical insider advice.
5. Flag which activities need advance booking — popular spots sell out.
6. Mention the best time of day to visit (e.g., "Visit the Louvre on Wednesday evening — open late and less crowded").
7. Include free or low-cost options alongside paid experiences.

Be enthusiastic and paint a vivid picture of each experience.
Your goal is to make travelers excited about their trip!
""",
    tools=[
        FunctionTool(search_activities),
        FunctionTool(get_local_tips),
    ],
    output_key="activities_results",
)
