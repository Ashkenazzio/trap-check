"""
Mock data for development and testing without SerpAPI.
Contains realistic sample data for known tourist traps, local gems, and edge cases.

Test Venue Selection Rationale:
- Da Michele (Naples): Clear authentic - locals love it, cheap, historic
- Olive Garden Times Square: Clear trap - chain in tourist hotspot
- Carlo Menta (Rome): Mixed/edge case - divisive "volume trap" model
- Katz's Deli (NYC): Edge case - famous, expensive, but quality justifies
"""

MOCK_PLACES = {
    "pizzeria da michele": {
        "data_id": "mock_da_michele_001",
        "place_id": "ChIJMock123",
        "name": "L'Antica Pizzeria Da Michele",
        "address": "Via Cesare Sersale, 1, 80139 Napoli NA, Italy",
        "rating": 4.4,
        "review_count": 28547,
        "price_level": "$",
        "type": "Pizza restaurant",
        "types": ["pizza_restaurant", "restaurant"],
        "gps_coordinates": {"lat": 40.8498, "lng": 14.2654},
        "google_maps_url": "https://maps.google.com/?cid=mock_da_michele",
        "thumbnail": None,
    },
    "olive garden times square": {
        "data_id": "mock_olive_garden_001",
        "place_id": "ChIJMock456",
        "name": "Olive Garden Italian Restaurant",
        "address": "2 Times Square, New York, NY 10036",
        "rating": 3.8,
        "review_count": 12453,
        "price_level": "$$",
        "type": "Italian restaurant",
        "types": ["italian_restaurant", "restaurant"],
        "gps_coordinates": {"lat": 40.7580, "lng": -73.9855},
        "google_maps_url": "https://maps.google.com/?cid=mock_olive_garden",
        "thumbnail": None,
    },
    "carlo menta": {
        "data_id": "mock_carlo_menta_001",
        "place_id": "ChIJMock789",
        "name": "Ristorante Carlo Menta",
        "address": "Via della Lungaretta, 101, 00153 Roma RM, Italy",
        "rating": 4.0,
        "review_count": 6234,
        "price_level": "$",
        "type": "Italian restaurant",
        "types": ["italian_restaurant", "restaurant", "pizza_restaurant"],
        "gps_coordinates": {"lat": 41.8879, "lng": 12.4699},
        "google_maps_url": "https://maps.google.com/?cid=mock_carlo_menta",
        "thumbnail": None,
    },
    "katz's delicatessen": {
        "data_id": "mock_katz_001",
        "place_id": "ChIJMockABC",
        "name": "Katz's Delicatessen",
        "address": "205 E Houston St, New York, NY 10002",
        "rating": 4.5,
        "review_count": 19234,
        "price_level": "$$",
        "type": "Deli",
        "types": ["deli", "restaurant", "sandwich_shop"],
        "gps_coordinates": {"lat": 40.7223, "lng": -73.9874},
        "google_maps_url": "https://maps.google.com/?cid=mock_katz",
        "thumbnail": None,
    },
}

