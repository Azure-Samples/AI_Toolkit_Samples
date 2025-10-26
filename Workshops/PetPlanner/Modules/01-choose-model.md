# 🐕 Module 1: Choose a Model

The model determines how your agent thinks and responds. You’ll choose a model that can understand natural language, fetch data, and generate friendly pet playdate recommendations. Your goal is to select and configure the right model for your Pet Planner agent!

## 🧩 Instructions

1. Open a new GitHub Copilot chat window via the **Toggle Chat** icon.
1. Click the **Set Mode** drop-down and select **Agent**.
1. Click the **Pick Model** drop-down and select **Claude Sonnet 4.5**.
1. In the chat window, enter the **GitHub Copilot Prompt** provided below and submit.
1. Review the response from GitHub Copilot. Given the non-deterministic nature of language models, responses will vary.
1. If GitHub Copilot requests to open the **Model Catalog**, respond with **Yes** OR click the provided button to access the **Model Catalog**. Alternatively, you can open the **AI Toolkit** extension and navigate to **Model Tools > Model Catalog**.
1. In the **Model Catalog** select the **Hosted by** drop-down and select **GitHub**.
1. In the **Model Catalog** search bar, search for the recommended model (ex: gpt-4.1-mini). Once the model is found, click **Try in Playground**.
1. If prompted to sign-in to GitHub, select **Allow**. For **Select user to authorize** click **Continue** next to the username. Next, for **Visual Studio Code is requesting additional permissions**, select **Authorize Visual-Studio-Code**. After sign-in is complete, select **Open** to open Visual Studio Code.
1. In the **Playground**, in **Model Preferences**, confirm that **OpenAI gpt-4.1-mini (via GitHub)** is selected.
1. For the **System prompt**, enter the **Agent System Prompt** provided below.
1. In the chat window, enter the prompt: `It's raining today. What should my dog and I do?`
1. Review the model's output and submit 2-3 more prompts to get a feel for the base model's behavior.

## 💬 GitHub Copilot Prompt

`I want to build a Pet Planner agent. Its job is to help pet owners sniff out the perfect playdate by: (1) checking the weather, (2) fetching fun activity ideas, and (3) pointing to the best spot in town. Which language model(s) would you recommend for this scenario, and why? Explain the trade-offs between models (e.g., reasoning ability, cost, latency, context length) so that I can make an informed choice.`

## ⚙️ Agent System Prompt

`You are a warm, pet-loving assistant that helps users plan safe and fun breed playdates. Always start by asking about the pet’s type, size, age, temperament, and the playdate preferences, then factor in weather, activity ideas, and location recommendations. Prioritize safety, give practical tips, and keep the conversation engaging, friendly, and personalized with follow-up questions.`

## 🔍 What’s Happening

GitHub Copilot calls 1 tool:

- Get AI Model Guidance

> [!NOTE]
>If GitHub Copilot doesn't invoke the AI Toolkit tools when generating it's response, you can enter `#aitk` in the chat window to explicitly select which tool(s) you'd like GitHub Copilot to use prior to submitting your prompt.

## ✅ Checkpoint

You should now have a model recommendation for your agent and a deployed Azure AI Foundry version of the model.

## 🐾 Next Step

Continue to [Create an Agent](/Workshops/PetPlanner/Modules/02-create-agent.md)