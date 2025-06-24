import os
from dotenv import load_dotenv
from openai import OpenAI  # This is the new import
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

client = OpenAI(
    api_key=groq_api_key,
    base_url="https://api.groq.com/openai/v1"  # Important: use Groq's endpoint
)
def load_raw_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()
    
def save_spun_text(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def spin_text_with_llama(chapter_text, tone="modern and engaging"):
    system_prompt = f"""You are an AI writer. Rewrite the following story in a {tone} tone.
Keep the events unchanged, but modernize the writing, improve clarity, pacing, and readability."""
    response = client.chat.completions.create(
        model="llama3-8b-8192",  
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": chapter_text}
        ],
        temperature=0.8,
        max_tokens=2048
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    input_path = "outputs/raw_chapter1.txt"
    output_path = "outputs/chapter1_spun_v1.txt"
    #print("Loading raw chapter...")
    chapter = load_raw_text(input_path)
    #print("Spinning with Groq LLaMA 3...")
    spun_version = spin_text_with_llama(chapter)
    #print("Saving rewritten chapter...")
    save_spun_text(output_path, spun_version)
    #print(f"✅ AI-spun chapter saved to: {output_path}")
