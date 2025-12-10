import os
import logging
from typing import Optional
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app import csrf

# Configure logger
logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GOOGLE_GENAI_AVAILABLE = True
except ImportError:
    GOOGLE_GENAI_AVAILABLE = False
    logger.warning("google-generativeai not installed. Marketing AI disabled.")

class MarketingAI:
    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_API_KEY1")
        self.is_available = False
        
        if not GOOGLE_GENAI_AVAILABLE:
            return
            
        if self.api_key:
            try:
                # Configure specific client for Marketing/SEO
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-flash-lite-latest')
                self.is_available = True
                logger.info("✅ Marketing AI initialized with GOOGLE_API_KEY1")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Marketing AI: {e}")
        else:
            logger.warning("⚠️ GOOGLE_API_KEY1 not found. Marketing features will use default key or be disabled.")
            # Fallback to default key if KEY1 not present
            default_key = os.environ.get("GOOGLE_API_KEY")
            if default_key:
                try:
                    genai.configure(api_key=default_key)
                    self.model = genai.GenerativeModel('gemini-flash-lite-latest')
                    self.is_available = True
                    logger.info("⚠️ Marketing AI using default GOOGLE_API_KEY as fallback")
                except:
                    pass

    def generate_seo_post(self, topic: str, keywords: str, language: str = 'uz') -> str:
        """
        Generate SEO optimized content for blog or channel
        """
        if not self.is_available:
            return "⚠️ AI xizmati mavjud emas. API kalitni tekshiring."

        prompts = {
            'uz': f"""
            Siz professional SMM menejer va SEO mutaxassisisiz.
            Mavzu: {topic}
            Kalit so'zlar: {keywords}
            
            Vazifa: Telegram kanal yoki Instagram uchun SEO optimallashtirilgan, o'quvchini jalb qiluvchi post yozing.
            
            Talablar:
            1. Sarlavha: Diqqatni tortadigan (Clickbait emas, lekin qiziqarli)
            2. Kirish: Muammoni ko'rsatish va qiziqtirish
            3. Asosiy qism: Foydali ma'lumotlar ro'yxati (bullet points)
            4. Call to Action (CTA): Obuna bo'lishga yoki sotib olishga undash
            5. Xshteglar: # bilan yozilgan 5-10 ta relevant heshteg
            6. Emojilar: Matnni jonlantirish uchun mos emojilar
            
            Matnni chiroyli formatda va professional ohangda yozing.
            """,
            
            'ru': f"""
            Вы профессиональный SMM-менеджер и SEO-специалист.
            Тема: {topic}
            Ключевые слова: {keywords}
            
            Задача: Написать SEO-оптимизированный, вовлекающий пост для Telegram-канала или Instagram.
            
            Требования:
            1. Заголовок: Цепляющий внимание
            2. Введение: Обозначение проблемы и интрига
            3. Основная часть: Полезная информация списком
            4. Call to Action (CTA): Призыв к действию (подписка/покупка)
            5. Хэштеги: 5-10 релевантных хэштегов
            6. Эмодзи: Для оживления текста
            """
        }

        try:
            prompt = prompts.get(language, prompts['uz'])
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"SEO post generation error: {e}")
            return "❌ Post yaratishda xatolik yuz berdi."

    def generate_marketing_plan(self, product_name: str, target_audience: str) -> str:
        """
        Generate a mini marketing strategy
        """
        if not self.is_available:
            return "⚠️ AI xizmati mavjud emas."

        prompt = f"""
        Mahsulot: {product_name}
        Nishon auditoriya: {target_audience}
        
        Ushbu mahsulot uchun 3 kunlik mini marketing rejasini tuzing:
        1-kun: Qiziqtirish (Teaser)
        2-kun: Foydali kontent + Muammo yechimi
        3-kun: Sotuv posti (Chegirma yoki Taklif)
        
        Har bir kun uchun qisqacha post g'oyasi va sarlavhasini yozing.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Marketing plan error: {e}")
            return "❌ Marketing reja tuzishda xatolik."

    
    def generate_image_prompt(self, topic: str) -> str:
        """ 
        Generate a detailed image prompt for Imagen 3 / Midjourney based on the topic
        """
        if not self.is_available:
            return ""
            
        prompt = f"""
        Mavzu: {topic}
        
        Vazifa: Ushbu mavzu uchun "Imagen 3" yoki "Midjourney" AI lari uchun mukammal ingliz tilida rasm promptini yozing.
        
        Talablar:
        1. Fotorealistik, 8k sifat, kinematik yoritish.
        2. Tafsilotlarga boy (muhit, ranglar, uslub).
        3. Prompt ingliz tilida bo'lishi SHART.
        4. Javob faqat promptdan iborat bo'lsin.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Image prompt generation error: {e}")
            return ""

# Create Blueprint
marketing_bp = Blueprint('marketing', __name__)

# Global instance - lazy initialized
_marketing_ai = None

def get_marketing_ai():
    """Get or create the marketing AI instance (lazy initialization)"""
    global _marketing_ai
    if _marketing_ai is None:
        _marketing_ai = MarketingAI()
    return _marketing_ai

@marketing_bp.route('/')
@login_required
def marketing_index():
    """Marketing tools page"""
    return render_template('marketing.html')

@marketing_bp.route('/generate-seo', methods=['POST'])
@csrf.exempt
@login_required  
def generate_seo():
    """Generate SEO optimized post"""
    data = request.get_json()
    topic = data.get('topic', '')
    keywords = data.get('keywords', '')
    language = data.get('language', 'uz')
    
    if not topic:
        return jsonify({'error': 'Mavzuni kiriting'}), 400
    
    result = get_marketing_ai().generate_seo_post(topic, keywords, language)
    return jsonify({'content': result})

@marketing_bp.route('/generate-plan', methods=['POST'])
@csrf.exempt
@login_required
def generate_plan():
    """Generate marketing plan"""
    data = request.get_json()
    product_name = data.get('product_name', '')
    target_audience = data.get('target_audience', '')
    
    if not product_name:
        return jsonify({'error': 'Mahsulot nomini kiriting'}), 400
    
    result = get_marketing_ai().generate_marketing_plan(product_name, target_audience)
    return jsonify({'content': result})

@marketing_bp.route('/generate-image-prompt', methods=['POST'])
@csrf.exempt
@login_required
def generate_image_prompt():
    """Generate image prompt for AI image generators"""
    data = request.get_json()
    topic = data.get('topic', '')
    
    if not topic:
        return jsonify({'error': 'Mavzuni kiriting'}), 400
    
    result = get_marketing_ai().generate_image_prompt(topic)
    return jsonify({'prompt': result})