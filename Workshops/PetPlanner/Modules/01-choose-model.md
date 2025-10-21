# 🐕 Module 1: Choose a Model

The model determines how your agent thinks and responds. You’ll choose a model that can understand natural language, fetch data, and generate friendly pet playdate recommendations. Your goal is to select and configure the right model for your Pet Planner agent!

## 🧩 Instructions

1. Open a new GitHub Copilot chat window via the **Toggle Chat** icon.
1. Click the **Select Mode** drop-down and select **Agent**.
1. Click the **Pick Model** drop-down and select **Claude Sonnet 4**.
1. In the chat window, enter the **GitHub Copilot Prompt** provided below and submit.
1. Review the response from GitHub Copilot. Given the non-deterministic nature of language models, responses will vary.
1. If GitHub Copilot requests to open the **Model Catalog**, respond with **Yes** OR click the provided button to access the **Model Catalog**. Alternatively, you can open the **AI Toolkit** extension and navigate to **Model Tools > Model Catalog**.
1. In the **Model Catalog** select the **Hosted by** drop-down and select **GitHub**.
1. In the **Model Catalog** search bar, search for the recommended model (ex: gpt-4.1-mini). Once the model is found, click **Try in Playground**.
1. In the **Playground**, in **Model Preferences**, confirm that **OpenAI gpt-4.1-mini (via GitHub)** is selected.
1. In the chat window, enter the prompt: `It's raining today. What should my dog and I do?`
1. Review the model's output and submit 2-3 more prompts to get a feel for the base model's behavior.

## 💬 GitHub Copilot Prompt

I want to build a Pet Planner agent. Its job is to help pet owners sniff out the perfect playdate by: (1) checking the weather, (2) fetching fun activity ideas, and (3) pointing to the best spot in town. Which language model(s) would you recommend for this scenario, and why? Explain the trade-offs between models (e.g., reasoning ability, cost, latency, context length) so that I can make an informed choice.

## 🔍 What’s Happening

GitHub Copilot calls 2 tools:

- Get AI Model Guidance
- Get Agent Code Generation Best Practices

## ✅ Checkpoint

You should now have a model recommendation for your agent and have deployed the model.

## 🐾 Next Step

Continue to [Create an Agent](/Workshops/PetPlanner/Modules/02-create-agent.md)