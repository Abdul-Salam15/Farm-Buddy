
import os
import sys
# Add parent directory to path
sys.path.append(os.getcwd())

from utils.gemini_api import ask_gemini
from dotenv import load_dotenv

load_dotenv()

print("Testing Gemini API...")
try:
    history = [{"role": "user", "content": "Hello, how are you?"}]
    response = ask_gemini(history)
    print("Response type:", type(response))
    print("Response:", response)
    
    print("\nTesting Streaming...")
    stream = ask_gemini(history, stream=True)
    print("Stream type:", type(stream))
    for chunk in stream:
        print("Chunk:", chunk, end="", flush=True)
    print("\nDone.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
