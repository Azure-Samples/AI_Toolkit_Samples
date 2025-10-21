# 🐕 Module 6: Evaluate Agent Responses

Evaluating responses ensures your agent meets expectations — helpful, playful, and reliable — while handling edge cases gracefully. Your goal is to Assess your Pet Planner’s performance.

## 🧩 Instructions

1. Open the GitHub Copilot chat window.
1. In the chat window, enter the **GitHub Copilot Prompt** provided below and submit.
1. Review the response from GitHub Copilot. Given the non-deterministic nature of language models, responses will vary.
1. If GitHub Copilot inquiries whether to create a dataset with queries and responses, respond: `Yes, only create 3 rows of data`.
1. After GitHub Copilot completes it's task of creating a test dataset and the evaluation file, run the evaluation file in the terminal.
1. Review the evaluation results.

## 💬 GitHub Copilot Prompt

Add evaluation to my agent using the Azure AI Evaluation SDK.

## 🔍 What’s Happening

Copilot compares your agent’s responses against best practices and performance criteria, surfacing improvements in tone, relevance, or correctness.

GitHub Copilot calls 2 tools:

- Evaluation Planner
- Get Evaluation Agent Runner Best Practices
- Get Evaluation Code Generation Best Practices
- Get AI Model Guidance

## ✅ Checkpoint

You now have synthetic data ready to evaluate your Pet Planner’s responses. You should also have an evaluation script that runs the recommended evaluators, and results from your latest evaluation run.

## 🐾 Workshop Complete

🎉 You’ve built, connected, and optimized your Pet Planner agent — ready to sniff out the perfect playdate!