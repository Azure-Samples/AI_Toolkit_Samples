# 🐕 Module 3: Connect an MCP Server

Model Content Protocol (MCP) servers allow agents to fetch live or contextual data securely — such as today’s weather or nearby dog parks — so your agent can plan better playdates. Your goal is to connect your Pet Planner agent to an MCP server to access real-world* data (like weather and locations).

> [!NOTE]
>We'll be using simulated "live data" for this workshop.

## 🧩 Instructions

1. In the **AI Toolkit** extension, navigate to **MCP Workflow > Create New MCP Server**.
1. For **Select MCP Server Template**, select **python-weather**.
1. For **Select Folder**, select the **Default folder**.
1. For **Enter MCP Server Name**, enter: `pet-planner`
1. A new Visual Studio Code window will open. In the new Visual Studio Code window, open a new terminal.
1. In the terminal, run the command `uv venv` to create a virtual environment.
1. Next, activate the virtual environment via the command palette. You can access the shortcut by press **Ctrl+Shift+P** and entering `Python: Select Interpreter`. Next, select the virtual environment that you just created.
1. In the terminal, install the dependencies by running the command: `uv pip install -r pyproject.toml --extra dev`
1. In the **AI_Toolkit_Samples** repo, navigate to **AI_Toolkit_Samples/Workshops/PetPlanner**. Open the `pet-planner-server.py` file and copy the content of the file.
1. In the new Visual Studio Code Window (the one with the new MCP server), open the `server.py` file (location: `src/server.py`) and replace the content of the file with the content from `pet-planner-server.py`.
1. Click the **Run and Debug** icon (i.e. on the left under **Source Control**). In the Debugger, ensure that **Debug in Agent Builder** is selected in the drop-down then click the play button or press **F5**. The debugger will start and the **Agent Builder** will open.
1. In the **Agent Builder**, select the **Pet Planner** agent and ensure that the **gpt-4.1-mini Remote via Azure AI Foundry** model is selected.
1. Within the **Tool** section, click the **+** button and select **MCP Server**. 
1. Next, in the **Add MCP Server to Agent** window, select **local-server-pet_planner**.
1. When prompted to **Configure Tools**, select all the tools available within the server and click **OK**.
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

Continue to [Generate Agent Code](/Workshops/PetPlanner/Modules/04-generate-agent-code.md)