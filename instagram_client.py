import logging
import os
import time
from typing import Optional, Dict, Any, List
try:
    from instagrapi import Client
    INSTAGRAPI_AVAILABLE = True
except ImportError:
    INSTAGRAPI_AVAILABLE = False

logger = logging.getLogger(__name__)

class InstagramClient:
    def __init__(self):
        self.client: Optional[Client] = None
        self.username: Optional[str] = None
        self.is_authenticated = False
        
        if INSTAGRAPI_AVAILABLE:
            self.client = Client()
            # Set request timeout
            self.client.request_timeout = 30
            
    def login(self, username, password):
        """Login to Instagram using instagrapi"""
        if not INSTAGRAPI_AVAILABLE:
            logger.error("instagrapi library not installed")
            return False, "Kutubxona o'rnatilmagan"
            
        try:
            logger.info(f"Attempting login for {username}...")
            self.client.login(username, password)
            self.username = username
            self.is_authenticated = True
            logger.info(f"Successfully logged in as {username}")
            return True, "Muvaffaqiyatli kirildi"
        except Exception as e:
            logger.error(f"Instagram login failed for {username}: {str(e)}")
            self.is_authenticated = False
            error_msg = str(e)
            if "challenge_required" in error_msg:
                return False, "Tasdiqlash kodi talab qilinadi (Challenge)"
            elif "feedback_required" in error_msg:
                return False, "Instagram blokladi (Feedback required)"
            elif "bad_password" in error_msg:
                return False, "Parol noto'g'ri"
            return False, f"Xatolik: {error_msg}"

    def send_message(self, user_id: str, text: str):
        """Send direct message to a user"""
        if not self.is_authenticated or not self.client:
            return False
            
        try:
            # user_id should be integer string for instagrapi usually, but let's check
            # instagrapi direct_send takes user_ids which is list of int
            self.client.direct_send(text, [int(user_id)])
            return True
        except Exception as e:
            logger.error(f"Failed to send DM: {e}")
            return False

    def get_user_id_from_username(self, username: str):
        """Get numeric user ID from username"""
        if not self.is_authenticated:
            return None
        try:
            return self.client.user_id_from_username(username)
        except Exception as e:
            logger.error(f"Failed to get user ID: {e}")
            return None

    def get_unread_messages(self):
        """Get unread messages from inbox (for polling)"""
        if not self.is_authenticated:
            return []
        try:
            # This is "pending" requests or just inbox? 
            # direct_threads(amount=20, selected_filter='unread')
            threads = self.client.direct_threads(amount=20, selected_filter='unread')
            messages = []
            for thread in threads:
                # Process last message if it's from the other user
                # This is simplified logic
                pass
            return threads
        except Exception as e:
            logger.error(f"Failed to check inbox: {e}")
            return []
            
# Global instance management could handle multiple bots, 
# but for now let's keep it simple or manage instances inside bot_manager
