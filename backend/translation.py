import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def translate_to_amharic(english_text):
    prompt = f"""
You are an expert English-to-Amharic translator. 
Your goal is to provide a translation that sounds natural to a native speaker in Addis Ababa, not a literal word-for-word translation.

EXAMPLES:
Input: "Persistence is the key to success."
Output: {{"full_translation": "ጽናት ለስኬት ቁልፍ ነው።", "word_map": {{"persistence": "ጽናት", "key": "ቁልፍ", "success": "ስኬት"}}}}

Input: "He is a software developer."
Output: {{"full_translation": "እሱ የሶፍትዌር አልሚ ነው።", "word_map": {{"software": "ሶፍትዌር", "developer": "አልሚ"}}}}

Now translate this text:
"{english_text}"

Return ONLY JSON.
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # Strongest free model
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs only JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"} # Forces valid JSON
        )
        
        # Groq returns the content as a string inside the message object
        return json.loads(completion.choices[0].message.content)

    except Exception as e:
        print(f"❌ Groq Error: {str(e)}")
        raise e





# import os
# from google import genai
# from dotenv import load_dotenv
# import json

# load_dotenv()

# client = genai.Client(
#     api_key=os.getenv("GEMINI_API_KEY"),
#     http_options={'api_version': 'v1beta'} 
# )

# def translate_to_amharic(english_text):
#     prompt = f"""
#     You are the translation engine for 'Project Anbibu'. 
#     Task: Create a word-by-word mapping for an interactive reader.
    
#     1. Translate the full text into natural Amharic for the 'Main Translation' view.
#     2. Create a 'word_map' object:
#        - Keys should be the original English words from the text (case-insensitive).
#        - Values should be the most context-appropriate Amharic translation for that specific word.
#        - Exclude common stop-words (a, an, the, is, are).

#     Text:
#     {english_text}
    
#     Return ONLY a JSON object with these keys: "full_translation", "word_map".
#     """

#     response = client.models.generate_content(
#         model="gemini-1.5-flash", 
#         contents=prompt,
#         config={"response_mime_type": "application/json"}
#     )
    
#     return json.loads(response.text)