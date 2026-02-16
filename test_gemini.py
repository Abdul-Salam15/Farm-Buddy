import google.generativeai as genai

from dotenv import load_dotenv
import os

load_dotenv()

# Replace with your actual Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")
resp = model.generate_content("Hello Gemini, test if API works")
print(resp.text)
