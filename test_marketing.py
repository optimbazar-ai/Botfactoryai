import os
import logging
from dotenv import load_dotenv

# Load env vars
load_dotenv()

from marketing import marketing_ai

# Setup logging to console
logging.basicConfig(level=logging.INFO)

def test_generation():
    print("🚀 Marketing AI Testing...\n")
    
    topic = "iPhone 15 Pro"
    print(f"Post mavzusi: {topic}")
    
    # 1. Test SEO Post
    print("\n📝 Generating SEO Post...")
    post = marketing_ai.generate_seo_post(topic, "iphone, apple, tech", "uz")
    print("-" * 50)
    print(post)
    print("-" * 50)
    
    # 2. Test Image Prompt
    print("\n🎨 Generating Image Prompt...")
    prompt = marketing_ai.generate_image_prompt(topic)
    print("-" * 50)
    print(prompt)
    print("-" * 50)

if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY1"):
        print("⚠️ GOOGLE_API_KEY1 topilmadi. .env faylni tekshiring.")
    else:
        test_generation()
