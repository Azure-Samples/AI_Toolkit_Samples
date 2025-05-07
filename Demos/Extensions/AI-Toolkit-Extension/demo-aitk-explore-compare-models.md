# Explore and Compare Models

**Duration**: 5 mins

This demo guides users through exploring, deploying, and comparing AI models using the [AI Toolkit](https://aka.ms/AITookit) extension for Visual Studio Code. It includes instructions for browsing the Model Catalog, chatting with models hosted by GitHub models, adding local models via Ollama, comparing responses from different models, and generating sample code to programmatically interact with models.

## Prerequisites

- [Visual Studio Code](https://code.visualstudio.com/)
- [AI Toolkit for Visual Studio Code](https://aka.ms/AIToolkit)
- [GitHub Fine-grained personal access token (PAT)](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token)
- [Ollama](https://ollama.com/) (with a minimum of 1 model pulled to your local Ollama library - i.e. Qwen, Gemma 3, Llama, etc.)

## Setup Instructions

1. Create and activate a virtual environment for your workspace.
1. Run `pip install -r requirements.txt` to install dependencies.
1. Add your [GitHub PAT](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token) to the `.env` file. The PAT is required for making an inference call using the GPT-4o model hosted by GitHub Models in the **Generate and run sample code** section of the demo.

## Running the Demo

This demo showcases how to use the AI Toolkit extension for Visual Studio Code to explore, test, and integrate language models—both cloud-hosted and local—into a content creation workflow.

### Browse models and view model cards

In this section, you’ll introduce the audience to the Model Catalog within the AI Toolkit. You’ll show how to filter models by publisher and open a model card to learn more about a specific model’s capabilities, use cases, and configuration options.

1. Open the **AI Toolkit** extension from the **Activity Bar**.
1. In the **Catalog** section, select **Models** to open the **Model Catalog**. Selecting **Models** opens the **Model Catalog** in a new editor tab. Scroll through the **Model Catalog** to view the available models.
1. In the **Model Catalog**, use the **Publisher** filter and select **OpenAI**.
1. Select the **OpenAI GPT-4o** model name to view it's model card. The model card will open in a markdown file. View the contents of the model card.

### Add and chat with a model

Now that your audience has seen how to find a model, it’s time to show them how to interact with one. In this section, you’ll demonstrate how to add a model to the Playground, add custom context instructions, upload a file as context, and start a conversation with the model.

1. Go back to the **Model Catalog** tab and select **Try in Playground** for the **OpenAI GPT-4o** model. The model will add to **My Models** and the **Playground** opens in a new editor tab.
1. In the **Playground**, go to the **Model Preferences** section and make sure **OpenAI GPT-4o (via GitHub)** is selected in the **Model** field.
1. In the **Model Preferences** section, locate the **Context instructions** field and enter the following: `You are a skilled content creator who specializes in crafting engaging, clear, and audience-appropriate written material across formats like blogs, newsletters, social media posts, and video scripts. You adapt your tone based on the platform and purpose—whether it’s professional, conversational, playful, or educational. Always aim to make the content actionable, concise, and aligned with the intended audience's interests. When asked, you may suggest headlines, outlines, or rewrites to improve flow and clarity.`
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

### Add and chat with a local model

This section is all about showing that you’re not limited to hosted models. Here, you’ll take the audience through adding a local model via Ollama, launching it in the Playground, and sending it a test prompt—highlighting flexibility and offline use cases.

1. In the **AI Toolkit** panel (Side Bar), go to the **My Models** section, then hover over **My Models** and click the **+** icon that appears. The extension will launch a setup wizard via the **Command Palette**.
1. Select **Add Ollama Model** followed by **Select models from Ollama library**.
1. Select your preferred model from the **Ollama models library**,then click **OK**.
1. A notification will appear in the bottom-right corner confirming that the model was successfully added. Click the **Model Playground** button in the notification to test the model in the **Model Playground**. (*Note*: Alternatively, you can navigate to the **Model Playground** by selecting **Playground** under the **Tools** section in the AI Toolkit side bar.)
1. In the **Playground** tab, go to the **Model Preferences** section and make sure that the Ollama model is selected in the **Model** field. The model will reflect **(Local via Ollama)** at the end of its name. (*Note*: If the prior context instructions are not retained, re-add the context instructions for this demo.)
1. In the **chat window**, type the following into the chat input and press **Enter**: `I’m launching a newsletter for tech professionals interested in AI. Write a short introductory paragraph that sets the tone for a weekly email that’s equal parts informative, inspiring, and practical.` (*Note*: Generation speed will vary as it's dependent on your hardware.)
1. Review the model's response.

### Compare model response for 2 models

After showing how to chat with individual models, this section demonstrates the **Compare** feature. You’ll show the audience how to run the same prompt against two models side-by-side, making it easy to evaluate output differences in real time.

1. At the top of the playground, click **Compare** and select the **OpenAI GPT-4o via GitHub** model to compare model output. The **Playground** will display two chat windows.
1. You only need to type your prompt into one chat window—your input will automatically appear in both. In either **chat window**, enter the following into the input field and press **Enter**: `Write a brief intro for a weekly AI newsletter aimed at busy tech professionals. It should feel smart, helpful, and motivating.`
1. Review the output from the models.

### Generate and run sample code

In this final section, you’ll show how the AI Toolkit can help developers go from prototype to production. You’ll demonstrate how to auto-generate a code snippet for calling the model, customize it with your own prompt, and run it—all from within VS Code.

1. In the **OpenAI GPT-4o (via GitHub)** chat window, click the **Select this model** button.
1. At the top right of the **Playground**, click **</> View Code** to generate a code file to use the model programmatically.
1. The extension will launch a setup wizard via the **Command Palette**. Select **OpenAI SDK** for the client SDK. A new python file will open with the code.
1. Save the file (Ctrl+Shift+S) with the file name `aitk-inference-demo.py`.
1. In the `aitk-inference-demo.py` file, add the following after the import statements:
    ```python
    from dotenv import load_dotenv
    load_dotenv(override=True)
    ```
1. In the `aitk-inference-demo.py` file, change the `text` string value to `Suggest a headline and opening line for a blog post about how AI is changing developer workflows.`.
1. Save (Ctrl+S) and run the file.
1. Remove the output from the model.

## Clean-up
1. In the **AI Toolkit** panel (Side Bar), go to the **My Models** section.
1. Right-click the **OpenAI GPT-4o** model and select **Delete**.
1. Right-click your loaded **Ollama** model and select **Delete**.
1. In the **Explorer** panel, delete the `aitk-inference-demo.py` file.