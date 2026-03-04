"""
╔══════════════════════════════════════════════════════════════════╗
  Voyager — AI Travel Agent  |  FastAPI + Microsoft Agent Framework
  
  Tools:
    Track 1 — Custom Inline Tools (kernel_function):
      • calculate_trip_budget
      • check_visa_requirements
      • convert_currency

    Track 2 — MCP Server Tools (MCPStdioTool):
      • search_flights        (travel-mcp-server.js)
      • search_hotels         (travel-mcp-server.js)
      • get_weather           (travel-mcp-server.js)
      • build_itinerary       (travel-planner-mcp-server.js)
      • get_travel_tips       (travel-planner-mcp-server.js)

  Setup:
    pip install anthropic agent-framework==1.0.0b260107 fastapi uvicorn pydantic

  Run:
    uvicorn travel_agent:app --host 0.0.0.0 --port 8000 --reload

  Endpoints:
    POST /chat          — single-turn chat
    POST /chat/stream   — streaming chat (SSE)
    GET  /health        — health check
    GET  /tools         — list all registered tools
╚══════════════════════════════════════════════════════════════════╝
"""

import asyncio
import json
import os
import traceback
from typing import AsyncGenerator, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from agent_framework import (
    FunctionCallContent,
    MCPStdioTool,
    ToolProtocol,
)
from agent_framework.openai import OpenAIChatClient
from openai import AsyncOpenAI

# ──────────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────────

# ── MCP Server paths — update these to match your local setup ──
MCP_SEARCH_SERVER_PATH  = os.environ.get(
    "MCP_SEARCH_PATH",
    r"C:\Users\shrey\Downloads\v2\travel-mcp-server.js"
)
MCP_PLANNER_SERVER_PATH = os.environ.get(
    "MCP_PLANNER_PATH",
    r"C:\Users\shrey\Downloads\v2\travel-planner-mcp-server.js"
)

# ── OpenAI / GitHub Models client ──
openai_client = AsyncOpenAI(
    base_url="https://models.github.ai/inference",
    api_key=os.environ["GITHUB_TOKEN"],
    default_query={"api-version": "2024-08-01-preview"},
)

MODEL_ID = "openai/gpt-4.1"

# ──────────────────────────────────────────────────────────────────
# AGENT SYSTEM PROMPT
# ──────────────────────────────────────────────────────────────────

AGENT_INSTRUCTIONS = (
    "Act as Voyager, an expert AI travel agent. Provide warm, enthusiastic, and professional "
    "assistance for global trip planning, demonstrating both inline and MCP server tool use.\n\n"
    "Inject specific, actionable recommendations for flights, hotels, weather, itinerary, budget, "
    "visa, currency conversion, and insider tips. Proactively anticipate traveler needs. Always use "
    "structured formatting and highlight local tips and cultural insights.\n\n"
    "# Tool Use Guidelines\n\n"
    "## INLINE TOOLS (Track 1 — no server required)\n"
    "- **calculate_trip_budget** — call automatically after gathering flight + hotel prices\n"
    "- **check_visa_requirements** — call when user mentions passport or nationality\n"
    "- **convert_currency** — call when user mentions a non-USD budget or asks for conversion\n\n"
    "## MCP SERVER TOOLS (Track 2 — live server calls)\n"
    "- **search_flights** — find flights between cities\n"
    "- **search_hotels** — find hotels at destination\n"
    "- **get_weather** — get forecast for destination\n"
    "- **build_itinerary** — generate day-by-day trip plan\n"
    "- **get_travel_tips** — get insider tips and local advice\n\n"
    "# Workflow\n"
    "1. Destination mentioned → call get_weather\n"
    "2. Trip planning → search_flights + search_hotels + build_itinerary + get_travel_tips\n"
    "3. After prices → calculate_trip_budget automatically\n"
    "4. Passport/nationality mentioned → check_visa_requirements\n"
    "5. Non-USD budget → convert_currency\n"
    "6. Always end with get_travel_tips\n\n"
    "# Output Format\n"
    "Respond in structured markdown with headings, bullet points, and tables where helpful. "
    "Begin with brief reasoning, end with conclusions. Keep responses 300–600 words."
)

