#!/usr/bin/env node
/**
 * ╔══════════════════════════════════════════════════════╗
 *  TRAVEL AGENT — MCP SERVER 2: Planning Tools
 *  VS Code AI Toolkit · Agent Builder Demo
 *
 *  Add via: Agent Builder → Tools → + Add MCP Server
 *           → Command (stdio)
 *           → command: node
 *           → args:    travel-planner-mcp-server.js
 *
 *  Tools exposed:
 *    1. build_itinerary  – Day-by-day trip plan
 *    2. get_travel_tips  – Insider tips & local advice
 * ╚══════════════════════════════════════════════════════╝
 */

const readline = require("readline");

// ─────────────────────────────────────────────────────────
// MOCK DATA
// ─────────────────────────────────────────────────────────

const ITINERARIES = {
  "Paris": [
    { day: 1, theme: "Iconic Paris",    activities: ["Eiffel Tower (go early to beat crowds)", "Seine River Cruise", "Louvre Museum highlights tour", "Dinner at Le Comptoir du Relais in Saint-Germain"] },
    { day: 2, theme: "Art & Culture",   activities: ["Musee d'Orsay Impressionist collection", "Walk Saint-Germain-des-Pres", "Picasso Museum in Le Marais", "Sunset at Sacre-Coeur, Montmartre"] },
    { day: 3, theme: "Royal Escape",    activities: ["Day trip to Versailles Palace", "Stroll the Palace Gardens", "Return to Paris via RER C", "Evening walk on Champs-Elysees, Arc de Triomphe"] },
    { day: 4, theme: "Hidden Paris",    activities: ["Le Marais neighborhood and falafel", "Sainte-Chapelle stained glass", "Shakespeare & Company bookshop", "Jazz club in Saint-Germain"] },
    { day: 5, theme: "Food & Farewell", activities: ["Rue Mouffetard market breakfast", "French cooking class", "Final walk along the Seine", "CDG airport transfer"] },
  ],
  "Tokyo": [
    { day: 1, theme: "Modern Tokyo",      activities: ["Shibuya Scramble Crossing", "TeamLab Borderless digital art museum", "Harajuku Takeshita Street", "Shinjuku Golden Gai nightlife"] },
    { day: 2, theme: "Traditional Tokyo", activities: ["Senso-ji Temple Asakusa (arrive at 7am)", "Ueno Park and Tokyo National Museum", "Akihabara electronics district", "Tsukiji outer market dinner"] },
    { day: 3, theme: "Neighborhoods",     activities: ["Yanaka retro village morning walk", "Nezu Shrine tunnel path", "Omotesando luxury shopping boulevard", "Roppongi Hills art and views"] },
    { day: 4, theme: "Nikko Day Trip",    activities: ["Shinkansen to Nikko", "Tosho-gu Shrine complex", "Kegon Waterfall", "Return to Tokyo evening"] },
    { day: 5, theme: "Food & Farewell",   activities: ["Tsukiji sushi breakfast", "Odaiba waterfront and teamLab Planets", "Souvenir shopping in Asakusa", "Narita or Haneda transfer"] },
  ],
  "Rome": [
    { day: 1, theme: "Ancient Rome",      activities: ["Colosseum skip-the-line entry", "Roman Forum and Palatine Hill", "Capitoline Museums", "Trastevere neighborhood dinner"] },
    { day: 2, theme: "Vatican & Baroque", activities: ["Vatican Museums early entry", "Sistine Chapel", "St Peter's Basilica and dome climb", "Campo de' Fiori aperitivo, Piazza Navona"] },
    { day: 3, theme: "Fountains & Hills", activities: ["Trevi Fountain at 6am (before crowds)", "Spanish Steps and Piazza di Spagna", "Borghese Gallery (book ahead)", "Pincian Hill terrace sunset"] },
    { day: 4, theme: "Pompeii Day Trip",  activities: ["High-speed train to Naples", "Pompeii ruins guided tour", "Herculaneum for smaller crowds", "Pizza in Naples, evening train back"] },
    { day: 5, theme: "Slow Rome",         activities: ["Testaccio market and offal breakfast", "Aventine Hill keyhole view of St Peter's", "Aperol spritz aperitivo", "FCO airport transfer"] },
  ],
};

