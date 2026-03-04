// ============================================================
//  TRACK 1 — "Add Tools" in AI Toolkit Agent Builder
//  These are inline JSON function schemas pasted directly
//  into the Agent Builder "Add Tools" UI panel.
//  NO server required — the model executes these as
//  function calls resolved by the host/agent loop.
// ============================================================

// ── TOOL 1 ───────────────────────────────────────────────────
// Paste this into Agent Builder → Tools → + Add Tool
// Name: calculate_trip_budget
{
  "name": "calculate_trip_budget",
  "description": "Calculate the total estimated cost of a trip including flights, hotel, and daily expenses. Returns a detailed budget breakdown.",
  "parameters": {
    "type": "object",
    "properties": {
      "flight_cost_usd": {
        "type": "number",
        "description": "Round-trip flight cost per person in USD"
      },
      "hotel_per_night_usd": {
        "type": "number",
        "description": "Hotel cost per night in USD"
      },
      "nights": {
        "type": "number",
        "description": "Number of nights staying at the hotel"
      },
      "daily_expenses_usd": {
        "type": "number",
        "description": "Estimated daily spend on food, transport and activities in USD"
      },
      "num_travelers": {
        "type": "number",
        "description": "Number of travelers (default 1)"
      }
    },
    "required": ["flight_cost_usd", "hotel_per_night_usd", "nights", "daily_expenses_usd"]
  }
}

// ── TOOL 2 ───────────────────────────────────────────────────
// Paste this into Agent Builder → Tools → + Add Tool
// Name: check_visa_requirements
{
  "name": "check_visa_requirements",
  "description": "Check visa requirements and entry rules for a traveler going from one country to another. Returns visa type, processing time, fees, and key requirements.",
  "parameters": {
    "type": "object",
    "properties": {
      "passport_country": {
        "type": "string",
        "description": "The traveler's passport/citizenship country (e.g. 'United States', 'India', 'UK')"
      },
      "destination_country": {
        "type": "string",
        "description": "The destination country to visit (e.g. 'France', 'Japan', 'Italy')"
      },
      "trip_duration_days": {
        "type": "number",
        "description": "Intended length of stay in days"
      }
    },
    "required": ["passport_country", "destination_country"]
  }
}

// ── TOOL 3 ───────────────────────────────────────────────────
// Paste this into Agent Builder → Tools → + Add Tool
// Name: convert_currency
{
  "name": "convert_currency",
  "description": "Convert an amount from one currency to another using approximate exchange rates. Useful for budget planning and price comparisons.",
  "parameters": {
    "type": "object",
    "properties": {
      "amount": {
        "type": "number",
        "description": "The amount to convert"
      },
      "from_currency": {
        "type": "string",
        "description": "Source currency code (e.g. 'USD', 'EUR', 'GBP', 'JPY', 'INR')"
      },
      "to_currency": {
        "type": "string",
        "description": "Target currency code (e.g. 'EUR', 'JPY', 'GBP', 'USD')"
      }
    },
    "required": ["amount", "from_currency", "to_currency"]
  }
}
