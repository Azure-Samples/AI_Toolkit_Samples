import json
import random
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
server = FastMCP("pet_planner")

@server.tool()
async def mcp_get_weather(location: str) -> str:
    """Get current weather information for a specific location.
    
    Args:
        location: The location to get the weather for (city, state or city, country)
    """
    try:
        # In a real implementation, you would use a weather API like OpenWeatherMap
        # For this demo, we'll simulate weather data
        weather_conditions = [
            {"condition": "sunny", "temp": 75, "humidity": 45, "wind": 8, "pet_friendly": True},
            {"condition": "partly cloudy", "temp": 68, "humidity": 55, "wind": 12, "pet_friendly": True},
            {"condition": "cloudy", "temp": 62, "humidity": 70, "wind": 15, "pet_friendly": True},
            {"condition": "light rain", "temp": 58, "humidity": 85, "wind": 18, "pet_friendly": False},
            {"condition": "heavy rain", "temp": 55, "humidity": 95, "wind": 25, "pet_friendly": False},
            {"condition": "snow", "temp": 32, "humidity": 80, "wind": 20, "pet_friendly": False},
        ]
        
        # Simulate getting weather data
        weather = random.choice(weather_conditions)
        pet_advisory = "Great for pets!" if weather["pet_friendly"] else "Keep pets indoors"
        
        return f"""Weather in {location}:
Temperature: {weather['temp']}F
Conditions: {weather['condition'].title()}
Wind: {weather['wind']} mph
Humidity: {weather['humidity']}%
Pet Advisory: {pet_advisory}"""
    except Exception as e:
        return f"Sorry, I couldn't get weather information for {location}. Please try again."

@server.tool()
async def mcp_get_pet_activities(
    weather_condition: str, 
    pet_type: str = "dog", 
    activity_duration: str = "medium"
) -> str:
    """Get activity recommendations based on weather and pet type.
    
    Args:
        weather_condition: Current weather condition (sunny, cloudy, rainy, etc.)
        pet_type: Type of pet (dog, cat, bird, etc.)
        activity_duration: Desired activity duration (short, medium, long)
    """
    activity_database = {
        "sunny": {
            "dog": {
                "short": ["Fetch in the yard", "Quick walk around the block", "Backyard agility course"],
                "medium": ["Dog park visit", "Hiking trail", "Beach walk", "Frisbee in the park"],
                "long": ["Long hike", "Dog beach day", "Camping trip", "Outdoor training session"]
            },
            "cat": {
                "short": ["Supervised patio time", "Window bird watching", "Balcony exploration"],
                "medium": ["Harness walk in garden", "Outdoor cat enclosure time", "Supervised yard exploration"],
                "long": ["Extended outdoor enclosure time", "Adventure cat hiking (if trained)"]
            }
        },
        "cloudy": {
            "dog": {
                "short": ["Indoor fetch", "Puzzle toys", "Basic training"],
                "medium": ["Covered dog park", "Indoor agility", "Mall walk (pet-friendly)"],
                "long": ["Indoor dog training class", "Dog daycare", "Pet store adventure"]
            },
            "cat": {
                "short": ["Interactive toy play", "Treat puzzles", "Laser pointer games"],
                "medium": ["Cat cafe visit", "Indoor climbing structures", "Hide and seek games"],
                "long": ["Extended play session", "Cat furniture exploration", "Indoor hunting games"]
            }
        },
        "rainy": {
            "dog": {
                "short": ["Indoor tricks training", "Kong toy stuffing", "Gentle indoor play"],
                "medium": ["Dog-friendly indoor mall", "Pet store visit", "Indoor dog gym"],
                "long": ["Dog training class", "Dog spa day", "Extended indoor play session"]
            },
            "cat": {
                "short": ["Feather wand play", "Treat dispensing toys", "Cozy nap time"],
                "medium": ["Interactive puzzle feeders", "Cat TV watching", "Indoor obstacle course"],
                "long": ["Extended indoor play", "Cat grooming session", "Multi-level cat tree exploration"]
            }
        }
    }
    
    # Normalize inputs
    weather_key = "sunny" if "sun" in weather_condition.lower() else \
                  "rainy" if "rain" in weather_condition.lower() or "storm" in weather_condition.lower() else \
                  "cloudy"
    
    pet_key = pet_type.lower() if pet_type.lower() in activity_database[weather_key] else "dog"
    duration_key = activity_duration.lower() if activity_duration.lower() in ["short", "medium", "long"] else "medium"
    
    activities = activity_database[weather_key][pet_key][duration_key]
    selected_activities = random.sample(activities, min(3, len(activities)))
    
    return f"""Activity Recommendations for your {pet_type} ({duration_key} duration):

Weather: {weather_condition.title()}
Perfect activities:
{chr(10).join([f"• {activity}" for activity in selected_activities])}

Pro Tip: Always bring water and check your pet's paws after outdoor activities!"""