MOCK_REVIEWS = {
    "mock_da_michele_001": {
        "place_info": {
            "title": "L'Antica Pizzeria Da Michele",
            "address": "Via Cesare Sersale, 1, 80139 Napoli NA, Italy",
            "rating": 4.4,
            "reviews": 28547,
        },
        "reviews": [
            {
                "text": "Absolutely authentic Neapolitan pizza. The margherita is simple perfection - just tomato, mozzarella, basil, and that incredible charred crust. Yes there's a queue but it moves fast. Locals and tourists alike, everyone agrees this is the real deal. Been coming here for 20 years.",
                "rating": 5,
                "date": "2 weeks ago",
                "iso_date": "2024-11-28",
                "user": {"name": "Giuseppe M.", "local_guide": True, "reviews_count": 234},
                "likes": 45,
                "response": None,
            },
            {
                "text": "Waited 45 minutes in line but worth every second. Only two pizzas on the menu - marinara and margherita - and they've been perfecting them since 1870. The dough is incredibly light. Don't expect fancy service or decor, you're here for the pizza.",
                "rating": 5,
                "date": "1 month ago",
                "iso_date": "2024-11-15",
                "user": {"name": "Sarah T.", "local_guide": False, "reviews_count": 12},
                "likes": 23,
                "response": None,
            },
            {
                "text": "Overhyped tourist attraction. Yes it was in Eat Pray Love but that doesn't make it good. The pizza was fine but nothing special. Way too crowded and chaotic. There are better pizzerias in Naples without the ridiculous wait.",
                "rating": 2,
                "date": "3 weeks ago",
                "iso_date": "2024-11-21",
                "user": {"name": "Mike R.", "local_guide": False, "reviews_count": 8},
                "likes": 12,
                "response": None,
            },
            {
                "text": "As a Neapolitan, I can confirm this is where we take our relatives when they visit. It's not a tourist trap - it's genuinely historic and the pizza is exceptional. The prices are incredibly fair for the quality. Just go early or late to avoid the queue.",
                "rating": 5,
                "date": "1 week ago",
                "iso_date": "2024-12-05",
                "user": {"name": "Marco B.", "local_guide": True, "reviews_count": 567},
                "likes": 89,
                "response": None,
            },
            {
                "text": "I don't understand the hype. It's just pizza? The place is cramped and loud. Service is rushed - they want you in and out. For €5 it's cheap but the experience is not enjoyable if you want to actually sit and relax.",
                "rating": 3,
                "date": "2 months ago",
                "iso_date": "2024-10-10",
                "user": {"name": "Jennifer L.", "local_guide": False, "reviews_count": 3},
                "likes": 5,
                "response": None,
            },
            {
                "text": "This is the pizza that all other pizzas aspire to be. Simple, perfect, life-changing. The marinara without cheese is somehow the best pizza I've ever had. Worth the trip to Naples alone.",
                "rating": 5,
                "date": "3 weeks ago",
                "iso_date": "2024-11-21",
                "user": {"name": "David K.", "local_guide": True, "reviews_count": 189},
                "likes": 34,
                "response": None,
            },
            {
                "text": "Came here based on all the reviews. It's good pizza, very good even, but is it worth an hour wait? Probably not. The atmosphere is hectic and you feel rushed. I prefer Sorbillo down the street.",
                "rating": 3,
                "date": "1 month ago",
                "iso_date": "2024-11-15",
                "user": {"name": "Anna P.", "local_guide": False, "reviews_count": 45},
                "likes": 8,
                "response": None,
            },
            {
                "text": "My family has been coming here for three generations. This is not a tourist trap - it's a Naples institution. The fact that tourists discovered it doesn't change the quality. Best pizza in the world, no question.",
                "rating": 5,
                "date": "2 weeks ago",
                "iso_date": "2024-11-28",
                "user": {"name": "Francesco D.", "local_guide": True, "reviews_count": 312},
                "likes": 67,
                "response": None,
            },
            # Italian language reviews (for language diversity testing)
            {
                "text": "La vera pizza napoletana come si faceva una volta. Mia nonna mi portava qui da bambino e il sapore è sempre lo stesso. Impasto leggero, pomodoro San Marzano, mozzarella di bufala freschissima. Non c'è paragone con le altre pizzerie.",
                "rating": 5,
                "date": "1 week ago",
                "iso_date": "2024-12-05",
                "user": {"name": "Antonio R.", "local_guide": True, "reviews_count": 423},
                "likes": 156,
                "response": None,
            },
            {
                "text": "Siamo napoletani e questa è la nostra pizzeria da sempre. I turisti hanno scoperto questo posto ma la qualità non è cambiata. Venite presto la mattina per evitare la coda. La margherita è poesia.",
                "rating": 5,
                "date": "2 weeks ago",
                "iso_date": "2024-11-28",
                "user": {"name": "Lucia F.", "local_guide": True, "reviews_count": 287},
                "likes": 98,
                "response": None,
            },
            {
                "text": "Troppa fila ultimamente, ma la pizza resta eccezionale. Il cornicione è perfetto - alto, morbido dentro, croccante fuori. Solo due pizze nel menu perché non serve altro quando le fai così bene.",
                "rating": 4,
                "date": "3 weeks ago",
                "iso_date": "2024-11-21",
                "user": {"name": "Salvatore M.", "local_guide": False, "reviews_count": 67},
                "likes": 45,
                "response": None,
            },
        ],
        "topics": [
            {"keyword": "pizza", "mentions": 892},
            {"keyword": "queue", "mentions": 234},
            {"keyword": "margherita", "mentions": 567},
            {"keyword": "authentic", "mentions": 189},
            {"keyword": "wait", "mentions": 345},
            {"keyword": "Naples", "mentions": 123},
        ],
    },
    "mock_olive_garden_001": {
        "place_info": {
            "title": "Olive Garden Italian Restaurant",
            "address": "2 Times Square, New York, NY 10036",
            "rating": 3.8,
            "reviews": 12453,
        },
        "reviews": [
            {
                "text": "Classic tourist trap in the middle of Times Square. Overpriced mediocre chain food that you can get anywhere in America. $25 for pasta that tastes like it came from a microwave. The breadsticks are the only redeeming quality.",
                "rating": 2,
                "date": "1 week ago",
                "user": {"name": "NYC Local", "local_guide": True, "reviews_count": 456},
                "likes": 234,
                "response": None,
            },
            {
                "text": "Why would you come to New York City to eat at Olive Garden?? There are thousands of amazing Italian restaurants here. This is the definition of a tourist trap - same food as your suburban mall but 3x the price.",
                "rating": 1,
                "date": "2 weeks ago",
                "user": {"name": "Manhattan Mike", "local_guide": True, "reviews_count": 892},
                "likes": 567,
                "response": None,
            },
            {
                "text": "We were tired from walking around Times Square and just wanted something familiar. Yes it's a chain but the food was fine and the AC was nice. Not everything needs to be a culinary adventure.",
                "rating": 4,
                "date": "3 weeks ago",
                "user": {"name": "Karen S.", "local_guide": False, "reviews_count": 12},
                "likes": 8,
                "response": None,
            },
            {
                "text": "Absolutely ridiculous prices for Olive Garden food. $30 for chicken parm that costs $15 in New Jersey. You're paying for the Times Square location, not the food. Complete rip-off.",
                "rating": 1,
                "date": "1 month ago",
                "user": {"name": "Budget Traveler", "local_guide": False, "reviews_count": 34},
                "likes": 123,
                "response": None,
            },
            {
                "text": "Waited 45 minutes to be seated, then another 30 for food. Staff seemed overwhelmed and uninterested. The pasta was cold. Never again - there are SO many better options within walking distance.",
                "rating": 1,
                "date": "2 weeks ago",
                "user": {"name": "Disappointed Dan", "local_guide": False, "reviews_count": 67},
                "likes": 89,
                "response": "We apologize for your experience and hope you'll give us another chance.",
            },
            {
                "text": "Look, I know it's not authentic Italian, but my kids are picky eaters and they loved it. Sometimes you just need predictable food when traveling. The unlimited breadsticks kept everyone happy.",
                "rating": 3,
                "date": "1 month ago",
                "user": {"name": "Mom of 3", "local_guide": False, "reviews_count": 5},
                "likes": 12,
                "response": None,
            },
            {
                "text": "As someone who lives in NYC, I would NEVER eat here. This is where tourists go because they recognize the name. You're in one of the best food cities in the world - explore! Don't waste a meal here.",
                "rating": 1,
                "date": "3 weeks ago",
                "user": {"name": "Foodie Frank", "local_guide": True, "reviews_count": 1234},
                "likes": 456,
                "response": None,
            },
            {
                "text": "Tourist trap 101. Mediocre food, inflated prices, terrible service. The only people here are out-of-towners who don't know better. Please, do yourself a favor and walk 5 blocks in any direction for real food.",
                "rating": 1,
                "date": "1 week ago",
                "user": {"name": "Real NYer", "local_guide": True, "reviews_count": 678},
                "likes": 345,
                "response": None,
            },
        ],
        "topics": [
            {"keyword": "tourist trap", "mentions": 234},
            {"keyword": "overpriced", "mentions": 456},
            {"keyword": "Times Square", "mentions": 567},
            {"keyword": "breadsticks", "mentions": 123},
            {"keyword": "chain", "mentions": 189},
            {"keyword": "wait", "mentions": 234},
        ],
    },
    "mock_carlo_menta_001": {
        "place_info": {
            "title": "Ristorante Carlo Menta",
            "address": "Via della Lungaretta, 101, 00153 Roma RM, Italy",
            "rating": 4.0,
            "reviews": 6234,
        },
        "reviews": [
            # Positive reviews - budget travelers love it
            {
                "text": "Best value in Trastevere! €10 tourist menu with pasta, pizza, wine, AND dessert. Yes it's basic but you're in Rome eating for nothing. Perfect for backpackers. We came back twice.",
                "rating": 5,
                "date": "1 week ago",
                "user": {"name": "Budget Backpacker", "local_guide": False, "reviews_count": 34},
                "likes": 67,
                "response": None,
            },
            {
                "text": "Everyone complaining about quality is missing the point. It's €5 pasta in one of the most expensive tourist areas of Rome. What do you expect, Michelin stars? For the price, it's incredible.",
                "rating": 4,
                "date": "2 weeks ago",
                "user": {"name": "Realistic Traveler", "local_guide": False, "reviews_count": 89},
                "likes": 45,
                "response": None,
            },
            {
                "text": "Honestly shocked by the negative reviews. We had great cacio e pepe for €6 and the staff were friendly. Maybe people came with wrong expectations? It's cheap Roman food, not fine dining.",
                "rating": 5,
                "date": "3 weeks ago",
                "user": {"name": "Happy Tourist", "local_guide": False, "reviews_count": 12},
                "likes": 23,
                "response": None,
            },
            # Negative reviews - quality concerns
            {
                "text": "Classic tourist trap operating on volume. The lasagna was a travesty - basically 10 sheets of pasta glued together with barely any sauce. You get what you pay for, and this is why Romans avoid Trastevere.",
                "rating": 2,
                "date": "2 weeks ago",
                "user": {"name": "Roman Foodie", "local_guide": True, "reviews_count": 456},
                "likes": 189,
                "response": None,
            },
            {
                "text": "Tourist trap 101. Yes it's cheap but the food is mass-produced garbage. The carbonara was clearly made with cream (a crime!) and the pasta was overcooked mush. Walk 10 minutes away from Trastevere for real food.",
                "rating": 1,
                "date": "1 week ago",
                "user": {"name": "Italian Food Purist", "local_guide": True, "reviews_count": 234},
                "likes": 156,
                "response": None,
            },
            {
                "text": "Chaotic doesn't begin to describe it. My partner was bumped by servers THREE times. The €10 menu is a trap - the portions are tiny and the quality is cafeteria-level. Avoid unless you're truly broke.",
                "rating": 2,
                "date": "3 weeks ago",
                "user": {"name": "Disappointed Diner", "local_guide": True, "reviews_count": 178},
                "likes": 98,
                "response": None,
            },
            {
                "text": "As a local, I would NEVER eat here. This is where tourists go because they see the cheap prices without understanding they're getting frozen, reheated food. The pizzas come from a central kitchen. Sad.",
                "rating": 1,
                "date": "1 month ago",
                "user": {"name": "Trastevere Local", "local_guide": True, "reviews_count": 567},
                "likes": 234,
                "response": None,
            },
            # Mixed/nuanced reviews
            {
                "text": "It's complicated. The prices are genuinely amazing (€3 pizza!) and some dishes are fine. But others are clearly pre-made. Know what you're getting into: cheap fuel, not a culinary experience. I don't regret it but wouldn't return.",
                "rating": 3,
                "date": "2 weeks ago",
                "user": {"name": "Honest Reviewer", "local_guide": False, "reviews_count": 123},
                "likes": 78,
                "response": None,
            },
        ],
        "topics": [
            {"keyword": "cheap", "mentions": 456},
            {"keyword": "tourist menu", "mentions": 234},
            {"keyword": "value", "mentions": 189},
            {"keyword": "quality", "mentions": 312},
            {"keyword": "tourist trap", "mentions": 145},
            {"keyword": "Trastevere", "mentions": 267},
        ],
    },
    "mock_katz_001": {
        "place_info": {
            "title": "Katz's Delicatessen",
            "address": "205 E Houston St, New York, NY 10002",
            "rating": 4.5,
            "reviews": 19234,
        },
        "reviews": [
            # Positive reviews - quality defenders
            {
                "text": "Yes it's famous from When Harry Met Sally. Yes there's usually a line. But this is NOT a tourist trap - the pastrami is genuinely the best in the world. I'm a born-and-raised New Yorker and I still come here regularly. Worth every penny.",
                "rating": 5,
                "date": "1 week ago",
                "user": {"name": "LES Local", "local_guide": True, "reviews_count": 567},
                "likes": 234,
                "response": None,
            },
            {
                "text": "As a Jewish New Yorker, I can confirm this is the gold standard for deli. My family has been coming here for four generations. It's famous because it's genuinely excellent, not the other way around.",
                "rating": 5,
                "date": "2 weeks ago",
                "user": {"name": "NYC Native", "local_guide": True, "reviews_count": 234},
                "likes": 123,
                "response": None,
            },
            {
                "text": "Finally tried the famous Katz's. $28 for a sandwich seemed crazy but WOW. Hand-carved pastrami piled high, perfect rye bread, spicy mustard. I get it now. This is the real deal.",
                "rating": 5,
                "date": "3 weeks ago",
                "user": {"name": "First Timer", "local_guide": False, "reviews_count": 23},
                "likes": 67,
                "response": None,
            },
            # Critical reviews - price and chaos concerns
            {
                "text": "Classic NYC tourist trap disguised as an institution. $28 for a sandwich?! The pastrami is good but not THAT good. The chaos, the rude staff yelling at you, the confusing ticket system - it's an experience designed to extract maximum dollars from tourists.",
                "rating": 2,
                "date": "1 week ago",
                "user": {"name": "Price Conscious", "local_guide": True, "reviews_count": 345},
                "likes": 156,
                "response": None,
            },
            {
                "text": "Massively overrated and overpriced. The pastrami was decent but I've had better in Brooklyn for half the price. The whole place feels like a tourist attraction now, not a neighborhood deli. Most locals I know avoid it.",
                "rating": 2,
                "date": "2 weeks ago",
                "user": {"name": "Brooklyn Foodie", "local_guide": True, "reviews_count": 456},
                "likes": 189,
                "response": None,
            },
            {
                "text": "Lost my ticket and they charged me $50!!! The food was fine but this place runs on tourist money now. The whole 'don't lose your ticket' thing feels like a scam. Stressful experience, won't return.",
                "rating": 1,
                "date": "3 weeks ago",
                "user": {"name": "Frustrated Visitor", "local_guide": False, "reviews_count": 89},
                "likes": 234,
                "response": None,
            },
            # Mixed/nuanced reviews
            {
                "text": "Honestly overrated. It's good pastrami but $28 good? Not sure. The place is chaotic and loud. Carnegie Deli was better before it closed. Still, if you've never had it, it's worth trying once.",
                "rating": 3,
                "date": "1 month ago",
                "user": {"name": "Skeptical Sam", "local_guide": True, "reviews_count": 456},
                "likes": 34,
                "response": None,
            },
            {
                "text": "It's complicated. The pastrami IS exceptional - probably the best I've had. But $28 is insane, the lines are brutal, and the vibe is pure tourist chaos. Come once for the experience, then find a local spot.",
                "rating": 3,
                "date": "2 weeks ago",
                "user": {"name": "Honest Review", "local_guide": False, "reviews_count": 123},
                "likes": 78,
                "response": None,
            },
        ],
        "topics": [
            {"keyword": "pastrami", "mentions": 678},
            {"keyword": "expensive", "mentions": 423},
            {"keyword": "overpriced", "mentions": 234},
            {"keyword": "tourist", "mentions": 312},
            {"keyword": "famous", "mentions": 234},
            {"keyword": "worth it", "mentions": 189},
            {"keyword": "line", "mentions": 156},
            {"keyword": "ticket", "mentions": 123},
        ],
    },
}


def get_mock_place(query: str) -> dict | None:
    """Find a mock place by query (fuzzy match on name)."""
    query_lower = query.lower()
    query_words = set(query_lower.split())

    for key, place in MOCK_PLACES.items():
        key_words = set(key.split())
        name_lower = place["name"].lower()

        # Check if any query word matches key words
        if query_words & key_words:
            return place

        # Check if any query word is in the place name
        if any(word in name_lower for word in query_words):
            return place

        # Check if query is substring of key or vice versa
        if key in query_lower or query_lower in key:
            return place

    return None


def get_mock_reviews(data_id: str) -> dict | None:
    """Get mock reviews for a data_id."""
    return MOCK_REVIEWS.get(data_id)
