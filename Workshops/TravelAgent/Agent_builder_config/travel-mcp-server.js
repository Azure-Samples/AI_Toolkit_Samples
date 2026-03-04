#!/usr/bin/env node
/**
 * ╔══════════════════════════════════════════════════════╗
 *  TRAVEL AGENT — MCP SERVER 1: Core Search Tools
 *  VS Code AI Toolkit · Agent Builder Demo
 *
 *  Add via: Agent Builder → Tools → + Add MCP Server
 *           → Command (stdio)
 *           → command: node
 *           → args:    travel-mcp-server.js
 *
 *  Tools exposed:
 *    1. search_flights  – Search flights between cities
 *    2. search_hotels   – Find hotels at a destination
 *    3. get_weather     – Weather forecast for a city
 * ╚══════════════════════════════════════════════════════╝
 */

const readline = require("readline");

// ─────────────────────────────────────────────────────────
// MOCK DATA
// ─────────────────────────────────────────────────────────

const FLIGHTS_DB = {
  "NYC-PAR": [
    { id: "AF001", airline: "Air France",    departure: "08:00", arrival: "21:30",   duration: "7h 30m",  price: 620,  stops: 0, class: "Economy"  },
    { id: "DL202", airline: "Delta",         departure: "11:15", arrival: "23:55",   duration: "8h 40m",  price: 540,  stops: 0, class: "Economy"  },
    { id: "BA310", airline: "British Air",   departure: "14:00", arrival: "07:10+1", duration: "9h 10m",  price: 480,  stops: 1, class: "Economy"  },
    { id: "AF002", airline: "Air France",    departure: "17:30", arrival: "08:00+1", duration: "8h 30m",  price: 1240, stops: 0, class: "Business" },
  ],
  "NYC-TOK": [
    { id: "NH100", airline: "ANA",           departure: "11:00", arrival: "14:30+1", duration: "13h 30m", price: 890,  stops: 0, class: "Economy"  },
    { id: "JL005", airline: "Japan Airlines",departure: "13:30", arrival: "17:00+1", duration: "13h 30m", price: 950,  stops: 0, class: "Economy"  },
    { id: "UA808", airline: "United",        departure: "09:00", arrival: "14:00+1", duration: "15h 00m", price: 760,  stops: 1, class: "Economy"  },
  ],
  "NYC-ROM": [
    { id: "AZ610", airline: "Alitalia",      departure: "10:00", arrival: "23:00",   duration: "9h 00m",  price: 580,  stops: 0, class: "Economy"  },
    { id: "LH402", airline: "Lufthansa",     departure: "16:00", arrival: "08:30+1", duration: "10h 30m", price: 510,  stops: 1, class: "Economy"  },
  ],
};

const HOTELS_DB = {
  "Paris": [
    { id: "H001", name: "Le Grand Hotel Paris",    stars: 5, ppn: 420, rating: 9.2, area: "Opera",         amenities: ["Spa","Pool","Restaurant","Gym"] },
    { id: "H002", name: "Hotel Lumiere",            stars: 4, ppn: 195, rating: 8.7, area: "Montmartre",    amenities: ["Restaurant","Bar","Concierge"] },
    { id: "H003", name: "Seine View Boutique",      stars: 4, ppn: 230, rating: 9.0, area: "Saint-Germain", amenities: ["River View","Breakfast","Bar"] },
    { id: "H004", name: "Budget Inn Paris Centre",  stars: 3, ppn: 89,  rating: 7.8, area: "Le Marais",     amenities: ["WiFi","24hr Reception"] },
  ],
  "Tokyo": [
    { id: "H010", name: "Park Hyatt Tokyo",         stars: 5, ppn: 650, rating: 9.5, area: "Shinjuku",      amenities: ["Spa","Pool","3 Restaurants","Gym"] },
    { id: "H011", name: "Cerulean Tower Tokyu",     stars: 5, ppn: 410, rating: 9.0, area: "Shibuya",       amenities: ["Spa","Restaurant","City Views"] },
    { id: "H012", name: "Shinjuku Granbell",        stars: 4, ppn: 160, rating: 8.4, area: "Shinjuku",      amenities: ["Restaurant","Bar","Modern Design"] },
    { id: "H013", name: "Tokyo Capsule Deluxe",     stars: 3, ppn: 55,  rating: 8.1, area: "Akihabara",     amenities: ["WiFi","Lounge","Lockers"] },
  ],
  "Rome": [
    { id: "H020", name: "Hotel Eden Rome",          stars: 5, ppn: 580, rating: 9.3, area: "Via Veneto",    amenities: ["Rooftop Pool","Spa","Fine Dining"] },
    { id: "H021", name: "Colosseum View Hotel",     stars: 4, ppn: 210, rating: 8.8, area: "Celio",         amenities: ["Colosseum View","Restaurant","Terrace"] },
    { id: "H022", name: "Trastevere Charme",        stars: 3, ppn: 120, rating: 8.5, area: "Trastevere",    amenities: ["Garden","Breakfast","Local Vibes"] },
  ],
};

