from transformers import pipeline
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

req = "The system shall allow users to reset their password."
labels = ["functional requirement", "non-functional requirement"]
result = classifier(req, labels)
print(result)

# DSR desenhar o experimento