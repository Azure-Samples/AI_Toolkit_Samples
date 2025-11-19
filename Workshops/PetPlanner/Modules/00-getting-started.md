# Getting Started - Pet Planner Workshop

Welcome to the PetPlanner Workshop! This guide will walk you through all the setup steps needed to complete this workshop.

## Prerequisites

### Required Accounts

- [Azure](https://signup.azure.com/) subscription
- [GitHub](https://www.github.com) with a [GitHub Copilot](https://github.com/github-copilot/signup) subscription

### Development Environment

- [Python 3.10](https://www.python.org/downloads/) (or higher)
- [uv](https://docs.astral.sh/uv/#installation) - A fast Python package installer and resolver (alternative to pip)
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli-windows?view=azure-cli-latest&pivots=winget) - Used for Azure authentication and resource management
- [Visual Studio Code](https://code.visualstudio.com/download)
  - [AI Toolkit](https://aka.ms/AIToolkit) extension
  - [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) extension
  - [Azure Resources](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azureresourcegroups) extension

## Visual Studio Code Setup

### Confirm Access to GitHub Models with GitHub Copilot

1. In Visual Studio Code, click the **Toggle Chat** icon to open **GitHub Copilot**.
1. In the **Pick Model** drop-down, confirm the availability of **Claude Sonnet 4** and **Claude Sonnet 4.5**.
1. Set the model to **Claude Sonnet 4.5**.

> [!NOTE]
> If you reach your quota limit using **Claude Sonnet 4.5** with GitHub Copilot, feel free to use **Claude Sonnet 4** as an alternative.

### Confirm Version of the AI Toolkit

1. Open the **Extensions** and select **AI Toolkit**.
1. Confirm that version **0.24.1** or later is installed.
2. If you're using an older version of the AI Toolkit extension, update to the latest version.

### Create a Microsoft Foundry Project

1. Navigate to the [Microsoft Foundry](https://ai.azure.com) portal.
2. If you do not have any existing Foundry projects, complete the [Microsoft Foundry Quickstart - Create resources](https://learn.microsoft.com/azure/ai-foundry/quickstarts/get-started-code?tabs=azure-ai-foundry#first-run-experience) instructions.
3. If you have an existing Foundry project, deploy the **gpt-4.1-mini** model using the **Default settings**.

### Sign-In to Azure

1. Open the **Azure Resources** extension (i.e. Azure icon).
1. Select **Sign in to Azure…**.
1. For **The extension 'Azure Resources' wants to sign in using Microsoft**, select **Allow**.
1. For the sign-in screen, enter your Azure subscription credentials.
1. Click **Sign in**.

### Set the Default Foundry Project in Visual Studio Code

1. In Visual Studio Code, in the **Azure Resources** extension, expand your Azure subscription and expand the **Microsoft Foundry** service.
1. Right click the Foundry project that you created for this workshop and select **Open in Micorosft Foundry Extension**. This sets the project as the default project.
2. Open the **AI Toolkit** extension.
3. Expand **My Resources > Models > Microsoft Foundry**.
4. Confirm that your **gpt-4.1-mini** deployment is listed.



## Documentation
- [AI Toolkit](https://aka.ms/AIToolkit/doc)
- [Microsoft Agent Framework](https://learn.microsoft.com/agent-framework/)
- [Azure AI Evaluation SDK](https://learn.microsoft.com/azure/ai-foundry/how-to/develop/evaluate-sdk)
- [GitHub Copilot](https://code.visualstudio.com/docs/copilot/overview)
