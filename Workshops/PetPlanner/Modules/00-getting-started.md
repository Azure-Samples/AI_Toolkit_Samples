# Getting Started - PetPlanner Workshop

Welcome to the PetPlanner Workshop! This guide will walk you through all the setup steps needed to complete this workshop.

## Prerequisites

### Required Accounts
<!-- Add account setup requirements here -->
- [Azure](https://signup.azure.com/) subscription
- [GitHub](https://www.github.com) with a [GitHub Copilot](https://github.com/github-copilot/signup) subscription

## Environment Setup

### 1. Python Environment
- [Python 3.10](https://www.python.org/downloads/) (or higher)
- [uv](https://docs.astral.sh/uv/#installation) - A fast Python package installer and resolver (alternative to pip)

### 2. Azure
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli-windows?view=azure-cli-latest&pivots=winget) - Used for Azure authentication and resource management

### 3. Development Tools
- [Visual Studio Code](https://code.visualstudio.com/download)
  - [AI Toolkit](https://aka.ms/AIToolkit) extension
  - [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) extension
  - [Azure Resources](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azureresourcegroups) extension

## GitHub Universe (Admin Only)

The following steps are to be completed by the admins for the GitHub Universe workshop. Complete the following steps after launching the Skillable environment.

### Sign-in to the GitHub Enterprise Account

1. In the Skillable browser, login to the GitHub Enterprise account. When prompted, choose to stay signed-in.
1. In Visual Studio Code, click the **GitHub Copilot** icon (lower right) and select **Setup Copilot**.
1. On the **Sign in to use GitHub Copilot** screen, select **Continue with GitHub**. A new browser window will open. For **Select user to authorize Visual Studio Code**, click **Continue** for the **GitHub Universe Enterprise** account.
1. For **Authorize Visual Studio Code**, select **Authorize Visual-Studio-Code**.
1. For **This site is trying to open Visual Studio Code**, select **Open**.

### Confirm Access to GitHub Models with GitHub Copilot

1. Back in Visual Studio Code, click the **Toggle Chat** icon to open **GitHub Copilot**.
1. In the **Pick Model** drop-down, confirm the availability of **Claude Sonnet 4** and **Claude Sonnet 4.5**.
1. Set the model to **Claude Sonnet 4.5**.

### Confirm Version of the AI Toolkit

1. Open the **Extensions** and select **AI Toolkit**.
1. Confirm that version **0.24.1** is installed OR click **Restart extensions** to get the latest extension update.

### Sign-In to Azure

1. Open the **Azure Resources** extension (i.e. Azure icon).
1. Select **Sign in to Azure…**.
1. For **The extension 'Azure Resources' wants to sign in using Microsoft**, select **Allow**.
1. For the sign-in screen, go to the **Resources** tab in Skillable and click the value for **Username**.
1. For **Enter Temporary Access Pass**, click  the value for **TAP**.
1. Click **Sign in**.
1. For the **Automatically sign in to all desktop apps and websites on this device?** click **Yes, all apps**.
1. For **Account added to this device**, click **Done**.

### Set the Default Foundry Project in Visual Studio Code

1. In Visual Studio Code, in the **Azure Resources** extension, expand the **GHU25** resource and expand the **Azure AI Foundry** service.
1. Right click the listed project and select **Open in Azure AI Foundry Extension**. This sets the project as the default project.
1. In the **Azure AI Foundry** extension, within the **Resources** section, expand the **project > Models** to confirm that **gpt-4.1-mini** is listed.
1. In the **AI Toolkit** extension, within **My Resources**, expand **Models > Azure AI Foundry** to confirm **gpt-4.1-mini** is listed.

### Open Browser Tabs

1. In the browser, open: [Pet Planner MCP Server](https://github.com/Azure-Samples/AI_Toolkit_Samples/blob/main/Workshops/PetPlanner/pet-planner-server.py">AI_Toolkit_Samples/Workshops/PetPlanner/pet-planner-server.py)
1. In the browser, navigate to the [Azure](https://portal.azure.com) portal.
1. In the **Azure** portal, search for **resource groups**. Select the **ResourceGroup1** resource.
1. In the resource group, select the **Azure AI Foundry** resource (note: starts with **ghu**).
1. In the **Azure AI Foundry** resource, click the **Go to Azure AI Foundry portal** button.
1. In the **Azure AI Foundry** portal, navigate to **My Assets > Models + endpoints**.
1. Select the **gpt-4.1-mini** model.

### Clean-Up

1. Select the **Pet Planner MCP Server** browser tab so that it's the first tab attendees will see when they maximize the browser.
1. Keep the **Azure AI Foundry** portal tab open in the background.
1. Close all other tabs (i.e. **Azure** portal, all GitHub Enterprise account log-in pages, etc.)
1. Minimize the browser.
1. Maximize the **Visual Studio Code** window.

## Documentation
- [AI Toolkit](https://aka.ms/AIToolkit/doc)
- [Microsoft Agent Framework](https://learn.microsoft.com/agent-framework/)
- [Azure AI Evaluation SDK](https://learn.microsoft.com/azure/ai-foundry/how-to/develop/evaluate-sdk)
- [GitHub Copilot](https://code.visualstudio.com/docs/copilot/overview)