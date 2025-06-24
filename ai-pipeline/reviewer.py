import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

client = OpenAI(
    api_key=groq_api_key,
    base_url="https://api.groq.com/openai/v1"
)

def load_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def save_text(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def review_text_with_llama(spun_text, tone="natural and polished"):
    system_prompt = f"""You are an experienced book editor. Your task is to review and refine AI-generated rewritten chapters.
Keep the story structure, events, and pacing the same, but:
- Fix any awkward phrasing
- Smooth out transitions
- Improve clarity and readability
- Maintain a {tone} tone without over-editing
Make the final version feel natural, like it was written by a human author."""
    response = client.chat.completions.create(
        model="llama3-8b-8192", 
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": spun_text}
        ],
        temperature=0.7,
        max_tokens=2048
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    input_path = "outputs/chapter1_spun_v1.txt"
    output_path = "outputs/chapter1_reviewed_v1.txt"

    #print("🔍Loading AI-spun chapter...")
    spun_text = load_text(input_path)
    #print("🧠Reviewing with AI Reviewer...")
    reviewed_text = review_text_with_llama(spun_text)
    #print("💾Saving reviewed version...")
    save_text(output_path, reviewed_text)
    #print(f"✅Reviewed chapter saved to: {output_path}")