const WEATHER_DB = {
  "Paris": { temp_c: 18, condition: "Partly Cloudy", humidity: 65, wind_kph: 12,
    forecast: ["Cloudy 17C","Showers 16C","Sunny 20C","Sunny 22C","Partly Cloudy 19C","Rainy 15C","Overcast 17C"] },
  "Tokyo": { temp_c: 24, condition: "Sunny",         humidity: 70, wind_kph: 8,
    forecast: ["Sunny 24C","Sunny 26C","Partly Cloudy 23C","Showers 20C","Rainy 18C","Overcast 21C","Sunny 25C"] },
  "Rome":  { temp_c: 28, condition: "Sunny",         humidity: 45, wind_kph: 10,
    forecast: ["Sunny 28C","Sunny 30C","Sunny 29C","Partly Cloudy 25C","Showers 22C","Sunny 27C","Sunny 31C"] },
};

// ─────────────────────────────────────────────────────────
// TOOL LOGIC
// ─────────────────────────────────────────────────────────

function searchFlights({ origin, destination, date, cabin_class }) {
  const destKey = destination.substring(0, 3).toUpperCase();
  const route   = Object.keys(FLIGHTS_DB).find(k => k.includes(destKey));
  let results   = FLIGHTS_DB[route] || FLIGHTS_DB["NYC-PAR"];
  if (cabin_class) {
    const filtered = results.filter(f => f.class.toLowerCase() === cabin_class.toLowerCase());
    if (filtered.length) results = filtered;
  }
  return {
    route: `${origin} to ${destination}`,
    date: date || "Next available",
    flights_found: results.length,
    results: results.map(f => ({
      flight_id: f.id, airline: f.airline,
      departure: f.departure, arrival: f.arrival,
      duration: f.duration,
      stops: f.stops === 0 ? "Non-stop" : `${f.stops} stop`,
      class: f.class,
      price_usd: `$${f.price}`,
    })),
    tip: "Prices are per person. Book 3+ weeks ahead for best fares.",
  };
}

function searchHotels({ city, check_in, check_out, max_price_per_night }) {
  const nights = 5;
  let hotels   = HOTELS_DB[city] || HOTELS_DB["Paris"];
  if (max_price_per_night) {
    const filtered = hotels.filter(h => h.ppn <= max_price_per_night);
    if (filtered.length) hotels = filtered;
  }
  return {
    city, check_in: check_in || "Flexible", check_out: check_out || `+${nights} nights`,
    hotels_found: hotels.length,
    results: hotels.map(h => ({
      hotel_id: h.id, name: h.name,
      stars: h.stars + " stars",
      area: h.area,
      guest_rating: `${h.rating}/10`,
      price_per_night: `$${h.ppn}`,
      estimated_total: `$${h.ppn * nights} for ${nights} nights`,
      amenities: h.amenities.join(", "),
    })),
    tip: "Free cancellation on most properties when booked 48h+ ahead.",
  };
}

