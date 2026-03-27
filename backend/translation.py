import os
from google import genai
from dotenv import load_dotenv
import json

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options={'api_version': 'v1beta'} 
)

def translate_to_amharic(english_text):
    prompt = f"""
    You are the translation engine for 'Project Anbibu'. 
    Task: Create a word-by-word mapping for an interactive reader.
    
    1. Translate the full text into natural Amharic for the 'Main Translation' view.
    2. Create a 'word_map' object:
       - Keys should be the original English words from the text (case-insensitive).
       - Values should be the most context-appropriate Amharic translation for that specific word.
       - Exclude common stop-words (a, an, the, is, are).

    Text:
    {english_text}
    
    Return ONLY a JSON object with these keys: "full_translation", "word_map".
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=prompt,
        config={"response_mime_type": "application/json"}
    )
    
    return json.loads(response.text)