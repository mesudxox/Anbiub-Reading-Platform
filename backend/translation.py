import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def translate_to_amharic(english_text):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Context: You are a professional translator for an educational app called Anbibu.
    Source Material: The Autobiography of Malcolm X.
    Task: Translate the text below into natural, powerful Amharic. 
    Tone: Serious and historical. 
    
    English Text:
    {english_text}
    """
    
    response = model.generate_content(prompt)
    
    return response.text

sample_text = "I am not a racist. I believe in human beings."
result = translate_to_amharic(sample_text)
print(f"Amharic Result: {result}")