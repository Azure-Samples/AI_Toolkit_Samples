# Create an Agent with Tools

**Duration**: 7 mins

This demo explains how to create and deploy an AI agent with tools, such as Grounding with Bing Search, using the [Azure AI Foundry](https://marketplace.visualstudio.com/items?itemName=TeamsDevApp.vscode-ai-foundry) extension for Visual Studio Code. It provides instructions for creating and deploying an agent to Azure AI Foundry. The demo also includes steps for interacting with the agent in the Agent Playground and reviewing execution threads.

## Prerequisites

- [Visual Studio Code](https://code.visualstudio.com/)
- [Azure AI Foundry extension](https://marketplace.visualstudio.com/items?itemName=TeamsDevApp.vscode-ai-foundry)
- [An existing Azure AI Foundry project](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/create-projects?tabs=ai-studio) (note: The extension interacts with Azure AI Foundry at the project level.)
- [Grounding with Bing Search](https://portal.azure.com/#create/Microsoft.BingGroundingSearch) resource

## Setup Instructions

### Set your default project

The Azure AI Foundry extension interacts with Azure AI Foundry at the project level. Before running the demo, you'll need to sign-in to Azure and select your default project.

1. In Visual Studio Code, select the Azure icon from the **Activity Bar**.
1. In the **Resources** section, select **Sign in to Azure...**. You'll be prompted to sign-in.
1. Once you're signed-in, navigate to the **Resources** section and select your **Azure Subscription** followed by your **Resource Group**.
1. Select **Azure AI Foundry**
1. Right-click your project and select **Open in Azure AI Foundry Extension**.

### Connect the Grounding with Bing Search resource to your project

The **Grounding with Bing Search** resource must be connected to the Azure AI Foundry project that'll be used for this demo. The connection can be made within the **Management Center** of your project.

1. Navigate to the [Azure AI Foundry portal](https://ai.azure.com) and select your project.
1. In the left navigation menu, towards the bottom, select **Management center**.
1. In the **Connected resources** section, select **New connection**.
1. In the **Add a connection to external assets** window, select **Grounding with Bing Search**.
1. In the **Connect a Grounding with Bing Search Account** window, select **Add connection** next to your **Grounding with Bing** resource.
1. Click **Close**.

### Prepare the Bing Grounding tool YAML

For ease of preparation, the `bing_grounding.yml` file contains the yaml that'll later be required for adding **Grounding with Bing Search** as a tool for the agent. The YAML contains placeholder values that should be replaced prior to running the demo. The values for the placeholders are available within the **Overview** section of the **Management center** of your project. Open the file and replace the following placeholders:

- `subscription_ID` = Your Subscription ID
- `resource_group_name` = Your Resource Group name
- `project_name` = Your Project name
- `bing_grounding_connection_name` = The connection name **NOT** the resource name

Provided below is an example of the `tool-connection` for `bing_grounding`:

`/subscriptions/a4f7c123-9be2-4c88-a9df-8e3a6b75fc10/resourceGroups/rg-aifx-demo/providers/Microsoft.MachineLearningServices/workspaces/aifx-demo/connections/aifxbinggrounding`

## Running the Demo

In this demo, you’ll show how to create, deploy, and interact with an AI agent using the Azure AI Foundry extension. You’ll take the audience through the full process—from configuring agent metadata to running it in the Playground and inspecting execution threads.

### Create an agent

In this section, you’ll show how to create a new agent using the agent designer and YAML editor. You’ll configure basic metadata, assign a model, add instructions, and manually add a tool like Grounding with Bing Search. This highlights how both visual and code-based editing can be used together for agent configuration.

1. Open the **Azure AI Foundry** extension from the **Activity Bar**.
1. In the **Resources** section, within the **Agents** subsection, hover over **Agents** and click the **+** icon that appears. You will be prompted the save the agent file.
1. In the file save dialog that appears, navigate to the directory in which you want to save the agent file. Name the file `content-agent` and click **Save Agent File**. A notification will appear in the bottom-right corner confirming that the agent file was successfully saved. The agent YAML file and designer will open.
1. In the designer editor (right), enter the following:
    1. Name: **Content Agent**
    1. Model: **gpt-4o**
    1. Instructions: Copy and paste the instructions from the `system-prompt.md` file.
1. In the agent YAML file (left), complete the following:
    1. In the `metadata.authors` sequence, replace the `author1` value with your name and remove the `author2` value.
    1. In the `metadata.tags` sequence, remove the values `tag1` and `tag2`.
    1. Replace the `tools` key, with the entry in the **bing_grounding.yml** file (do not add via the designer).
1. Save the agent yaml file.
1. In the designer editor (right), validate that the **Bing Grounding** tool appears in the **Tool** section.
1. At the bottom of the designer editor, click the **Deploy to Azure AI Foundry** button. A notification will appear in the bottom-right corner confirming that the agent was successfully created.

### Run the agent

After deploying the agent, this section takes the audience through running the agent in the Agent Playground. You’ll demonstrate how to submit a prompt, view the response, and optionally carry on the conversation—bringing your agent to life in a natural, chat-like interface.

1. In the left **Activity Bar**, navigate to the **Resources** section.
1. Expand the **Agents** subsection and confirm that the **Content Agent** appears in the list of agents.
1. In the left **Activity Bar**, navigate to the **Tools** section and select **Agent Playground**. The extension will launch a setup wizard via the **Command Palette**.
1. Select the agent. The **Agent Playground** will then open in a new editor tab.
1. In the **chat window**, type the following into the chat input and press **Enter** : `Find three recent blog posts or articles (published in the past month) about how AI is being used by developers. Summarize the key takeaways from each, and suggest one new content idea inspired by the trends you found.`.
1. Review the agent's response and submit a suitable follow-up prompt.

### View threads

Finally, you'll show the audience how to inspect the execution history of the agent by reviewing its threads. This section focuses on exploring a specific response, expanding the step details, and gaining insight into how the agent processed the request—perfect for debugging and transparency.

1. In the left **Activity Bar**, navigate to the **Resources** section.
1. Expand the **Threads** subsection.
1. Select the first successful thread (indicated with a green circle and check-mark).
1. In the agent's response, expand the **Step details** and review the information provided.

## Clean-up
1. In the **Azure AI Foundry** panel (Side Bar), go to the **Resources** section.
1. Within the **Agents** subsection, right-click the **Content Agent** and select **Delete**.