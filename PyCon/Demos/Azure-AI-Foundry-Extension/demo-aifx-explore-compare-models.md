# Explore and Compare Models

**Duration**: 5 mins

This demo showcases how to explore, deploy, and interact with AI models using the [Azure AI Foundry](https://marketplace.visualstudio.com/items?itemName=TeamsDevApp.vscode-ai-foundry) extension and the [AI Toolkit](https://aka.ms/AITookit) extension for Visual Studio Code. It provides step-by-step instructions for setting up the environment, browsing the model catalog, deploying models to Azure, and using the Playground to chat with models. The demo also covers comparing model responses, generating sample code for programmatic interaction, and managing model deployments, offering a comprehensive guide for leveraging Azure AI Foundry in AI development workflows.

## Prerequisites

- [Visual Studio Code](https://code.visualstudio.com/)
- [Azure AI Foundry extension](https://marketplace.visualstudio.com/items?itemName=TeamsDevApp.vscode-ai-foundry)
- [AI Toolkit for Visual Studio Code](https://aka.ms/AIToolkit)
- [An existing Azure AI Foundry project](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/create-projects?tabs=ai-studio) with a `o4-mini` deployment (note: The extension interacts with Azure AI Foundry at the project level.)

## Setup Instructions

### Setup environment and install dependencies

1. Create a virtual environment for your workspace.
1. Run `pip install -r requirements.txt` to install dependencies.
1. Add your **AZURE_INFERENCE_SDK_KEY** to the `.env` file. This key is available on the **Overview** page of your Azure AI Foundry project.

### Set your default project

The Azure AI Foundry extension interacts with Azure AI Foundry at the project level. Before running the demo, you'll need to sign-in to Azure and select your default project.

1. In Visual Studio Code, select the Azure icon from the **Activity Bar**.
1. In the **Resources** section, select **Sign in to Azure...**. You'll be prompted to sign-in.
1. Once you're signed-in, navigate to the **Resources** section and select your **Azure Subscription** followed by your **Resource Group**.
1. Select **Azure AI Foundry**
1. Right-click your project and select **Open in Azure AI Foundry Extension**.

## Running the Demo

In this demo, you’ll showcase how to discover, deploy, and interact with language models using the Azure AI Foundry extension. You'll cover the full lifecycle—from model browsing to code generation—using the built-in tools within Visual Studio Code.

### Browse models in the Model Catalog

Begin by introducing your audience to the Model Catalog, a centralized place for discovering models across different publishers and tasks. This section shows how to browse available models and apply filters to find the right one for your needs.

1. Open the **Azure AI Foundry** extension from the **Activity Bar**.
1. In the **Tools** section, select **Model Catalog** to open the **Model Catalog** in a new editor tab. Scroll through the **Model Catalog** to view the available models.
1. Apply the filters to filter the models by either **Publisher** or **Task**.

### Deploy and chat with a model

Now that your audience has seen where to find models, you’ll demonstrate how to deploy a model into your Azure project using the built-in wizard. After deployment, you’ll switch to the Model Playground to run a chat session, showing how developers can test responses interactively with custom prompts and file uploads.

1. In the **Model Catalog**, search for **gpt-4o** and select the **Deploy in Azure** link for the **gpt-4o** model. The extension will launch a setup wizard via the **Command Palette**.
1. Select your **AI service**.
1. Select your preferred **model version**.
1. Select your preferred **deployment type**.
1. Enter the following **name** for the model and press **Enter**: `gpt-4o`
1. A confirmation dialog box will appear. Click the **Deploy** button to deploy the model to your project.
1. In the left **Activity Bar**, navigate to the **Tools** section, and click **Model Playground**. The extension will launch a setup wizard via the **Command Palette**.
1. Select the **gpt-4o** model. The **Playground** will then open in a new editor tab.
1. In the **Playground**, go to the **Model Preferences** section and make sure **gpt-4o_AIFoundry (via Custom)** is selected in the **Model** field.
1. In the **Model Preferences** section, locate the **Context instructions** field and enter the following: `You are a skilled content creator who specializes in crafting engaging, clear, and audience-appropriate written material across formats like blogs, newsletters, social media posts, and video scripts. You adapt your tone based on the platform and purpose—whether it’s professional, conversational, playful, or educational. Always aim to make the content actionable, concise, and aligned with the intended audience's interests. When asked, you may suggest headlines, outlines, or rewrites to improve flow and clarity.`
1. Review the model's response.
1. In the **chat window**, type the following into the chat input and press **Enter** : `I’m launching a newsletter for tech professionals interested in AI. Write a short introductory paragraph that sets the tone for a weekly email that’s equal parts informative, inspiring, and practical.`
1. Review the model's response.
1. In the chat input, select the **Search File** icon (paperclip) and upload the `brand-style-guide.docx` file.
1. In the **chat window**, type the following into the chat input and press **Enter** :
    ```
    Does this paragraph follow the uploaded style guide? If not, what should I change?

    In today's competitive landscape, businesses must leverage AI or risk falling behind.
    Artificial intelligence offers myriad possibilities for optimizing workflows and scaling operations.
    Reach out today to explore how your organization can begin this transformative journey.
    ```
1. Review the model's response.

## Chat with an existing model deployment

To show flexibility with existing resources, this section demonstrates how to view model deployment information for an existing deployed model directly from the Resources panel. You’ll take the audience through interacting with that model in the Playground, just like with a fresh deployment—without repeating the setup process.

1. In the left **Activity Bar**, navigate to the **Resources** section.
1. Within the **Models** subsection, right-click the **o4-mini** model and select **Open in Playground**. The **Playground** will then open in a new editor tab.
1. In the **Playground**, go to the **Model Preferences** section and make sure **o4-mini_AIFoundry (via Custom)** is selected in the **Model** field.
1. In the **Model Preferences** section, locate the **Context instructions** field and enter the following: `You are a skilled content creator who specializes in crafting engaging, clear, and audience-appropriate written material across formats like blogs, newsletters, social media posts, and video scripts. You adapt your tone based on the platform and purpose—whether it’s professional, conversational, playful, or educational. Always aim to make the content actionable, concise, and aligned with the intended audience's interests. When asked, you may suggest headlines, outlines, or rewrites to improve flow and clarity.`
1. In the **chat window**, type the following into the chat input and press **Enter** : `I’m launching a newsletter for tech professionals interested in AI. Write a short introductory paragraph that sets the tone for a weekly email that’s equal parts informative, inspiring, and practical.`
1. Review the model's response.

### Compare model response for 2 models

In this section, you’ll highlight how multiple models can be compared side-by-side in the Playground. This is useful when teams are evaluating model quality, fine-tuning decisions, or vendor/model selection. You’ll enter a single prompt and show how the outputs differ in real time.

1. At the top of the playground, click **Compare** and select the **gpt-4o_AIFoundry (via Custom)** model to compare model output. The **Playground** will display two chat windows.
1. You only need to type your prompt into one chat window—your input will automatically appear in both. In either **chat window**, enter the following into the input field and press **Enter**: `Write a brief intro for a weekly AI newsletter aimed at busy tech professionals. It should feel smart, helpful, and motivating.`
1. Review the output from the models.

### Generate and run sample code

Finally, you’ll show the audience how to generate and run inference code programmatically. This section shows how to export model usage as a Python script using the Azure AI client SDK—bridging the gap between experimentation and integration in an app or workflow.

1. In the left **Activity Bar**, navigate to the **Resources** section
1. Within the **Models** subsection, right-click the **gpt-4o** model and select **Open Code File**. The extension will launch a setup wizard via the **Command Palette**.
1. Select **Azure AI model inference client library** for the **SDK**.
1. Select **Python** for **language**.
1. Select **Key Authentication** for the **auth method**.
1. A new python file will open with the code.
1. Save the file (Ctrl+Shift+S) with the file name `aifx-inference-demo.py`.
1. In the `aifx-inference-demo.py` file, add the following after the import statements:
    ```
    from dotenv import load_dotenv
    load_dotenv()
    ```
1. In the `aifx-inference-demo.py` file, change the value for the `key` variable to `os.getenv("AZURE_INFERENCE_SDK_KEY")`.
1. Save (Ctrl+S) and run the file. (*Note*: You can modify the `print` statement to only output the model's response. To do so, replace `print(response)` with `print(response.choices[0].message.content)`)
1. Review the output from the model.

## Clean-up
1. In the **Azure AI Foundry** panel (Side Bar), go to the **Resources** section.
1. Within the **Models** subsection, right-click the **gpt-4o** model and select **Delete**.
1. In the **Explorer** panel, delete the **afx-inference-demo.py** file.