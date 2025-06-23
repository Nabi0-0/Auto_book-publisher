import openai
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def load_raw_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def save_spun_text(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def spin_text_with_gpt(chapter_text, tone="modern and engaging"):
    system_prompt = f"""You are an AI writer. Rewrite the given story in a {tone} tone.
Keep the story and events the same but rewrite the language in a clearer, modern style. Use more vivid, easy-to-read language, and improve pacing and structure."""
    
    response = openai.ChatCompletion.create(
        model="gpt-4",  # or "gpt-3.5-turbo" if you don't have access to GPT-4
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": chapter_text}
        ],
        temperature=0.8,
        max_tokens=4096  # adjust based on chapter length
    )
    return response['choices'][0]['message']['content']

if __name__ == "__main__":
    input_path = "outputs/raw_chapter1.txt"
    output_path = "outputs/chapter1_spun_v1.txt"

    print("Loading raw chapter...")
    chapter = load_raw_text(input_path)

    print("Spinning with AI Writer...")
    spun_version = spin_text_with_gpt(chapter)

    print("Saving spun version...")
    save_spun_text(output_path, spun_version)

    print(f"AI-spun chapter saved to: {output_path}")
