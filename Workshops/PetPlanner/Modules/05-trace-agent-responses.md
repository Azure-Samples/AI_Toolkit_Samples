# 🐕 Module 5: Trace Agent Responses

Tracing reveals the decision path your agent takes — which helps debug and improve its reasoning when generating suggestions. Your goal is to enable tracing to understand how your Pet Planner processes information step-by-step.

## 🧩 Instructions

1. Open the GitHub Copilot chat window.
1. In the chat window, enter the **GitHub Copilot Prompt** provided below and submit.
1. Review the response from GitHub Copilot. Given the non-deterministic nature of language models, responses will vary.
1. If GitHub Copilot requests to open the **Tracing Viewer**, respond with **Yes** OR click the provided button to access the **Tracing Viewer**. Alternatively, you can open the **AI Toolkit** extension and navigate to **Agent and Workflow Tools > Tracing**.
1. In the **Tracing Viewer** confirm that the **Collector** has started (i.e. blue button under **Tracing**). If the **Collector** has not started, click **Start Collector**.
1. In the **Terminal**, run the command `python pet-planner-agent.py`.
1. View the traces in the **Tracing Viewer**.

## 💬 GitHub Copilot Prompt

`Enable local tracing in my Pet Planner agent.`

## 🔍 What’s Happening

Tracing logs the model’s chain of reasoning, API calls, and response generation steps — useful for transparency and optimization.

GitHub Copilot calls 1 tool:

- Get Tracing Code Generation Best Practices

## ✅ Checkpoint

You can now see a visual/textual trace of your Pet Planner’s thought process.

## 🐾 Next Step

Continue to [Evaluate Agent Responses](/Workshops/PetPlanner/Modules/06-evaluate-agent-responses.md)