@server.tool()
async def mcp_find_pet_friendly_locations(
    location: str, 
    activity_type: str = "park", 
    distance_miles: int = 5
) -> str:
    """Find pet-friendly locations near the specified area.
    
    Args:
        location: The city or area to search for pet-friendly locations
        activity_type: Type of location (park, restaurant, store, beach, etc.)
        distance_miles: Search radius in miles
    """
    # Simulate location database
    location_database = {
        "park": [
            {"name": "Sunset Dog Park", "rating": 4.8, "features": ["Off-leash area", "Water fountains", "Agility equipment"], "distance": 1.2},
            {"name": "Riverside Trail Park", "rating": 4.6, "features": ["Walking trails", "Pet waste stations", "Shaded areas"], "distance": 2.3},
            {"name": "Central City Park", "rating": 4.4, "features": ["Large open space", "Pet-friendly events", "Parking available"], "distance": 3.1},
            {"name": "Meadowbrook Off-Leash Park", "rating": 4.9, "features": ["Separate small/large dog areas", "Swimming pond", "Training area"], "distance": 4.2}
        ],
        "restaurant": [
            {"name": "The Patio Cafe", "rating": 4.7, "features": ["Outdoor seating", "Pet menu available", "Water bowls"], "distance": 0.8},
            {"name": "Bark & Bistro", "rating": 4.5, "features": ["Dog-friendly patio", "Special pet treats", "Pet washing station"], "distance": 1.5},
            {"name": "Sunny Side Grill", "rating": 4.3, "features": ["Pet-friendly deck", "Shade umbrellas", "Treats for pets"], "distance": 2.7},
            {"name": "Garden View Restaurant", "rating": 4.6, "features": ["Large patio", "Pet water stations", "Weekend pet events"], "distance": 3.4}
        ],
        "store": [
            {"name": "Pet Paradise Superstore", "rating": 4.8, "features": ["Wide aisles", "Pet grooming", "Training supplies"], "distance": 1.1},
            {"name": "Furry Friends Boutique", "rating": 4.6, "features": ["Designer pet gear", "Custom accessories", "Photo sessions"], "distance": 1.9},
            {"name": "Healthy Paws Pet Store", "rating": 4.7, "features": ["Natural foods", "Holistic treatments", "Expert advice"], "distance": 2.8},
            {"name": "Adventure Pet Gear", "rating": 4.5, "features": ["Outdoor equipment", "Travel accessories", "Expert fitting"], "distance": 3.6}
        ],
        "beach": [
            {"name": "Sandy Paws Beach", "rating": 4.9, "features": ["Off-leash hours", "Fresh water rinse", "Waste bag stations"], "distance": 4.8},
            {"name": "Coastal Dog Beach", "rating": 4.7, "features": ["Large off-leash area", "Lifeguard on duty", "Pet-friendly parking"], "distance": 6.2},
            {"name": "Sunset Cove (Pet Section)", "rating": 4.4, "features": ["Designated pet area", "Tide pools", "Beach toys rental"], "distance": 7.1}
        ]
    }
    
    # Get locations for the requested type
    available_locations = location_database.get(activity_type.lower(), location_database["park"])
    
    # Filter by distance and sort by rating
    filtered_locations = [loc for loc in available_locations if loc["distance"] <= distance_miles]
    filtered_locations.sort(key=lambda x: x["rating"], reverse=True)
    
    if not filtered_locations:
        return f"Sorry, I couldn't find any pet-friendly {activity_type}s within {distance_miles} miles of {location}. Try expanding your search radius!"
    
    result = f"""Top Pet-Friendly {activity_type.title()}s near {location}:

"""
    
    for i, loc in enumerate(filtered_locations[:3], 1):
        result += f"""#{i} {loc['name']} - Rating: {loc['rating']}/5
Distance: {loc['distance']} miles away
Features: {', '.join(loc['features'])}

"""
    
    result += "Pro Tip: Call ahead to confirm current pet policies and hours!"
    
    return result

