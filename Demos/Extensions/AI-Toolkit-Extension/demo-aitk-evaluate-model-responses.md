# Evaluate Model Responses

**Duration**: 10 mins

This demo focuses on evaluating AI model responses using the [AI Toolkit](https://aka.ms/AITookit) extension for Visual Studio Code. It demonstrates how to set up and run evaluations, create custom evaluators, and analyze results. The demo leverages the GPT-4o model as a judge for evaluations and provides step-by-step instructions for configuring evaluators, importing datasets, and reviewing evaluation outcomes.

## Prerequisites

- [Visual Studio Code](https://code.visualstudio.com/)
- [AI Toolkit for Visual Studio Code](https://aka.ms/AIToolkit)
- [GitHub Fine-grained personal access token (PAT)](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token)

## Setup Instructions

This section takes you through the steps for showcasing how the AI Toolkit helps evaluate model outputs using built-in and custom evaluation tools. You’ll guide the audience through setting up evaluations, creating custom evaluators, and analyzing results—all within Visual Studio Code.

### Add the OpenAI GPT-4o model

The demo leverages the **GPT-4o** model as the model judge for evaluations. The model should be added to **My Models** before running the demo.

1. Open the **AI Toolkit** extension from the **Activity Bar**.
1. In the **Catalog** section, select **Models** to open the **Model Catalog**. Selecting **Models** opens the **Model Catalog** in a new editor tab.
1. In the **Model Catalog** search bar, enter **OpenAI GPT-4o**.
1. Click **+ Add** to add the model to your **My Models** list. Ensure that you've selected the model that's **Hosted by GitHub**.
1. In the **Activity Bar**, confirm that the **OpenAI GPT-4o** model appears in the list.

## Running the Demo

### Setup and run an evaluation

In this section, you’ll take the audience through how to set up and run a standard evaluation using built-in evaluators. This helps demonstrate how developers can assess the quality of model outputs using tools like Likert scoring, pass/fail thresholds, or retrieval accuracy—all without leaving VS Code.

1. Open the **AI Toolkit** extension from the **Activity Bar**.
1. In the **Tools** section, select **Evaluation**. Selecting the **Evaluation** tool opens it in a new editor tab.
1. In the **Overview** tab of the **Evaluation** editor, click the **+ New Evaluation** button. The extension will launch a setup wizard via the **Command Palette**.
1. Enter the name **demo-evaluation** and press **Enter**.
1. Select the following evaluators and click **OK**:
    1. Coherence
    1. Fluency
    1. Relevance
    1. Similarity
1. Select the **gpt-4o GitHub** model.
1. Select **Sample dataset**.
1. A notification will appear in the bottom-right corner confirming that the evaluation was successfully created. Click the **Open demo-evaluation** button in the notification to view the evaluation setup. (*Note*: Alternatively, you can view the evaluation setup by navigating to the **Evaluation** editor and selecting the evaluation from the **Overview** tab.)
1. In the **Evaluation** editor, click the **Run Evaluation** button to start the evaluation job. When the evaluation run is complete, the results will appear in the editor. (*Note*: When the evaluation is run, a notification will appear in the bottom-right corner indicating the status of the job.) Once the job is complete, a **View Results** button will appear in the notification. Click the **View Results** button to view the evaluation results. (*Note*: Alternatively, you can view the evaluation results by navigating to the **Evaluation** editor and selecting the evaluation from the **Overview** tab.)
1. Review the evaluation results.

### Create a custom evaluator

Now that the audience has seen how to run evaluations with built-in evaluators, this section introduces the power of custom evaluators. You’ll show how to create one from scratch by providing a name, description, evaluation type, and prompt—enabling tailored assessment criteria for specific scenarios. The custom evaluator will be used to assess the model's "Call to Action" for social posts.

1. In the **Evaluation** editor, select the **Evaluators** tab. (*Note*: Alternatively, if you're starting in the evaluation results view, you can click the **<** button in the Editor)
1. In the **Evaluators** tab, click the **+ Create Evaluator** button.
1. Enter the following for the custom evaluator:
    1. Name - `Call to Action Quality`
    1. Description - `Assess how clear, relevant, and motivating the call to action is in responses.`
    1. Type - LLM-based
    1. Prompt - Copy + paste the prompt within the `cta-evaluator.md` file.
1. Click **Save**.

### Setup and run an evaluation with a custom evaluator

In this final section, you’ll demonstrate how to use the custom evaluator created in the previous step. This includes importing a dataset, mapping the relevant columns, and launching the evaluation—giving the audience a complete look at how to run bespoke model assessments inside the toolkit.

1. In the **Evaluation** editor, select the **Overview** tab and click the **+ New Evaluation** button.
1. In the setup wizard, enter the name **cta-evaluation** and press **Enter**.
1. Select the **Call to Action Quality** evaluator and click **OK**.
1. Select the **gpt-4o GitHub** model.
1. Select **Import dataset**.
1. In the file explorer, select the **cta-evaluation-data.jsonl** file.
1. A notification will appear in the bottom-right corner confirming that the evaluation was successfully created. Click the **Open cta-evaluation** button in the notification to view the evaluation setup. (*Note*: Alternatively, you can view the evaluation setup by navigating to the **Evaluation** editor and selecting the evaluation from the **Overview** tab.)
1. In the **Evaluation** editor, validate that the **query** and **response** column mappings are accurate.
1. Click the **Run Evaluation** button to start the evaluation job.
1. Review the evaluation results.

## Clean-up
1. In the **AI Toolkit** panel (Side Bar), in the **Tools** section, select **Evaluation**.
1. In the **Overview** tab of the **Evaluation** editor, check the boxes next to the **demo-evaluation** and **cta-evaluation** evaluation runs and click the **Delete** button.