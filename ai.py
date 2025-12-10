import os
import logging
from typing import Optional
from flask import current_app

try:
    import google.generativeai as genai
    # Initialize Gemini client
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY", "default_key"))
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("Google Generative AI library not available. Install with: pip install google-generativeai")

def get_ai_response(message: str, bot_name: str = "Chatbot Factory AI", user_language: str = "uz", knowledge_base: str = "", chat_history: str = "") -> Optional[str]:
    """
    Generate AI response using Google Gemini with chat history context
    """
    try:
        # Language-specific system prompts - STRICT RAG MODE
        language_prompts = {
            'uz': f"Siz {bot_name} - savdo platformasi virtual yordamchisisiz. \nQAT'IY QOIDALAR:\n1. Faqat va faqat quyida keltirilgan BILIMLAR BAZASI (Knowledge Base) asosida javob bering.\n2. O'zingizdan hech qanday tashqi ma'lumot qo'shmang.\n3. Agar savolga javob bazada bo'lmasa, aniq ayting: 'Uzr, bu haqida ma'lumot menda yo'q. Iltimos, operatorga murojaat qiling.'\n4. Ortiqcha iltifot va uzun kirish so'zlaridan saqlaning. Javobingiz aniq va lo'nda bo'lsin.\n5. Narxlar haqida so'ralsa, faqat bazadagi aniq raqamlarni ayting.\n6. Markdown (**, *, `) belgilarini ishlatmang.",
            'ru': f"Вы {bot_name} - виртуальный помощник торговой платформы. \nСТРОГИЕ ПРАВИЛА:\n1. Отвечайте ТОЛЬКО на основе предоставленной БАЗЫ ЗНАНИЙ.\n2. НЕ добавляйте информацию от себя.\n3. Если ответа нет в базе, скажите: 'Извините, у меня нет информации об этом. Пожалуйста, обратитесь к оператору.'\n4. Избегайте лишних слов и длинных вступлений. Ответ должен быть кратким и точным.\n5. НИКОГДА не используйте markdown (**).",
            'en': f"You are {bot_name}, a virtual assistant. \nSTRICT RULES:\n1. Answer ONLY based on the provided KNOWLEDGE BASE.\n2. Do NOT add external information.\n3. If the answer is not in the base, say: 'Sorry, I don't have information about this. Please contact the operator.'\n4. Keep answers concise and direct.\n5. NEVER use markdown (**)."
        }
        
        system_prompt = language_prompts.get(user_language, language_prompts['uz'])

        # Inject platform contact info so bot can answer contact-related questions precisely
        try:
            support_phone = (current_app.config.get('SUPPORT_PHONE') or '').strip()
            support_tg = (current_app.config.get('SUPPORT_TELEGRAM') or '').strip()
            contact_block = []
            if support_phone:
                contact_block.append(f"Admin telefon raqami: {support_phone}")
            if support_tg:
                contact_block.append(f"Telegram aloqa: {support_tg}")
            if contact_block:
                system_prompt += "\n\nQO'SHIMCHA ALOQA MA'LUMOTLARI:\n" + "\n".join(contact_block) + "\n" 
        except Exception:
            pass
        
        # Add knowledge base context if available
        if knowledge_base:
            # Increased limit for Gemini Flash (it handles large context well)
            kb_limit = 10000 
            limited_kb = knowledge_base[:kb_limit]
            system_prompt += f"\n\nSizda quyidagi bilim bazasi mavjud:\n{limited_kb}\n\nAgar foydalanuvchi yuqoridagi ma'lumotlar haqida so'rasa, aniq va to'liq javob bering."
            
            # Debug: log knowledge base uzunligi
            logging.info(f"DEBUG: Knowledge base length: {len(knowledge_base)}, Limited to: {len(limited_kb)}")
        
        # Add chat history context if available
        if chat_history:
            system_prompt += f"\n\nOldingi suhbatlar:\n{chat_history}\n\nYuqoridagi suhbatlarni eslab qoling va kontekst asosida javob bering."
        
        # Create the prompt (optimize for shorter context)
        if len(system_prompt) > 3000:  # Limit system prompt length for speed
            system_prompt = system_prompt[:3000] + "..."
        
        full_prompt = f"{system_prompt}\n\nFoydalanuvchi savoli: {message}"
        
        # Generate response using Gemini with optimization settings
        if not GEMINI_AVAILABLE:
            return get_fallback_response(user_language)
            
        # Use faster model configuration for quicker responses
        generation_config = genai.types.GenerationConfig(
            temperature=0.7,  # Slightly lower for faster generation
            max_output_tokens=500,  # Limit output for speed
            top_p=0.9,
            top_k=40
        )
        
        # Use gemini-flash-lite-latest as requested by user
        model = genai.GenerativeModel(
            'gemini-flash-lite-latest',
            generation_config=generation_config
        )
        response = model.generate_content(full_prompt)
        
        if response.text:
            # Return response as-is, let Telegram handler deal with encoding
            return response.text
        else:
            return get_fallback_response(user_language)
            
    except Exception as e:
        # Safe error logging to prevent encoding issues  
        try:
            error_msg = str(e)
            unicode_replacements = {
                '\u2019': "'", '\u2018': "'", '\u201c': '"', '\u201d': '"',
                '\u2013': '-', '\u2014': '-', '\u2026': '...', '\u00a0': ' ',
                '\u2010': '-', '\u2011': '-', '\u2012': '-', '\u2015': '-'
            }
            
            for unicode_char, replacement in unicode_replacements.items():
                error_msg = error_msg.replace(unicode_char, replacement)
            
            error_msg = error_msg.encode('ascii', errors='ignore').decode('ascii')
            logging.error(f"AI response error: {error_msg}")
        except:
            logging.error("AI response error: Unicode encoding issue")
        return get_fallback_response(user_language)