const TRAVEL_TIPS = {
  "Paris": {
    transport: ["Buy Navigo Decouverte weekly metro pass (22.80 EUR)", "Taxis from CDG cost 55 EUR flat rate to central Paris", "Velib bike share available across the city"],
    booking:   ["Book Eiffel Tower tickets 2-3 weeks ahead — no walk-ins", "Versailles Palace: book skip-the-line tickets online", "Many national museums free first Sunday of each month"],
    money:     ["Tipping not mandatory but 5-10% appreciated", "Most restaurants add a service charge", "Street cafes often cheaper than sit-down restaurants"],
    apps:      ["Bonjour RATP (metro routes)", "TheFork (restaurant booking)", "Paris Je t'aime (official tourist app)"],
    emergency: { police: "17", ambulance: "15", tourist_helpline: "+33 8 92 68 30 00" },
  },
  "Tokyo": {
    transport: ["Get Suica or Pasmo IC card at any JR station", "Buy JR Pass before leaving home for Shinkansen travel", "Tokyo Metro 24/48/72hr pass for unlimited subway rides"],
    booking:   ["TeamLab: book online 2 weeks ahead — always sells out", "Tsukiji sushi bars: queue early (6:30am)", "Popular ramen shops: expect 30-45 min wait at peak times"],
    money:     ["Japan is still very cash-heavy — carry Yen", "7-Eleven and Lawson ATMs accept foreign cards", "Convenience store food is excellent and cheap"],
    apps:      ["Google Translate camera mode for menus", "Japan Official Travel App", "Hyperdia for train routes"],
    emergency: { police: "110", ambulance: "119", tourist_helpline: "03-3201-3331 (Japan Visitor Hotline)" },
  },
  "Rome": {
    transport: ["Buy 48hr or 72hr Roma Pass for transport + museum discounts", "Validate transit tickets before boarding — fines are steep", "Taxis from FCO cost 50 EUR flat rate to central Rome"],
    booking:   ["Book Colosseum online — the queue without tickets is brutal", "Vatican Museums: book early morning entry to miss crowds", "Borghese Gallery: timed entry required, book weeks ahead"],
    money:     ["Avoid restaurants on the main tourist piazzas — overpriced", "Look for 'Menu del Giorno' for great lunch deals", "Tip about 10% in restaurants — not included in bill"],
    apps:      ["Moovit (Rome transit)", "TheFork (OpenTable equivalent)", "Rome2rio (getting around)"],
    emergency: { police: "112", ambulance: "118", tourist_helpline: "+39 06 0608" },
  },
};

// ─────────────────────────────────────────────────────────
// TOOL LOGIC
// ─────────────────────────────────────────────────────────

function buildItinerary({ city, days, interests, travel_style }) {
  const plan = ITINERARIES[city] || ITINERARIES["Paris"];
  const n    = Math.min(days || 5, plan.length);
  return {
    destination: city,
    duration: `${n} days`,
    style: travel_style || "Mixed sightseeing, food, and culture",
    interests: interests || "General",
    itinerary: plan.slice(0, n).map(d => ({
      day: d.day,
      theme: d.theme,
      activities: d.activities,
    })),
    budget_per_day: {
      budget:    "$80-120 USD (excl. flights and hotel)",
      mid_range: "$150-250 USD (excl. flights and hotel)",
      luxury:    "$400+ USD (excl. flights and hotel)",
    },
    pro_tips: [
      "Book major attractions 2+ weeks in advance",
      "Restaurant reservations essential for fine dining",
      "Download offline maps before you travel",
      "Keep digital and physical copies of all bookings",
    ],
  };
}

function getTravelTips({ city, category }) {
  const tips = TRAVEL_TIPS[city] || TRAVEL_TIPS["Paris"];
  if (category && tips[category]) {
    return { city, category, tips: tips[category] };
  }
  return {
    city,
    transport_tips: tips.transport,
    booking_tips:   tips.booking,
    money_tips:     tips.money,
    recommended_apps: tips.apps,
    emergency_numbers: tips.emergency,
    general_advice: [
      "Travel insurance is strongly recommended",
      "Check visa requirements 6 weeks before travel",
      "Notify your bank before departing",
      "Keep emergency cash in a separate location",
    ],
  };
}

// ─────────────────────────────────────────────────────────
// MCP TOOL SCHEMAS
// ─────────────────────────────────────────────────────────

const TOOLS = [
  {
    name: "build_itinerary",
    description: "Generate a detailed day-by-day travel itinerary for a destination with themed days, activities, dining suggestions, and budget tiers.",
    inputSchema: {
      type: "object",
      properties: {
        city:         { type: "string", description: "Destination city (e.g. Paris, Tokyo, Rome)" },
        days:         { type: "number", description: "Number of trip days (1-5)" },
        interests:    { type: "string", description: "Travel interests e.g. art, food, history, nightlife (optional)" },
        travel_style: { type: "string", enum: ["Budget", "Mid-range", "Luxury"], description: "Travel style preference (optional)" },
      },
      required: ["city", "days"],
    },
  },
  {
    name: "get_travel_tips",
    description: "Get insider tips, local advice, emergency numbers, recommended apps, and practical information for a destination city.",
    inputSchema: {
      type: "object",
      properties: {
        city:     { type: "string", description: "Destination city (e.g. Paris, Tokyo, Rome)" },
        category: { type: "string", enum: ["transport","booking","money","apps"], description: "Filter by specific tip category (optional)" },
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
        serverInfo: { name: "travel-planner-mcp", version: "1.0.0" },
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
      if      (name === "build_itinerary") result = buildItinerary(args);
      else if (name === "get_travel_tips") result = getTravelTips(args);
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