# ──────────────────────────────────────────────────────────────────
# TRACK 1 — INLINE CUSTOM TOOLS
# These are Python functions decorated with @kernel_function.
# The agent framework converts them into tool schemas automatically
# and the model calls them directly — no MCP server needed.
# ──────────────────────────────────────────────────────────────────

try:
    from agent_framework import kernel_function
    KERNEL_FUNCTION_AVAILABLE = True
except ImportError:
    # Fallback: define a no-op decorator so the file still loads
    # and we can surface a clear error at runtime
    def kernel_function(func=None, *, name=None, description=None):
        if func is None:
            def decorator(f):
                f._kernel_function = True
                f._kf_name = name
                f._kf_description = description
                return f
            return decorator
        func._kernel_function = True
        return func
    KERNEL_FUNCTION_AVAILABLE = False

print(f"[INFO] kernel_function available: {KERNEL_FUNCTION_AVAILABLE}")


class TravelInlineTools:
    """
    Track 1 — Custom Inline Tools
    Registered as a plugin (class with @kernel_function methods).
    The agent framework introspects these and exposes them as callable
    tools alongside the MCP server tools.
    """

    # ── EXCHANGE RATES (approximate, for demo) ──
    RATES = {
        ("USD", "EUR"): 0.92, ("USD", "GBP"): 0.79, ("USD", "JPY"): 150.0,
        ("USD", "INR"): 83.0, ("USD", "AUD"): 1.53, ("USD", "CAD"): 1.36,
        ("USD", "CHF"): 0.89, ("USD", "SGD"): 1.34, ("USD", "AED"): 3.67,
        ("EUR", "USD"): 1.09, ("GBP", "USD"): 1.27, ("JPY", "USD"): 0.0067,
        ("INR", "USD"): 0.012, ("AUD", "USD"): 0.65, ("CAD", "USD"): 0.74,
    }

    # ── VISA DATA (representative examples, for demo) ──
    VISA_DATA = {
        ("United States", "France"):  {"required": False, "type": "Visa-Free (Schengen)",   "max_days": 90,  "fee": "$0",  "processing": "N/A"},
        ("United States", "Japan"):   {"required": False, "type": "Visa-Free",              "max_days": 90,  "fee": "$0",  "processing": "N/A"},
        ("United States", "Italy"):   {"required": False, "type": "Visa-Free (Schengen)",   "max_days": 90,  "fee": "$0",  "processing": "N/A"},
        ("United States", "UK"):      {"required": False, "type": "Visa-Free (eTA needed)", "max_days": 180, "fee": "$0",  "processing": "N/A"},
        ("India", "France"):          {"required": True,  "type": "Schengen Tourist Visa",  "max_days": 90,  "fee": "$90", "processing": "15 business days"},
        ("India", "Japan"):           {"required": True,  "type": "Tourist Visa",           "max_days": 30,  "fee": "$25", "processing": "5 business days"},
        ("India", "Italy"):           {"required": True,  "type": "Schengen Tourist Visa",  "max_days": 90,  "fee": "$90", "processing": "15 business days"},
        ("India", "UK"):              {"required": True,  "type": "Standard Visitor Visa",  "max_days": 180, "fee": "$115","processing": "15 business days"},
        ("UK", "France"):             {"required": False, "type": "Visa-Free (post-Brexit short stay)", "max_days": 90, "fee": "$0", "processing": "N/A"},
        ("UK", "Japan"):              {"required": False, "type": "Visa-Free",              "max_days": 90,  "fee": "$0",  "processing": "N/A"},
        ("Australia", "France"):      {"required": False, "type": "Visa-Free (Schengen)",   "max_days": 90,  "fee": "$0",  "processing": "N/A"},
        ("Australia", "Japan"):       {"required": False, "type": "Visa-Free",              "max_days": 90,  "fee": "$0",  "processing": "N/A"},
    }

    @kernel_function(
        name="calculate_trip_budget",
        description=(
            "Calculate the total estimated cost of a trip including flights, hotel, and daily expenses. "
            "Returns a detailed budget breakdown per person and grand total. "
            "Call this automatically after gathering flight and hotel prices."
        ),
    )
    def calculate_trip_budget(
        self,
        flight_cost_usd: float,
        hotel_per_night_usd: float,
        nights: int,
        daily_expenses_usd: float,
        num_travelers: int = 1,
    ) -> str:
        """
        Args:
            flight_cost_usd:     Round-trip flight cost per person in USD
            hotel_per_night_usd: Hotel nightly rate in USD
            nights:              Number of hotel nights
            daily_expenses_usd:  Daily spend per person (food, transport, activities)
            num_travelers:       Number of travelers (default 1)
        """
        hotel_total      = hotel_per_night_usd * nights
        daily_total      = daily_expenses_usd * nights
        cost_per_person  = flight_cost_usd + (hotel_total / num_travelers) + daily_total
        grand_total      = flight_cost_usd * num_travelers + hotel_total + daily_total * num_travelers

        result = {
            "num_travelers": num_travelers,
            "breakdown_per_person": {
                "flights":        f"${flight_cost_usd:,.0f}",
                "hotel_share":    f"${hotel_total / num_travelers:,.0f}  (${hotel_per_night_usd}/night × {nights} nights ÷ {num_travelers} travelers)",
                "daily_expenses": f"${daily_total:,.0f}  (${daily_expenses_usd}/day × {nights} days)",
                "total_per_person": f"${cost_per_person:,.0f}",
            },
            "grand_total_all_travelers": f"${grand_total:,.0f}",
            "hotel_total":   f"${hotel_total:,.0f}  ({nights} nights)",
            "budget_rating": (
                "Budget-friendly 💚" if grand_total < 2000
                else "Mid-range 💛" if grand_total < 5000
                else "Premium 💎"
            ),
            "saving_tips": [
                "Book flights 3–6 weeks ahead for best economy fares",
                "Consider shoulder season travel (Apr–May, Sep–Oct) for 20–30% savings",
                "Use a no-foreign-transaction-fee credit card abroad",
                "Look for hotels with free breakfast to cut daily costs",
            ],
        }
        return json.dumps(result, indent=2)

    @kernel_function(
        name="check_visa_requirements",
        description=(
            "Check visa requirements and entry rules for a traveler going from one country to another. "
            "Returns visa type, processing time, fees, max stay, and key document requirements. "
            "Call this whenever the user mentions their passport country or nationality."
        ),
    )
    def check_visa_requirements(
        self,
        passport_country: str,
        destination_country: str,
        trip_duration_days: int = 7,
    ) -> str:
        """
        Args:
            passport_country:     Traveler's passport/citizenship country (e.g. 'United States', 'India')
            destination_country:  Country to visit (e.g. 'France', 'Japan', 'Italy')
            trip_duration_days:   Intended length of stay in days (default 7)
        """
        # Normalize lookup
        key = (passport_country.strip().title(), destination_country.strip().title())
        visa = self.VISA_DATA.get(key)

        if visa:
            stay_ok = trip_duration_days <= visa["max_days"]
            result = {
                "passport":           passport_country,
                "destination":        destination_country,
                "trip_duration_days": trip_duration_days,
                "visa_required":      visa["required"],
                "entry_type":         visa["type"],
                "max_stay_days":      visa["max_days"],
                "stay_permitted":     stay_ok,
                "visa_fee":           visa["fee"],
                "processing_time":    visa["processing"],
                "key_documents": [
                    "Valid passport (min. 6 months validity beyond travel date)",
                    "Return / onward ticket",
                    "Proof of accommodation",
                    "Proof of sufficient funds",
                    *(["Completed visa application form", "Recent passport photos (2×)", "Travel insurance"] if visa["required"] else []),
                ],
                "advisory": (
                    f"⚠️  Your {trip_duration_days}-day stay exceeds the {visa['max_days']}-day maximum. "
                    "Please check with the consulate for long-stay visa options."
                    if not stay_ok else
                    f"✅  Your {trip_duration_days}-day stay is within the permitted {visa['max_days']}-day limit."
                ),
                "source_note": "Always verify with the official embassy or consulate before travel.",
            }
        else:
            # Generic fallback for passport/destination pairs not in the demo DB
            result = {
                "passport":        passport_country,
                "destination":     destination_country,
                "visa_required":   "Unknown — please verify",
                "entry_type":      "Not in demo dataset",
                "key_documents": [
                    "Valid passport (min. 6 months validity)",
                    "Return / onward ticket",
                    "Proof of accommodation",
                    "Travel insurance recommended",
                ],
                "advisory": (
                    f"⚠️  Visa data for {passport_country} → {destination_country} is not in the demo dataset. "
                    "Please check the official embassy website or IATA Travel Centre."
                ),
                "source_note": "Always verify with the official embassy or consulate before travel.",
            }

        return json.dumps(result, indent=2)

    @kernel_function(
        name="convert_currency",
        description=(
            "Convert an amount from one currency to another using approximate exchange rates. "
            "Useful for budget planning and price comparisons. "
            "Call this when the user mentions a non-USD budget or asks for price conversions."
        ),
    )
    def convert_currency(
        self,
        amount: float,
        from_currency: str,
        to_currency: str,
    ) -> str:
        """
        Args:
            amount:        Amount to convert
            from_currency: Source currency code (USD, EUR, GBP, JPY, INR, AUD, CAD, SGD, AED)
            to_currency:   Target currency code
        """
        fc = from_currency.strip().upper()
        tc = to_currency.strip().upper()

        if fc == tc:
            result = {
                "from": f"{amount:,.2f} {fc}",
                "to":   f"{amount:,.2f} {tc}",
                "rate": 1.0,
                "note": "Same currency — no conversion needed.",
            }
            return json.dumps(result, indent=2)

        rate = self.RATES.get((fc, tc))

        # Try inverse if direct not found
        if rate is None:
            inverse = self.RATES.get((tc, fc))
            if inverse:
                rate = 1 / inverse

        # Try via USD as bridge
        if rate is None and fc != "USD" and tc != "USD":
            to_usd   = self.RATES.get((fc, "USD"))
            usd_to_t = self.RATES.get(("USD", tc))
            if to_usd and usd_to_t:
                rate = to_usd * usd_to_t

        if rate is None:
            return json.dumps({
                "error": f"Exchange rate for {fc} → {tc} not available in demo dataset.",
                "supported_currencies": ["USD", "EUR", "GBP", "JPY", "INR", "AUD", "CAD", "CHF", "SGD", "AED"],
            }, indent=2)

        converted = amount * rate

        # Format based on currency (JPY/INR don't use decimals conventionally)
        fmt = ",.0f" if tc in ("JPY", "INR") else ",.2f"

        result = {
            "original":        f"{amount:,.2f} {fc}",
            "converted":       f"{converted:{fmt}} {tc}",
            "exchange_rate":   f"1 {fc} = {rate:.4f} {tc}",
            "rate_note":       "Approximate rate for planning purposes only.",
            "tip":             "Use Wise, Revolut, or a no-FX-fee card for best live rates when travelling.",
        }
        return json.dumps(result, indent=2)


