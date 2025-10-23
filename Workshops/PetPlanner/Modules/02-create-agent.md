# 🐕 Module 2: Create an Agent

Agents connect your model with logic and personality. They define how your AI interacts with users — giving it purpose, style, and reasoning. In this step, you’ll define the Pet Planner’s behavior: how it chats, fetches pet-friendly data, and offers playful suggestions to make every pet outing purr-fect!

## 🧩 Instructions

1. In the **AI Toolkit** extension, navigate to **Agent and Workflow Tools > Agent Builder**.
1. In the **Agent Builder**, for the **Agent Name** enter: `Pet Planner`
1. For the **Model** drop-down, select **gpt-4.1-mini Remote via Azure AI Foundry**.
1. For the **Instructions**, enter the **Agent System Prompt** provided below.
1. On the right, in the **Playground**, enter the following prompt: `My labrador and I are in San Francisco. Recommend something fun to do.`
1. Review the model's output and submit 2-3 more prompts to continue observing the agent's behavior.

## ⚙️ Agent System Prompt

`You are a warm, pet-loving assistant that helps users plan safe and fun breed playdates. Always start by asking about the pet’s type, size, age, temperament, and the playdate preferences, then factor in weather, activity ideas, and location recommendations. Prioritize safety, give practical tips, and keep the conversation engaging, friendly, and personalized with follow-up questions.`

## 🔍 What’s Happening

You’re designing the brain and personality behind your Pet Planner. This is where you decide how it speaks, how it reacts, and what kind of tasks it can handle — from checking the weather to suggesting pet-friendly activities.

## ✅ Checkpoint

You should now have an agent that defines how the Pet Planner behaves — ready to interact with your chosen model.

## 🐾 Next Step

Continue to [Connect an MCP Server](/Workshops/PetPlanner/Modules/03-connect-mcp-server.md)