# Voyager — AI Travel Agent Demo

A fully functional AI-powered travel planning assistant with a beautiful frontend and Microsoft Agent Framework backend.

## 🚀 Quick Start (Today's Demo)

### Prerequisites
- Python 3.10+
- Node.js 18+ (for MCP servers, if using)
- `GITHUB_TOKEN` environment variable set (for GitHub Models API)

### 1. **Install Dependencies**

Using the requirements file:
```bash
cd f:\Travel-agent
pip install -r requirements.txt
```

Or manually:
```bash
pip install agent-framework==1.0.0b260107 fastapi uvicorn pydantic anthropic openai
```

### 2. **Set Environment Variables**

**Windows PowerShell:**
```powershell
$env:GITHUB_TOKEN = "your_github_token_here"
$env:MCP_SEARCH_PATH = "C:\path\to\travel-mcp-server.js"
$env:MCP_PLANNER_PATH = "C:\path\to\travel-planner-mcp-server.js"
```

Or update the paths directly in `travel_agent.py` lines 47-50.

### 3. **Start the Backend Server**

```bash
python travel_agent.py
```

Or with uvicorn directly:
```bash
uvicorn travel_agent:app --host 0.0.0.0 --port 8000 --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### 4. **Open the Frontend**

Open your browser to:
```
file:///f:/Travel-agent/index.html
```

Or serve it with a local server:
```bash
python -m http.server 8001 --directory f:\Travel-agent
```

Then visit: `http://localhost:8001`

---

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Single-turn chat (full response) |
| POST | `/chat/stream` | Streaming chat (SSE) |
| GET | `/health` | Health check & config |
| GET | `/tools` | List all 8 tools |

**Example cURL:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Plan a 7-day trip to Japan"}'
```

---

## 🛠️ Architecture

### **Track 1: Inline Custom Tools** (No server needed)
- `calculate_trip_budget` — Budget breakdown for flights, hotels, expenses
- `check_visa_requirements` — Visa lookup table (10+ country pairs)
- `convert_currency` — Currency conversion with live rates

### **Track 2: MCP Server Tools** (Node.js MCP servers)
- `search_flights` — Find flights (via travel-mcp-server.js)
- `search_hotels` — Find hotels (via travel-mcp-server.js)
- `get_weather` — Get destination weather (via travel-mcp-server.js)
- `build_itinerary` — Generate trip itinerary (via travel-planner-mcp-server.js)
- `get_travel_tips` — Insider travel tips (via travel-planner-mcp-server.js)

---

## 💡 Demo Prompts to Try

1. **"Plan a 5-day trip to Paris from New York. I have a US passport and a budget of $3000."**
   - Uses: search_flights, search_hotels, get_weather, calculate_trip_budget, check_visa_requirements

2. **"What's the visa requirement for an Indian citizen going to Japan for 30 days?"**
   - Uses: check_visa_requirements (Track 1)

3. **"Convert €500 to USD and calculate the trip cost for 2 travelers with $1200 flights and $150/night hotels for 5 nights."**
   - Uses: convert_currency, calculate_trip_budget (both Track 1)

4. **"Build a 3-day itinerary for Tokyo and get local travel tips."**
   - Uses: build_itinerary, get_travel_tips (Track 2 MCP)

---

## 🎨 Frontend Features

- **Real-time Streaming** — SSE (Server-Sent Events) for live chat updates
- **Tool Call Visualization** — Color-coded badge display for Track 1 (orange) vs Track 2 (blue)
- **Markdown Rendering** — Converts agent responses to formatted HTML
- **Responsive Design** — Beautiful dark theme with gradient accents
- **Quick Prompts** — Pre-built example questions
- **Auto-scrolling** — Keeps focus on latest message
- **Error Handling** — Clear messages if backend is offline

---

## 🔧 Customization

### **Add More Visa Data**
Edit `TravelInlineTools.VISA_DATA` in `travel_agent.py` (lines ~112-126)

### **Update Exchange Rates**
Edit `TravelInlineTools.RATES` in `travel_agent.py` (lines ~103-108)

### **Change OpenAI Model**
Edit `MODEL_ID` variable (line 55) or use your own:
```python
MODEL_ID = "gpt-4-turbo"  # or your model ID
```

### **Update MCP Server Paths**
Edit lines 47-50 in `travel_agent.py` or set environment variables:
```bash
set MCP_SEARCH_PATH=C:\Users\yourname\path\travel-mcp-server.js
```

---

## 📊 System Prompt

The agent follows detailed instructions (AGENT_INSTRUCTIONS, lines ~63-105) to:
1. Act as "Voyager" — an expert travel agent
2. Use Track 1 tools automatically when needed (budget, visa, currency)
3. Call MCP tools for live data (flights, hotels, weather, tips)
4. Provide structured, markdown-formatted responses
5. Use emojis and tables for clarity

---

## 🚨 Troubleshooting

### **"Connection failed" or "Backend not accessible"**
- ✅ Verify FastAPI is running on port 8000
- ✅ Check `http://localhost:8000/health` in browser
- ✅ Ensure no firewall is blocking port 8000

### **"GITHUB_TOKEN not set" error**
- ✅ Set your GitHub token:
  ```powershell
  $env:GITHUB_TOKEN = "xxxxxxxxxxxx"
  ```

### **MCP Server errors**
- ✅ Verify Node.js is installed: `node --version`
- ✅ Check MCP server paths are correct
- ✅ MCP servers can be offline — Track 1 tools will still work

### **No tool calls appearing**
- ✅ Check browser console (F12) for errors
- ✅ Verify model permissions to use tools
- ✅ Try simpler prompts first (e.g., "Convert 100 USD to EUR")

### **"is not a callable object" error**
- ✅ This was a tool registration issue — it's been fixed
- ✅ Inline tools are now extracted as individual method callables
- ✅ The agent framework receives: 3 inline methods + 2 MCP servers = 5 tools
- ✅ Restart the backend: `python travel_agent.py`
- ✅ Check terminal output for `✓ Inline tools:` message showing extracted methods
- ✅ If still failing, run: `python test_diagnostics.py` for detailed debugging

---

## 📦 Files

| File | Purpose |
|------|---------|
| `travel_agent.py` | FastAPI backend with Agent Framework + 8 tools |
| `index.html` | Frontend UI with real-time streaming + error handling |
| `README.md` | This file |

---

## 🎯 What Makes This Demo Stand Out

✅ **Two Tool Tracks** — Shows both inline (no-dependency) and MCP (server) tools  
✅ **Real Streaming** — SSE for live chat updates, not polling  
✅ **Production UI** — Professional design with error states  
✅ **Demo-Ready** — Quick setup, clear instructions, example prompts  
✅ **Extensible** — Easy to add more tools or customize behavior

---

## 📝 Notes

- Visa data & exchange rates are for demo purposes — verify before actual travel!
- MCP servers (search_flights, search_hotels, etc.) require running Node.js servers
- Track 1 tools work instantly; Track 2 depends on MCP server availability
- Agent uses OpenAI API via GitHub Models — ensure good internet connection

---

**Happy travels! 🌍✈️**