function getWeather({ city, days }) {
  const w = WEATHER_DB[city] || { temp_c: 20, condition: "Unknown", humidity: 60, wind_kph: 10, forecast: [] };
  const n = Math.min(days || 5, w.forecast.length);
  return {
    city,
    current: {
      temperature: `${w.temp_c}C / ${Math.round(w.temp_c * 9/5 + 32)}F`,
      condition: w.condition,
      humidity: `${w.humidity}%`,
      wind: `${w.wind_kph} km/h`,
    },
    forecast: w.forecast.slice(0, n).map((d, i) => ({
      day: i === 0 ? "Today" : i === 1 ? "Tomorrow" : `Day ${i + 1}`,
      summary: d,
    })),
    packing_advice: w.temp_c > 25
      ? "Pack light summer clothes, sunscreen and sunglasses."
      : w.temp_c > 15
        ? "Bring a light jacket for evenings."
        : "Warm coat and waterproof shoes recommended.",
  };
}

// ─────────────────────────────────────────────────────────
// MCP TOOL SCHEMAS
// ─────────────────────────────────────────────────────────

const TOOLS = [
  {
    name: "search_flights",
    description: "Search available flights between two cities. Returns flight options with prices, schedules, and airline details.",
    inputSchema: {
      type: "object",
      properties: {
        origin:      { type: "string", description: "Origin city or IATA code (e.g. NYC, New York)" },
        destination: { type: "string", description: "Destination city or IATA code (e.g. Paris, PAR)" },
        date:        { type: "string", description: "Travel date YYYY-MM-DD (optional)" },
        cabin_class: { type: "string", enum: ["Economy","Business","First"], description: "Cabin class preference (optional)" },
      },
      required: ["origin", "destination"],
    },
  },
  {
    name: "search_hotels",
    description: "Find hotels at a destination city. Filter by budget, check-in and check-out dates.",
    inputSchema: {
      type: "object",
      properties: {
        city:                { type: "string", description: "Destination city (e.g. Paris, Tokyo, Rome)" },
        check_in:            { type: "string", description: "Check-in date YYYY-MM-DD (optional)" },
        check_out:           { type: "string", description: "Check-out date YYYY-MM-DD (optional)" },
        max_price_per_night: { type: "number", description: "Max budget per night in USD (optional)" },
      },
      required: ["city"],
    },
  },
  {
    name: "get_weather",
    description: "Get current weather and a multi-day forecast with packing advice for any destination city.",
    inputSchema: {
      type: "object",
      properties: {
        city: { type: "string", description: "City name (e.g. Paris, Tokyo, Rome)" },
        days: { type: "number", description: "Number of forecast days 1-7 (default 5)" },
      },
      required: ["city"],
    },
  },
];

// ─────────────────────────────────────────────────────────
// JSON-RPC 2.0 / MCP HANDLER
// ─────────────────────────────────────────────────────────

function handle(req) {
  if (req.method === "initialize") {
    return {
      jsonrpc: "2.0", id: req.id,
      result: {
        protocolVersion: "2024-11-05",
        serverInfo: { name: "travel-search-mcp", version: "1.0.0" },
        capabilities: { tools: {} },
      },
    };
  }
  if (req.method === "tools/list") {
    return { jsonrpc: "2.0", id: req.id, result: { tools: TOOLS } };
  }
  if (req.method === "tools/call") {
    const { name, arguments: args } = req.params;
    try {
      let result;
      if      (name === "search_flights") result = searchFlights(args);
      else if (name === "search_hotels")  result = searchHotels(args);
      else if (name === "get_weather")    result = getWeather(args);
      else throw new Error(`Unknown tool: ${name}`);
      return {
        jsonrpc: "2.0", id: req.id,
        result: { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] },
      };
    } catch (e) {
      return {
        jsonrpc: "2.0", id: req.id,
        result: { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true },
      };
    }
  }
  return { jsonrpc: "2.0", id: req.id, error: { code: -32601, message: "Method not found" } };
}

const rl = readline.createInterface({ input: process.stdin });
rl.on("line", line => {
  try {
    const res = handle(JSON.parse(line.trim()));
    process.stdout.write(JSON.stringify(res) + "\n");
  } catch (_) {}
});