# ──────────────────────────────────────────────────────────────────
# TRACK 2 — MCP SERVER TOOLS
# ──────────────────────────────────────────────────────────────────

def create_mcp_tools() -> list[ToolProtocol]:
    return [
        MCPStdioTool(
            name="travel_search_mcp",
            description="MCP server — search tools: search_flights, search_hotels, get_weather",
            command="node",
            args=[MCP_SEARCH_SERVER_PATH],
        ),
        MCPStdioTool(
            name="travel_planner_mcp",
            description="MCP server — planning tools: build_itinerary, get_travel_tips",
            command="node",
            args=[MCP_PLANNER_SERVER_PATH],
        ),
    ]


# ──────────────────────────────────────────────────────────────────
# INLINE TOOLS → ToolProtocol ADAPTER
# Extract @kernel_function decorated methods from the class
# and pass them as individual tool functions to the agent framework.
# ──────────────────────────────────────────────────────────────────

def create_inline_tools() -> list:
    """
    Extract and return individual @kernel_function decorated methods as tools.
    
    The agent framework expects individual callable functions, not class instances.
    We introspect the TravelInlineTools class and extract the decorated methods.
    """
    plugin_instance = TravelInlineTools()
    tools = []
    
    # Find all methods with @kernel_function decorator
    for attr_name in dir(plugin_instance):
        if attr_name.startswith('_'):
            continue
        
        attr = getattr(plugin_instance, attr_name)
        
        # Check if this method has the kernel_function marker
        if hasattr(attr, '_kernel_function') or (callable(attr) and not isinstance(attr, type)):
            # Only include actual methods that look like tool functions
            if attr_name in ['calculate_trip_budget', 'check_visa_requirements', 'convert_currency']:
                tools.append(attr)
                print(f"[INFO] Extracted inline tool: {attr_name}")
    
    if not tools:
        print("[WARN] No inline tools found! Attempting to extract by method inspection...")
        # Fallback: manually add the three known methods
        tools = [
            plugin_instance.calculate_trip_budget,
            plugin_instance.check_visa_requirements,
            plugin_instance.convert_currency,
        ]
        for tool in tools:
            print(f"[INFO] Added tool: {tool.__name__}")
    
    return tools


