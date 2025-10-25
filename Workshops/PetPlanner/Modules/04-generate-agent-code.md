# 🐕 Module 4: Generate Agent Code

You’ve used the AI Toolkit (AITK) so far to quickly prototype and test your agent’s behavior.
Now, it’s time to move from a low-code prototype to a code-first workflow — giving you full control over your agent’s logic, structure, and integration.

Generating agent code allows you to:

- Extend and customize the agent’s behavior beyond the AITK UI.
- Add features, APIs, and new data connections directly in code.
- Collaborate through Git and version your agent like any other software project.

> [!WARNING]
>Do not stop the debugger. The debugger should remain running for the rest of this workshop. If the debugger is stopped, the Pet Planner MCP server will no longer run locally which prevents server access for the agent.

## 🧩 Instructions

1. At the bottom left of the **Agent Builder**, click **View Code**.
1. For the **SDK** select **Microsoft Agent Framework**.
1. For the **Programming Language** select **Python**.
1. Save the file at the root of your project as `pet-planner-agent`.
1. Before running the script, open a new **terminal** and run the command `az login` to authenticate to Azure. A log-in window will appear. When prompted, select your user. Next, in the **terminal**, select your subscription.
1. Next, install the **Microsoft Agent Framework (Pre-release)**. In the **terminal** run the command: `uv pip install agent-framework --pre`.
1. In the **terminal** run the command `python pet-planner-agent.py`.
1. Review the agent output.

## 🔍 What’s Happening

The AI Toolkit’s prototype definitions are now being translated into executable code.
This marks a key transition:

- The AI Toolkit was ideal for prototyping — testing logic, tuning behavior, and exploring ideas quickly.
- The code-first workflow empowers you to develop, debug, and extend your agent using standard development practices.

You now have full flexibility to:

- Integrate APIs or additional MCP servers.
- Add new commands and data flows.
- Deploy or share your agent with your team.

## ✅ Checkpoint

You should have a Pet Planner agent file (i.e. `pet-planner-agent.python`) that runs successfully.

## 🐾 Next Step

Continue to [Trace Agent Responses](/Workshops/PetPlanner/Modules/05-trace-agent-responses.md)