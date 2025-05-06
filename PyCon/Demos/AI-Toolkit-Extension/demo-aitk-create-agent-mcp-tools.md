# Create an Agent with Tools from a MCP Server

**Duration**: TBD

This demo demonstrates how to create an AI agent with tools from an MCP (Model Context Protocol) server using the [AI Toolkit](https://aka.ms/AITookit) extension for Visual Studio Code. It includes step-by-step instructions for setting up the environment, adding the GPT-4o model, configuring an MCP server, and integrating tools into the agent. The demo also covers creating system prompts, running the agent, structuring model output, and saving results to a file system.

## Prerequisites

- [Visual Studio Code](https://code.visualstudio.com/)
- [AI Toolkit for Visual Studio Code](https://aka.ms/AIToolkit)
- [GitHub Fine-grained personal access token (PAT)](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token)

## Setup Instructions

### Add the OpenAI GPT-4o model

The demo leverages the **GPT-4o** model as the chosen model for the agent. The model should be added to **My Models** before running the demo.

1. Open the **AI Toolkit** extension from the **Activity Bar**.
1. In the **Catalog** section, select **Models** to open the **Model Catalog**. Selecting **Models** opens the **Model Catalog** in a new editor tab.
1. In the **Model Catalog** search bar, enter **OpenAI GPT-4o**.
1. Click **+ Add** to add the model to your **My Models** list. Ensure that you've selected the model that's **Hosted by GitHub**.
1. In the **Activity Bar**, confirm that the **OpenAI GPT-4o** model appears in the list.

### Prepare the MCP server command

The demo leverages the [Filesystem](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem) MCP server to write to a directory. Before running the demo, create a new  `demo` directory on your desktop (or another easily accessible location) for the agent to save new files. Once the directory is created, take note of the **file path** as it'll be required for the MCP server command.

For ease of preparation, the `MCP_command.txt` file contains the command that'll be required for adding the Filesystem MCP server. Open the file and replace the following placeholders:

- `username` = Your system's user name (ex: `janedoe`)
- `directory_location` = File path to the directory (ex: `Desktop/demo`)

Provided below is an example of the command:

`npx -y @modelcontextprotocol/server-filesystem /Users/janedoe/Desktop/demo`

## Running the Demo

In this demo, you’ll show how to build, run, and enhance an AI agent inside Visual Studio Code using the AI Toolkit. This walkthrough covers prompt authoring, memory simulation, tool integration via MCP servers, and structured output—all within a single, cohesive workflow.

### Create an agent

Start by introducing your audience to the **Agent (Prompt) Builder**—a space where they can create and customize their own AI-powered agents. In this section, you’ll show the audience how to create a new agent, give it a name, and assign a model like GPT-4o to power the conversation.

1. Open the **AI Toolkit** extension from the **Activity Bar**.
1. In the **Tools** section, select **Agent (Prompt) Builder**. Selecting **Agent (Prompt) Builder** opens the **Agent (Prompt) Builder** in a new editor tab.
1. Click the **+ New Builder** button. The extension will launch a setup wizard via the **Command Palette**.
1. Enter the name **Content Agent** and press **Enter**.
1. In the **Agent (Prompt) Builder**, for the **Model** field, select the **OpenAI GPT-4o (via GitHub)** model.

### Create a system prompt for the agent

With the agent scaffolded, it’s time to define its personality and purpose. In this section, you’ll demonstrate how to use the **Generate system prompt** feature to describe the agent’s intended behavior—in this case, a content creator agent—and have the model write the system prompt for you.

1. For the **Prompts** section, click the **Generate system prompt** button. This button opens in the prompt builder which leverages AI to generate a system prompt for the agent.
1. In the **Generate a prompt** window, enter the following: `I want to create an agent that creates social media content across the following mediums: blogs, video scripts and captions for posts.`
1. Click the **Generate** button. A notification will appear in the bottom-right corner confirming that system prompt is being generated. Once the prompt generation is complete, the prompt will appear in the **System prompt** field of the **Agent (Prompt) Builder**.
1. Review the **System prompt** and modify if necessary.

### Run the agent

Now that the system prompt is set, you’ll guide the audience through running the agent with a user prompt, reviewing the response, and then simulating conversation history by adding model responses back into the prompt sequence. This shows how the agent can “remember” past messages for a more contextual chat experience.

1. In the **User prompt** field, enter the following prompt: `Create a short LinkedIn post about developer productivity with AI tools`.
1. Click the **Run** button to generate the agent's response.
1. On the right side of the **Agent (Prompt) Builder**, review the **Model Response**.
1. Under the **Model Response**, click **Add to Prompts** to append the model's output to the prompts. This action add's the **Model Response** as an **Assistant prompt** and simulates maintaining conversational context with the agent. When you submit another **User Prompt** and run the agent again, the previously added **Model Response** will be included in the prompt, allowing the model to reference it as part of the conversation history. (*Note*: Adding the **Model Response** to prompts automatically adds a new blank **User prompt**.)
1. In the newly added **User prompt** field, enter the following prompt as a follow-up to the agent's response: `Revise to be more casual`.
1. Click the **Run** button to generate the agent's response.
1. Review the **Model Response**.
1. Under the **Model Response**, click **Add to Prompts** to append the model's output to the prompts.

### Add an MCP server

Up until now, your agent has only generated text. In this section, you’ll introduce the audience to MCP servers, which allow the agent to use external tools. You’ll demonstrate how to connect to a local file-based server using a terminal command, bringing real-world actions into your agent's reach.

Once the MCP server is connected, you'll show how to select tools from the server and integrate them into your agent. These tools allow the agent to take actions like writing files or performing lookups, enabling task completion beyond just text generation.

1. In the **Tools** section of the **Agent (Prompt) Builder**, click the **+ MCP Server** button. The extension will launch a setup wizard via the **Command Palette**.
1. Select **+ Add Server**.
1. Select **Connect to an Existing MCP Server**.
1. Select **Command (stdio)**.
1. Enter the following command to run: `npx -y @modelcontextprotocol/server-filesystem /Users/<username>/<directory_location>`. (Note: Replace `<username>` with your system's user name. Replace `<directory_location>` with the file path to the directory.)
1. Enter the following name for the server: **Filesystem**.
1. Select the following tools and click **OK**:
    1. read_file
    1. write_file
    1. edit_file
1. Review the tools added by opening the **Tools List** within the **Tools** section. (*Note*: To modify the server command, click the server name in the **Tools** section to access its `mcp.json` file.)

### Run the agent with tools

Now that your agent has tools, it's time to use them. This section demonstrates how the agent can respond to a prompt by both generating content and taking action—like writing a file to your system. You’ll show the audience how to find and verify that file on their machine.

1. In the newly added **User prompt**, enter the following: `Create 5 related short LinkedIn posts about the benefits of using AI tools for developer productivity. Save the posts in a new file called "AI-productivity-series"`. (*Note*: If you did not add the prior **Model Response**, you can manually add a new **User prompt** field. Navigate to the top of the **Agent (Prompt) Builder**, click the **Add Prompt** button and select **User prompt**.)
1. Click the **Run** button to generate the agent's response.
1. Review the agent output.
1. In your file system, navigate to the directory that was chosen for the MCP Server command. (*Note*: If successful, the **Tool Response** provides the location in which the new file was written. The initial model response may insist that access to the path is denied, however, the follow-up model response should indicate that it was able to write to the directory.)
1. In the directory, validate that the agent created the file.
1. Open the file to review its content.

### Structure the model output

Up to this point, your output has been unstructured text. This final section demonstrates how to format the model’s response using a JSON schema, ensuring structured outputs that can be easily parsed or consumed by other systems. This is especially useful for API responses, content formatting, and automated pipelines.

1. Open the `single-post-schema.json` file to view it's structure. Notice that the structure includes a section for the post and its corresponding hashtags.
1. In the **Structure output** section of the **Agent (Prompt) Builder**, click the **Choose output format** drop-down and select **json_schema**.
1. Click the **Prepare schema** button. The extension will launch a setup wizard via the **Command Palette**.
1. Select **Select local file**.
1. In the file explorer, select the `single-post-schema.json` file and click **Open**.
1. In the **Agent (Prompt) Builder**, delete the following user prompts:
    1. `Revise to be more casual`
    1. `Create 5 related short LinkedIn posts about the benefits of using AI tools for developer productivity. Save the posts in a new file called "AI-productivity-series.`
1. Navigate to the top of the **Agent (Prompt) Builder**, click the **Add Prompt** button and select **User prompt**.
1. In the newly added **User prompt**, enter the following: `Write a short LinkedIn post about AI developer productivity`.
1. Click the **Run** button to generate the agent's response.
1. Review the **Model Response** to validate the json schema format.

## Clean-up
1. In the **AI Toolkit** panel (Side Bar), in the **Tools** section, select **Agent (Prompt) Builder**.
1. At the top left of the **Agent (Prompt) Builder**, select the **Recent** button.
1. Select the **trash** icon next to the agent.
1. In the **Confirm Prompt Deletion** pop-up, select **Delete**.