# ──────────────────────────────────────────────────────────────────
# FASTAPI APP
# ──────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Voyager — AI Travel Agent API",
    description=(
        "FastAPI wrapper around the Voyager travel agent.\n\n"
        "**Track 1 — Add Tools (inline):** calculate_trip_budget, check_visa_requirements, convert_currency\n\n"
        "**Track 2 — Add MCP Server:** search_flights, search_hotels, get_weather, build_itinerary, get_travel_tips"
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response models ──────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message to the travel agent", min_length=1)
    stream:  bool = Field(False, description="Enable streaming (SSE). Use /chat/stream endpoint instead.")

class ToolCall(BaseModel):
    name: str
    call_id: str

class ChatResponse(BaseModel):
    reply:      str
    tool_calls: list[ToolCall] = []
    model:      str
    status:     str = "success"

class HealthResponse(BaseModel):
    status:          str
    mcp_search_path: str
    mcp_planner_path:str
    inline_tools:    list[str]
    model:           str

class ToolInfo(BaseModel):
    name:   str
    track:  str
    source: str


# ── Core agent runner ─────────────────────────────────────────────

async def run_agent(user_message: str) -> tuple[str, list[dict]]:
    """
    Run the agent for a single turn.
    Returns (reply_text, list_of_tool_calls).
    """
    try:
        inline_tools = create_inline_tools()
        mcp_tools    = create_mcp_tools()
        all_tools    = [*inline_tools, *mcp_tools]

        print(f"[DEBUG] Inline tools: {inline_tools}")
        print(f"[DEBUG] MCP tools: {mcp_tools}")
        print(f"[DEBUG] All tools: {all_tools}")

        reply_parts: list[str] = []
        tool_calls:  list[dict] = []
        seen_call_ids: set[str] = set()

        async with (
            OpenAIChatClient(
                async_client=openai_client,
                model_id=MODEL_ID,
            ).create_agent(
                instructions=AGENT_INSTRUCTIONS,
                temperature=1,
                top_p=1,
                tools=all_tools,
            ) as agent
        ):
            async for chunk in agent.run_stream([user_message]):
                # Capture tool calls
                for content in chunk.contents:
                    if isinstance(content, FunctionCallContent):
                        if content.call_id not in seen_call_ids:
                            seen_call_ids.add(content.call_id)
                            tool_calls.append({
                                "name":    content.name,
                                "call_id": content.call_id,
                            })
                # Accumulate text
                if chunk.text:
                    reply_parts.append(chunk.text)

        return "".join(reply_parts), tool_calls
    except Exception as e:
        print(f"[ERROR] Agent error: {e}")
        traceback.print_exc()
        raise


async def stream_agent(user_message: str) -> AsyncGenerator[str, None]:
    """
    Stream the agent response as Server-Sent Events (SSE).
    Yields SSE-formatted strings.
    """
    try:
        inline_tools = create_inline_tools()
        mcp_tools    = create_mcp_tools()
        all_tools    = [*inline_tools, *mcp_tools]

        print(f"[DEBUG] Stream - Inline tools: {inline_tools}")
        print(f"[DEBUG] Stream - MCP tools: {mcp_tools}")
        print(f"[DEBUG] Stream - All tools: {all_tools}")

        seen_call_ids: set[str] = set()

        async with (
            OpenAIChatClient(
                async_client=openai_client,
                model_id=MODEL_ID,
            ).create_agent(
                instructions=AGENT_INSTRUCTIONS,
                temperature=1,
                top_p=1,
                tools=all_tools,
            ) as agent
        ):
            async for chunk in agent.run_stream([user_message]):
                # Emit tool call events
                for content in chunk.contents:
                    if isinstance(content, FunctionCallContent):
                        if content.call_id not in seen_call_ids:
                            seen_call_ids.add(content.call_id)
                            event = json.dumps({"type": "tool_call", "name": content.name, "call_id": content.call_id})
                            yield f"data: {event}\n\n"

                # Emit text chunks
                if chunk.text:
                    event = json.dumps({"type": "text", "content": chunk.text})
                    yield f"data: {event}\n\n"

        # Signal completion
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    except Exception as e:
        print(f"[ERROR] Stream agent error: {e}")
        traceback.print_exc()
        error_event = json.dumps({"type": "error", "message": str(e)})
        yield f"data: {error_event}\n\n"


# ── Endpoints ─────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health():
    """Health check — confirms agent config and tool list."""
    return HealthResponse(
        status="ok",
        mcp_search_path=MCP_SEARCH_SERVER_PATH,
        mcp_planner_path=MCP_PLANNER_SERVER_PATH,
        inline_tools=["calculate_trip_budget", "check_visa_requirements", "convert_currency"],
        model=MODEL_ID,
    )


@app.get("/tools", response_model=list[ToolInfo], tags=["System"])
async def list_tools():
    """List all tools registered with the agent (both tracks)."""
    return [
        # Track 1 — inline
        ToolInfo(name="calculate_trip_budget",   track="Track 1 — Add Tools (inline)", source="TravelInlineTools plugin"),
        ToolInfo(name="check_visa_requirements", track="Track 1 — Add Tools (inline)", source="TravelInlineTools plugin"),
        ToolInfo(name="convert_currency",        track="Track 1 — Add Tools (inline)", source="TravelInlineTools plugin"),
        # Track 2 — MCP Server 1
        ToolInfo(name="search_flights",          track="Track 2 — MCP Server 1 (travel-search-mcp)",  source="travel-mcp-server.js"),
        ToolInfo(name="search_hotels",           track="Track 2 — MCP Server 1 (travel-search-mcp)",  source="travel-mcp-server.js"),
        ToolInfo(name="get_weather",             track="Track 2 — MCP Server 1 (travel-search-mcp)",  source="travel-mcp-server.js"),
        # Track 2 — MCP Server 2
        ToolInfo(name="build_itinerary",         track="Track 2 — MCP Server 2 (travel-planner-mcp)", source="travel-planner-mcp-server.js"),
        ToolInfo(name="get_travel_tips",         track="Track 2 — MCP Server 2 (travel-planner-mcp)", source="travel-planner-mcp-server.js"),
    ]


@app.post("/chat", response_model=ChatResponse, tags=["Agent"])
async def chat(request: ChatRequest):
    """
    Single-turn chat with Voyager travel agent.
    
    Runs all 8 tools (3 inline + 5 MCP) as needed based on the user message.
    Returns the full response once complete.
    """
    try:
        reply, tool_calls = await run_agent(request.message)
        return ChatResponse(
            reply=reply,
            tool_calls=[ToolCall(**tc) for tc in tool_calls],
            model=MODEL_ID,
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@app.post("/chat/stream", tags=["Agent"])
async def chat_stream(request: ChatRequest):
    """
    Streaming chat with Voyager travel agent (Server-Sent Events).

    Response is a stream of SSE events:
    - `{"type": "tool_call", "name": "...", "call_id": "..."}` — when a tool is invoked
    - `{"type": "text",      "content": "..."}` — text chunks as they arrive
    - `{"type": "done"}`                         — stream complete
    - `{"type": "error",    "message": "..."}`   — if something goes wrong

    Example client (JavaScript):
    ```js
    const es = new EventSource('/chat/stream');
    es.onmessage = e => {
      const event = JSON.parse(e.data);
      if (event.type === 'text') process.stdout.write(event.content);
    };
    ```
    """
    return StreamingResponse(
        stream_agent(request.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control":     "no-cache",
            "X-Accel-Buffering": "no",   # Disable nginx buffering
        },
    )


# ──────────────────────────────────────────────────────────────────
# STANDALONE RUNNER  (python travel_agent.py)
# ──────────────────────────────────────────────────────────────────

async def _cli_demo() -> None:
    """Quick CLI test without starting the HTTP server."""
    demo_inputs = [
        "Hello! I'm planning a 5-day trip to Paris from New York in June. "
        "I have a US passport and a budget of around $3000. Can you help me plan everything?",
    ]
    for msg in demo_inputs:
        print(f"\n{'='*60}")
        print(f"User: {msg}")
        print(f"{'='*60}")
        seen: set[str] = set()

        inline_tools = create_inline_tools()
        mcp_tools    = create_mcp_tools()

        async with (
            OpenAIChatClient(
                async_client=openai_client,
                model_id=MODEL_ID,
            ).create_agent(
                instructions=AGENT_INSTRUCTIONS,
                temperature=1,
                top_p=1,
                tools=[*inline_tools, *mcp_tools],
            ) as agent
        ):
            async for chunk in agent.run_stream([msg]):
                for content in chunk.contents:
                    if isinstance(content, FunctionCallContent):
                        if content.call_id not in seen:
                            seen.add(content.call_id)
                            track = "Track 1 (inline)" if content.name in (
                                "calculate_trip_budget", "check_visa_requirements", "convert_currency"
                            ) else "Track 2 (MCP)"
                            print(f"\n[Tool Call → {track}] {content.name}")
                if chunk.text:
                    print(chunk.text, end="", flush=True)
        print("\n")

    print("--- Demo complete ---")
    await asyncio.sleep(1.0)


if __name__ == "__main__":
    import sys
    
    # Print diagnostics on startup
    print(f"\n{'='*70}")
    print(f"Voyager — AI Travel Agent | System Startup")
    print(f"{'='*70}")
    print(f"Python version: {sys.version.split()[0]}")
    print(f"FastAPI running on: http://0.0.0.0:8000")
    print(f"GitHub Models API: https://models.github.ai/inference")
    print(f"Model ID: {MODEL_ID}")
    
    # Test inline tools
    try:
        inline = create_inline_tools()
        print(f"✓ Inline tools: {len(inline)} methods extracted")
        for tool in inline:
            print(f"    - {tool.__name__}")
    except Exception as e:
        print(f"✗ Inline tools failed: {e}")
    
    # Test MCP tools
    try:
        mcp = create_mcp_tools()
        print(f"✓ MCP tools: {len(mcp)} servers configured")
        for i, tool in enumerate(mcp):
            print(f"    - {tool.name}")
    except Exception as e:
        print(f"✗ MCP tools failed: {e}")
    
    print(f"{'='*70}\n")
    
    if "--cli" in sys.argv:
        # Run CLI demo: python travel_agent.py --cli
        try:
            asyncio.run(_cli_demo())
        except KeyboardInterrupt:
            print("\nInterrupted.")
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
    else:
        # Start FastAPI server: python travel_agent.py
        uvicorn.run(
            "travel_agent:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info",
        )
