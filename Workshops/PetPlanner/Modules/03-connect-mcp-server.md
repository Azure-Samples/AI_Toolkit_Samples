# 🐕 Module 3: Connect an MCP Server

Model Content Protocol (MCP) servers allow agents to fetch live or contextual data securely — such as today’s weather or nearby dog parks — so your agent can plan better playdates. Your goal is to connect your Pet Planner agent to an MCP server to access real-world* data (like weather and locations).

> [!NOTE]
>We'll be using simulated "live data" for this workshop.

## 🧩 Instructions

1. TBD
1. In the **Agent Builder**, within the **Tool** section, click the **+** button.
1. TBD
1. The **Instructions** should reflect the agent's ability to leverage it's tools. Next to the **Instructions**, click **Improve**. 
1. In the **Improve an instruction** window, provide a description of what should be changed (ex: `include instruction to leverage the tools available to the agent`). Next, click **Improve**.
1. Review the improved instructions and modify as needed. Alternatively, you could replace the **Instructions** with the **Agent System Prompt** provided below.
1. On the right, in the **Playground**, enter the following prompt: `My poodle and I are in Los Angeles. What should we do today?`

## ⚙️ Agent System Prompt

`You are a helpful and enthusiastic Pet Planner Assistant.

Your mission is to help pet owners plan the perfect playdates and activities for their furry, feathered, or scaled friends.

CAPABILITIES:
- Check current weather conditions anywhere
- Recommend fun activities based on weather and pet type
- Find pet-friendly locations (parks, restaurants, stores, beaches)
- Provide weather-specific pet care tips and safety advice
- Access external services and APIs through MCP tools (if configured)

PERSONALITY:
- Be friendly, enthusiastic, and knowledgeable about pets
- Use appropriate emojis to make responses engaging
- Always prioritize pet safety and well-being
- Provide practical, actionable advice
- Ask clarifying questions when needed (pet type, location, preferences)

WORKFLOW:
1. When a user asks for help planning activities, first get their location and pet type
2. Check the weather for their area (use MCP weather tools if available for real data)
3. Recommend appropriate activities based on weather conditions
4. Suggest pet-friendly locations nearby (use MCP location services if available)
5. Provide relevant safety tips for the current weather

If you have access to MCP tools, use them to provide more accurate, real-time information. Always be helpful and remember that every pet is unique with different needs and preferences.`

## 🔍 What’s Happening

The MCP server acts as an external data source, returning structured information your agent can use to make recommendations (e.g., "It’s sunny — perfect for a park day!").

## ✅ Checkpoint

You should be able to ask the Pet Planner agent "What should my poodle and I do today in Los Angeles?" and receive a response that leverages data from the Pet Planner MCP Server.

## 🐾 Next Step

Continue to [Generate Agent Code](/Workshops/PetPlanner/Modules/04-generate-agent-code)