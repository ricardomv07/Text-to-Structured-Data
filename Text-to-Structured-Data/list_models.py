import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("Modelos disponibles:")
print("-" * 50)
for model in genai.list_models():
    print(f"Nombre: {model.name}")
    print(f"Display Name: {model.display_name}")
    print(f"Descripción: {model.description}")
    print(f"Métodos soportados: {model.supported_generation_methods}")
    print("-" * 50)
