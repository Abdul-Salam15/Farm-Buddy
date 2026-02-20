import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Force reload triggers

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
    "gemini-flash-lite-latest",
    system_instruction=SYSTEM_INSTRUCTION
)

def ask_gemini(messages_history: list, weather_context=None, stream=False, language='en'):
    """
    Sends the full conversation history to Gemini.
    stream: If True, returns a generator for streaming responses.
    language: Target language for the response ('en', 'ha', 'ig', 'yo').
    """
    # Verify input
    if not messages_history: return "Hello! How can I help you?"

    # Language instruction mapping
    lang_instructions = {
        'en': "Answer in English.",
        'ha': "Answer in Hausa language (Harshen Hausa).",
        'ig': "Answer in Igbo language (Asụsụ Igbo).",
        'yo': "Answer in Yoruba language (Èdè Yorùbá)."
    }
    lang_instruction = lang_instructions.get(language, "Answer in English.")

    # Convert Streamlit roles to Gemini roles
    gemini_history = []
    
    # Process messages, limit to last 10 to improve speed
    recent_messages = messages_history[-10:] if len(messages_history) > 10 else messages_history
    
    # Process all messages except the last one
    for msg in recent_messages[:-1]:
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [msg["content"]]})
    
    # Start chat
    chat = model.start_chat(history=gemini_history)
    
    # Last message
    last_message = recent_messages[-1]["content"]
    
    # Add current date to context to prevent hallucinations
    from datetime import datetime
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    
    system_context = f"Current Date: {current_date}\nIMPORTANT INSTRUCTION: {lang_instruction}"
    
    if weather_context:
        system_context += f"\nWeather Info: {weather_context}"
        
    last_message = f"[System Context: {system_context}]\n\n{last_message}"
        
    response = chat.send_message(last_message, stream=stream)
    
    if stream:
        def stream_generator():
            try:
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
            except Exception as e:
                # In case of safety filters or other errors during iteration
                print(f"Error during streaming: {e}")
                yield " [Error: Interrupted] "
        return stream_generator()
    else:
        try:
            return response.text.strip()
        except ValueError:
            # Handle cases where response might be blocked
            return "I'm sorry, I cannot answer that request due to safety guidelines."


def analyze_plant_image(image_path, conversation_history=None, stream=False):
    """
    Analyze a plant image for disease detection using Gemini Vision
    image_path: Path to the uploaded plant image
    conversation_history: Optional conversation context
    stream: If True, returns a generator
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

        response = model.generate_content([prompt, img], stream=stream)
        
        if stream:
            def stream_generator():
                try:
                    for chunk in response:
                        if chunk.text:
                            yield chunk.text
                except Exception as e:
                    print(f"Error during vision streaming: {e}")
                    yield " [Error: Interrupted] "
            return stream_generator()
        else:
            return response.text.strip()
        
    except Exception as e:
        if stream:
            def error_gen(): yield f"Error analyzing image: {str(e)}"
            return error_gen()
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

