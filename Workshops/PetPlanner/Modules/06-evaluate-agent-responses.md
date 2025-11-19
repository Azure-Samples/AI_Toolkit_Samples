# 🐕 Module 6: Evaluate Agent Responses

Evaluating responses ensures your agent meets expectations — helpful, playful, and reliable — while handling edge cases gracefully. Your goal is to assess your Pet Planner’s performance.

> [!WARNING]
>Do not stop the debugger. The debugger should remain running for the rest of this workshop. If the debugger is stopped, the Pet Planner MCP server will no longer run locally which prevents server access for the agent.

## 🧩 Instructions

1. Open the **pet-planner-agent.py** file so that GitHub Copilot can use the agent file as context.
1. Open the GitHub Copilot chat window via the **Toggle Chat** icon.
1. Click the **Set Mode** drop-down and select **Agent**.
1. Click the **Pick Model** drop-down and select **Claude Sonnet 4.5**.
1. In the chat window, enter the **GitHub Copilot Prompt** provided below and submit.
1. Review the response from GitHub Copilot. Given the non-deterministic nature of language models, responses will vary.
1. If GitHub Copilot requests that you confirm the recommended evaluators for evaluation, respond: `Only relevance and coherence`.
1. If GitHub Copilot inquiries whether to create a dataset with queries, respond: `Yes, only create 3 rows of data.`.
1. If GitHub Copilot inquiries whether to create a dataset with responses, respond: `Yes, collect responses.`.
1. You may be prompted to allow GitHub Copilot to run the **pet-planner-agent.py** file to collect responses. If prompted, select **Allow**. GitHub Copilot may occasionally run a command that results in an error. If that occurs, GitHub Copilot will likely resolve the error on its own. However, you will be re-prompted for permission each time GitHub Copilot would like to run the **pet-planner-agent.py** file.
1. After GitHub Copilot completes it's task of creating a test dataset, you'll be prompted to confirm the evaluation plan. Review and either respond `yes` or respond with your requested changes.
1. While GitHub Copilot creates the evaluation file, you may also be prompted to allow GitHub Copilot to install any required dependencies. As a precaution, review the request before selecting **Allow**. Selecting **Allow** enables GitHub Copilot to install dependencies on your behalf. In addition, it's recommended to follow up with an additional prompt such as `install in the uv virtual environment` rather than selecting **Allow**. Otherwise, GitHub Copilot may create it's own virtual environment.
1. After GitHub Copilot creates the evaluation file, you may be prompted to allow GitHub Copilot to run the evaluation file. If you'd prefer to run the file yourself, select **Skip**, otherwise select **Allow**.
1. Review the evaluation results in the terminal. Alternatively, open the evaluation results JSON file (e.g. `evaluation_results.json` although yours may be named differently) and open the **Command Palette** (CTRL+SHIFT+P). Type `Format Document` to format the JSON file for a better view of the file's content. As a bonus, you can prompt GitHub Copilot to `create a markdown report of the evaluation results`.
1. If evaluation setup is successful, select **Keep** in GitHub Copilot to keep the file changes. Evaluation setup is successful if the following conditions are met (**note**: example images are provided below):
    1. The evaluation file created by GitHub Copilot leverages the **Azure AI Evaluation SDK**, the SDK's built-in **relevance** and **coherence** evaluators, and your Microsoft Foundry model deployment and endpoint.
    1. There are 3 completed lines per evaluator in the terminal output.
    1. The relevance evaluator has a numeric value for each row of data.
    1. The coherence evaluator has a numeric value for each row of data.

![A screenshot of the terminal output for an evaluation run. There are 3 completed lines for both the relevance and coherence evaluators.](../Images/evaluation-status.png)

![A screenshot of the evaluation summary for a successful evaluation run.](../Images/evaluation-summary.png)

## 💬 GitHub Copilot Prompt

`Add evaluation to my agent.`

## 🔍 What’s Happening

Copilot compares your agent’s responses against best practices and performance criteria, surfacing improvements in tone, relevance, or correctness.

GitHub Copilot calls 2 tools:

- Evaluation Planner
- Get Evaluation Agent Runner Best Practices
- Get Evaluation Code Generation Best Practices
- Get AI Model Guidance

## 🧐 Troubleshooting

If the evaluation file created by GitHub Copilot produces an error, try resolving by referencing the [Azure AI Evaluation Local Evaluation](https://learn.microsoft.com/azure/ai-foundry/how-to/develop/evaluate-sdk#conversation-support-for-text) documentation. Provided below are a few common things to check:

- Confirm that GitHub Copilot uses the **Azure AI Evaluation SDK**. This can be confirmed via the import statement. You should see something similar to: `from azure.ai.evaluation import evaluate, RelevanceEvaluator, CoherenceEvaluator, AzureOpenAIModelConfiguration
`.
- Confirm that the `model_config` variable is an instance of the `AzureOpenAIModelConfiguration` class. If the class isn't currently imported, add it to the `azure.ai.evaluation` import statement, and then update the `model_config` variable to instantiate the class.
- Confirm that the `azure-deployment` value within the `model_config` is `gpt-4.1-mini`.
- Confirm that the `azure_endpoint` value within the `model_config` is the same as the **Target URI** for your model deployment. You can confirm this by viewing the model deployment information in the Microsoft Foundry portal.
- Confirm that the `api_version` value within the `model_config` is the same as the version provided in the **Target URI** for your model deployment (note: it's at the end of the **Target URI**).

## ✅ Checkpoint

You now have synthetic data ready to evaluate your Pet Planner’s responses. You should also have an evaluation script that runs the recommended evaluators, and results from your latest evaluation run.

## 🐾 Workshop Complete

🎉 You’ve built, connected, and optimized your Pet Planner agent — ready to sniff out the perfect playdate!