def get_fallback_response(language: str = "uz") -> str:
    """
    Fallback responses when AI fails
    """
    fallback_responses = {
        'uz': "Salom! Men BotFactory AI botiman. Hozir AI xizmat sozlanmoqda. Tez orada sizga yordam bera olaman! 🤖",
        'ru': "Привет! Я BotFactory AI бот. Сейчас настраивается AI сервис. Скоро смогу помочь вам! 🤖",
        'en': "Hello! I'm BotFactory AI bot. AI service is being configured now. I'll be able to help you soon! 🤖"
    }
    return fallback_responses.get(language, fallback_responses['uz'])

def process_knowledge_base(bot_id: int) -> str:
    """
    Process and combine knowledge base content for a bot
    """
    from models import KnowledgeBase
    
    try:
        knowledge_entries = KnowledgeBase.query.filter_by(bot_id=bot_id).all()
        combined_knowledge = ""
        
        # Debug: log bilim bazasi mavjudligi
        logging.info(f"DEBUG: Bot {bot_id} uchun {len(knowledge_entries)} ta bilim bazasi yozuvi topildi")
        
        for entry in knowledge_entries:
            logging.info(f"DEBUG: Processing entry - Type: {entry.content_type}, Source: {entry.source_name}")
            
            if entry.content_type == 'product':
                # For products, format them clearly for AI with detailed structure
                product_text = f"=== MAHSULOT MA'LUMOTI ===\n{entry.content}\n=== MAHSULOT OXIRI ===\n"
                combined_knowledge += product_text + "\n"
                logging.info(f"DEBUG: Product added to knowledge: {entry.source_name}")
            elif entry.content_type == 'image':
                # For images, add description about the image
                image_info = f"Rasm: {entry.filename or 'Yuklangan rasm'}"
                if entry.source_name:
                    image_info += f" ({entry.source_name})"
                image_info += f" - bu mahsulot/xizmat haqidagi vizual ma'lumot. Foydalanuvchi ushbu rasm haqida so'rasa, unga rasm haqida ma'lumot bering."
                combined_knowledge += f"{image_info}\n\n"
                logging.info(f"DEBUG: Image added to knowledge: {entry.source_name or entry.filename}")
            else:
                # For text and file content
                combined_knowledge += f"{entry.content}\n\n"
                logging.info(f"DEBUG: File content added to knowledge: {entry.filename}")
        
        logging.info(f"DEBUG: Combined knowledge length: {len(combined_knowledge)} characters")
        if combined_knowledge:
            logging.info(f"DEBUG: First 200 chars of knowledge: {combined_knowledge[:200]}...")
        
        return combined_knowledge.strip()
    except Exception as e:
        logging.error(f"Knowledge base processing error: {str(e)}")
        return ""

def find_relevant_product_images(bot_id: int, user_message: str) -> list:
    """
    Find the most relevant product image based on user's message
    Returns only the best matching product, not all products
    """
    from models import KnowledgeBase
    
    try:
        # Get products that match user's message
        products = KnowledgeBase.query.filter_by(bot_id=bot_id, content_type='product').all()
        
        if not products:
            return []
        
        user_message_lower = user_message.lower()
        user_words = [word.strip() for word in user_message_lower.split() if len(word.strip()) > 2]
        
        best_match = None
        best_score = 0
        
        for product in products:
            product_content = product.content.lower()
            product_name = (product.source_name or "").lower()
            
            # Calculate relevance score
            score = 0
            
            # Extract product name from content
            lines = product.content.split('\n')
            actual_product_name = ""
            for line in lines:
                if line.startswith('Mahsulot:'):
                    actual_product_name = line.replace('Mahsulot:', '').strip().lower()
                    break
            
            # High score for exact product name match
            if actual_product_name:
                for user_word in user_words:
                    if user_word in actual_product_name:
                        score += 10
                        
            # Medium score for source name match
            if product_name:
                for user_word in user_words:
                    if user_word in product_name:
                        score += 5
                        
            # Low score for content match (but avoid generic words)
            generic_words = ['mahsulot', 'narx', 'som', 'dollar', 'paket', 'zip', 'rasm', 'tavsif', 'haqida']
            for user_word in user_words:
                if user_word not in generic_words and user_word in product_content:
                    score += 1
            
            # Only consider products with images
            has_image = False
            image_url = ""
            for line in lines:
                if line.startswith('Rasm:') and 'http' in line:
                    image_url = line.replace('Rasm:', '').strip()
                    has_image = True
                    break
            
            # Update best match if this product scores higher and has an image
            if has_image and score > best_score:
                best_score = score
                best_match = {
                    'url': image_url,
                    'product_name': product.source_name or actual_product_name or 'Mahsulot',
                    'caption': f"📦 {product.source_name or actual_product_name or 'Mahsulot'}"
                }
        
        # Return only the best match, or empty list if no good match found
        if best_match and best_score >= 3:  # Minimum score threshold
            return [best_match]
        else:
            return []
            
    except Exception as e:
        logging.error(f"Error finding product images: {str(e)}")
        return []

def validate_ai_response(response: Optional[str], max_length: int = 4000) -> Optional[str]:
    """
    Validate and clean AI response
    """
    if not response:
        return None
    
    # Remove markdown formatting
    response = response.replace('**', '').replace('*', '').replace('`', '')
    
    # Limit response length
    if len(response) > max_length:
        response = response[:max_length] + "..."
    
    return response.strip()
