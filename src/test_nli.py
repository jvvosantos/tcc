from transformers import pipeline

# Load an NLI pipeline
nli = pipeline("text-classification", model="roberta-large-mnli")

# Example requirement pair
premise = "The system should respond quickly."
hypothesis = "This requirement contains vague or unclear terms that can be interpreted in multiple ways."

# Run inference
result = nli({"text": premise, "text_pair": hypothesis})
print(result)