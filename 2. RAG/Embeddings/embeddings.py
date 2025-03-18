import spacy
import pandas as pd

# Load a spaCy language model
#instead of OpenAI Text-embedding-ada-002
nlp = spacy.load("en_core_web_md")  #python -m spacy download en_core_web_md. 

with open("paragraph.txt", "r", encoding="utf-8") as file:
    paragraph = file.read()

# Process the paragraph using spaCy
doc = nlp(paragraph)

# store vector representations
vectors = []

# Iterate through the words in the paragraph and append their vectors to the list
for token in doc:
    vectors.append(token.vector)

# Create a DataFrame to store the vectors
df = pd.DataFrame(vectors)

# Save the vectors to a CSV file
df.to_csv('embeddings.csv', index=False)

'''

# paragraph = """
AI Toolkit for Visual Studio Code is an extension to help developers and AI engineers to easily build AI apps and agents through developing and testing with generative AI models locally or in the cloud.
AI Toolkit supports most genAI models on the market.

AI engineers can use AI Toolkit to discover and try popular AI models easily. 

The playground supports attachments, web search and thinking mode allowing for more interactive experimentation.
They can run multiple prompts in batch mode and evaluate the prompts in a dataset to AI models using popular evaluators.
Additionally, AI engineers can fine-tune and deploy AI models

'''