@server.tool()
async def mcp_get_pet_care_tips(
    weather_condition: str, 
    pet_type: str = "dog"
) -> str:
    """Get weather-specific pet care tips and safety advice.
    
    Args:
        weather_condition: Current weather condition
        pet_type: Type of pet
    """
    tips_database = {
        "sunny": {
            "dog": [
                "Provide plenty of fresh water and shade",
                "Walk during cooler hours (early morning/evening)",
                "Check pavement temperature with your hand - if it's too hot for you, it's too hot for paws",
                "Consider booties for hot pavement protection",
                "Watch for signs of overheating: excessive panting, drooling, lethargy"
            ],
            "cat": [
                "Ensure access to cool, shaded areas",
                "Provide multiple water sources",
                "Keep indoor cats away from direct sunlight through windows",
                "Consider cooling mats for comfort",
                "Monitor for heat stress signs"
            ]
        },
        "rainy": {
            "dog": [
                "Use waterproof gear if going outside",
                "Dry thoroughly after being outside to prevent skin issues",
                "Provide mental stimulation with indoor activities",
                "Check and clean paws after walks",
                "Keep a towel by the door for quick cleanups"
            ],
            "cat": [
                "Keep cats indoors during heavy rain",
                "Provide cozy, dry spots for comfort",
                "Increase indoor play to compensate for reduced outdoor time",
                "Monitor humidity levels in the home",
                "Ensure litter boxes are in dry areas"
            ]
        },
        "cold": {
            "dog": [
                "Consider warm clothing for short-haired breeds",
                "Limit time outside for small or elderly dogs",
                "Protect paws from ice and salt with booties",
                "Provide warm, dry bedding",
                "Increase caloric intake if spending time outdoors"
            ],
            "cat": [
                "Provide warm sleeping areas away from drafts",
                "Keep indoor cats comfortable with adequate heating",
                "Check outdoor cats for frostbite signs",
                "Provide extra blankets and warm bedding",
                "Monitor for signs of cold stress"
            ]
        }
    }
    
    # Determine weather category
    weather_key = "sunny" if any(word in weather_condition.lower() for word in ["sun", "hot", "warm"]) else \
                  "rainy" if any(word in weather_condition.lower() for word in ["rain", "storm", "wet"]) else \
                  "cold"
    
    pet_key = pet_type.lower() if pet_type.lower() in tips_database[weather_key] else "dog"
    
    tips = tips_database[weather_key][pet_key]
    
    return f"""Weather Safety Tips for your {pet_type.title()}:

Current conditions: {weather_condition.title()}

{chr(10).join([f"• {tip}" for tip in tips])}

Always consult your veterinarian if you notice any concerning symptoms!"""

if __name__ == "__main__":
    print("Pet Planner MCP Server starting...")
    print("Available tools: mcp_get_weather, mcp_get_pet_activities, mcp_find_pet_friendly_locations, mcp_get_pet_care_tips")
    print("Server ready for connections...")
    server.run()