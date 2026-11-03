
from google import genai
from config import gemini_api_key

client = genai.Client(api_key=gemini_api_key)

print("Available Gemini Flash models:\n")

for model in client.models.list():
    if "flash" in model.name.lower():
        print(model.name)
