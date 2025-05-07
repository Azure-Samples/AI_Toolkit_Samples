# AI Toolkit & Azure AI Foundry Extension Demos

The following resources are intended for a presenter to learn and deliver AI Toolkit and Azure AI Foundry extension demos.

## AI Engineer Scenarios

|Scenario  |Description  |Duration  |Video  |
|---------|---------|---------|---------|
|[Explore and Compare Models](Extensions\AI-Toolkit-Extension\demo-aitk-explore-compare-models.md) (AITK)     | This demo guides users through exploring, deploying, and comparing AI models using the AI Toolkit extension for Visual Studio Code. It includes instructions for browsing the Model Catalog, chatting with models hosted by GitHub models, adding local models via Ollama, comparing responses from different models, and generating sample code to programmatically interact with models.        |  5 mins       |  Coming Soon      |
|[Evaluate Model Responses](Extensions\AI-Toolkit-Extension\demo-aitk-evaluate-model-responses.md) (AITK)    |  This demo focuses on evaluating AI model responses using the AI Toolkit extension for Visual Studio Code. It demonstrates how to set up and run evaluations, create custom evaluators, and analyze results. The demo leverages the GPT-4o model as a judge for evaluations and provides step-by-step instructions for configuring evaluators, importing datasets, and reviewing evaluation outcomes.       |  10 mins       |  Coming Soon        |
|[Create an Agent with Tools from a MCP Server](Extensions\AI-Toolkit-Extension\demo-aitk-create-agent-mcp-tools.md) (AITK)    |   This demo demonstrates how to create an AI agent with tools from an MCP (Model Context Protocol) server using the AI Toolkit extension for Visual Studio Code. It includes step-by-step instructions for setting up the environment, adding the GPT-4o model, configuring an MCP server, and integrating tools into the agent. The demo also covers creating system prompts, running the agent, structuring model output, and saving results to a file system.      |    10 mins     |  Coming Soon        |
|[Explore and Compare Models](Extensions\Azure-AI-Foundry-Extension\demo-aifx-explore-compare-models.md) (AIFX)     |    This demo showcases how to explore, deploy, and interact with AI models using the Azure AI Foundry extension and the AI Toolkit extension for Visual Studio Code. It provides step-by-step instructions for setting up the environment, browsing the model catalog, deploying models to Azure, and using the Playground to chat with models. The demo also covers comparing model responses, generating sample code for programmatic interaction, and managing model deployments, offering a comprehensive guide for leveraging Azure AI Foundry in AI development workflows.     |  5 mins       |   Coming Soon       |
|[Create an Agent with Tools](Extensions\Azure-AI-Foundry-Extension\demo-aifx-create-agent-tools.md) (AIFX)     |   This demo explains how to create and deploy an AI agent with tools, such as Grounding with Bing Search, using the Azure AI Foundry extension for Visual Studio Code. It provides instructions for creating and deploying an agent to Azure AI Foundry. The demo also includes steps for interacting with the agent in the Agent Playground and reviewing execution threads.      |   7 mins      |  Coming Soon       |

## FAQs

#### Where can I download the AI Toolkit?
You can download and install the AI Toolkit within the **Extensions View** in Visual Studio Code. Alternatively, you can visit [aka.ms/AIToolkit](https://aka.ms/AIToolkit) to view the extension in the Visual Studio Marketplace.

#### Where can I download the Azure AI Foundry extension?
You can download and install the Azure AI Foundry extension within the **Extensions View** in Visual Studio Code. Alternatively, you can visit the [Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=TeamsDevApp.vscode-ai-foundry).

#### Where can I find the documentation for the AI Toolkit?
Documentation for the AI Toolkit is available at [aka.ms/AITookit/doc](https://aka.ms/AIToolkit/doc).

#### Where can I find the documentation for the Azure AI Foundry extension?
Documentation for the Azuer AI Foundry extension is available on Microsoft Learn:
- [Work with the  Azure AI Foundry for Visual Studio Code extension](aka.ms/aif-vscode-doc)
- [Work with Azure AI Agent Service in Visual Studio Code](aka.ms/aif-vscode-agent-doc)

#### Can I use my own models or other models from Hugging Face?
If your own model supports the OpenAI API contract, you can host it in the cloud and [add the model to AI Toolkit](https://code.visualstudio.com/docs/intelligentapps/models) as a custom model. You need to provide key information such as model endpoint URL, access key and model name.

#### Does the extension work in Linux or other systems?
Yes, AI Toolkit runs on Windows, Mac, and Linux.

#### Why does the AI Toolkit need GitHub and Hugging Face credentials?
We host all the project templates in GitHub, and the base models are hosted in Azure or Hugging Face. These environments require an account for access via the APIs.
