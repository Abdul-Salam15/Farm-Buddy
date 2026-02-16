import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# System instruction for the persona
SYSTEM_INSTRUCTION = """
You are FarmBuddy, an expert agricultural advisor for Nigerian smallholder farmers. 
Your goal is to provide accurate, practical, and easy-to-understand farming advice.
- Prioritize organic and cost-effective solutions.
- Use simple English.
- If you don't know the answer, admit it and suggest consulting a local extension agent.
"""

model = genai.GenerativeModel(
    "gemini-flash-latest",
    system_instruction=SYSTEM_INSTRUCTION
)

def ask_gemini(messages_history: list, weather_context=None) -> str:
    """
    Sends the full conversation history to Gemini for a context-aware response.
    messages_history: List of dicts [{"role": "user", "content": "..."}, ...]
    weather_context: Optional string containing current weather info
    """
    # Convert Streamlit roles to Gemini roles
    # Streamlit: "user", "assistant"
    # Gemini: "user", "model"
    gemini_history = []
    
    # Process all messages except the last one (which is the new prompt)
    for msg in messages_history[:-1]:
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [msg["content"]]})
    
    # Start a chat session with history
    chat = model.start_chat(history=gemini_history)
    
    # Send the last message (current user prompt)
    last_message = messages_history[-1]["content"]
    
    if weather_context:
        # Prepend weather context to the user's message
        last_message = f"[System Context: {weather_context}]\n\n{last_message}"
        
    response = chat.send_message(last_message)
    
    return response.text.strip()


def analyze_plant_image(image_path, conversation_history=None):
    """
    Analyze a plant image for disease detection using Gemini Vision
    image_path: Path to the uploaded plant image
    conversation_history: Optional conversation context
    """
    from PIL import Image
    
    try:
        # Load the image
        img = Image.open(image_path)
        
        # Create prompt for plant disease analysis
        prompt = """You are FarmBuddy, an expert agricultural advisor specializing in plant disease diagnosis.

Analyze this plant leaf image and provide:
1. **Disease Identification**: What disease or problem do you see? (if any)
2. **Confidence Level**: How confident are you in this diagnosis?
3. **Symptoms Observed**: Describe the visible symptoms
4. **Recommended Treatment**: Practical, cost-effective solutions for Nigerian smallholder farmers
5. **Prevention Tips**: How to prevent this in the future

Use simple English and be practical. If you cannot identify a specific disease, explain what you observe and suggest consulting a local agricultural extension agent."""

        # If there's conversation history, include it for context
        if conversation_history:
            # Use vision model with context
            response = model.generate_content([prompt, img])
        else:
            # Just analyze the image
            response = model.generate_content([prompt, img])
        
        return response.text.strip()
        
    except Exception as e:
        return f"Error analyzing image: {str(e)}"


def summarize_title(text):
    """
    Generate a short 5-word summary title for a conversation based on the first prompt
    """
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        # Use simple model for summarization
        prompt = f"Summarize the following text into a short title of maximum 5 words. Do not use quotes or special characters. Text: {text}"
        response = model.generate_content(prompt)
        return response.text.strip().replace('"', '').replace('*', '')
    except Exception as e:
        print(f"Error generating title: {str(e)}")
        # Fallback to truncation if AI fails
        return text[:30] + "..." if len(text) > 30 else text

