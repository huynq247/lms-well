import google.generativeai as genai
import json
import os
from typing import List, Dict, Any
from app.core.auth import UserRole
from app.core.config import get_settings

class GeminiService:
    def __init__(self):
        # Cấu hình Gemini API key từ settings
        settings = get_settings()
        api_key = settings.gemini_api_key
        if not api_key or api_key == "your-gemini-api-key-here":
            raise ValueError("GEMINI_API_KEY không được cấu hình trong biến môi trường")
        
        genai.configure(api_key=api_key)
        # Use stable Gemini 2.5 Flash - fast and reliable
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    def verify_admin_permission(self, user) -> bool:
        """Kiểm tra quyền admin của user"""
        return user and hasattr(user, 'role') and user.role == UserRole.ADMIN
    
    async def generate_flashcards(self, topic: str, quantity: int = 10, language: str = "vietnamese") -> List[Dict[str, Any]]:
        """
        Tạo flashcards tự động bằng Gemini AI
        
        Args:
            topic: Chủ đề để tạo flashcards
            quantity: Số lượng flashcards cần tạo (mặc định 10)
            language: Ngôn ngữ (mặc định tiếng Việt)
            
        Returns:
            List[Dict]: Danh sách flashcards với cấu trúc question/answer
        """
        
        prompt = f"""
        Tạo {quantity} flashcards về chủ đề "{topic}" bằng tiếng {language}.
        
        Yêu cầu:
        - Mỗi flashcard phải có câu hỏi (question) và câu trả lời (answer)
        - Câu hỏi phải rõ ràng, cụ thể
        - Câu trả lời phải chính xác, súc tích
        - Phù hợp với mục đích học tập
        
        Trả về dữ liệu theo định dạng JSON sau:
        {{
            "flashcards": [
                {{
                    "question": "Câu hỏi 1",
                    "answer": "Câu trả lời 1",
                    "difficulty": "easy|medium|hard",
                    "tags": ["tag1", "tag2"]
                }},
                ...
            ]
        }}
        
        Chỉ trả về JSON, không có text khác.
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Parse JSON từ response
            json_text = response.text.strip()
            if json_text.startswith("```json"):
                json_text = json_text[7:-3]
            elif json_text.startswith("```"):
                json_text = json_text[3:-3]
                
            flashcards_data = json.loads(json_text)
            
            return flashcards_data.get("flashcards", [])
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Lỗi parse JSON từ Gemini response: {str(e)}")
        except Exception as e:
            raise ValueError(f"Lỗi tạo flashcards: {str(e)}")
    
    async def generate_deck_description(self, deck_name: str, flashcards: List[Dict]) -> str:
        """
        Tạo mô tả cho deck dựa trên tên deck và flashcards
        
        Args:
            deck_name: Tên deck
            flashcards: Danh sách flashcards trong deck
            
        Returns:
            str: Mô tả cho deck
        """
        
        topics = [card.get("question", "")[:50] for card in flashcards[:3]]
        topics_text = ", ".join(topics)
        
        prompt = f"""
        Tạo mô tả ngắn gọn cho bộ thẻ học "{deck_name}" 
        dựa trên một số câu hỏi mẫu: {topics_text}
        
        Yêu cầu:
        - Mô tả không quá 200 ký tự
        - Bằng tiếng Việt
        - Thể hiện nội dung chính của bộ thẻ
        - Hấp dẫn và khuyến khích học tập
        
        Chỉ trả về mô tả, không có text khác.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Bộ thẻ học về {deck_name} với {len(flashcards)} thẻ học tập."

    async def generate_single_flashcard(self, word_or_topic: str, language: str = "english", 
                                      card_type: str = "vocabulary", difficulty: str = "medium",
                                      include_pronunciation: bool = True, include_examples: bool = True,
                                      include_synonyms: bool = True) -> Dict[str, Any]:
        """
        Tạo chi tiết một flashcard bằng Gemini AI
        
        Args:
            word_or_topic: Từ vựng hoặc chủ đề cần tạo flashcard
            language: Ngôn ngữ (english, vietnamese, etc.)
            card_type: Loại thẻ (vocabulary, grammar, pronunciation, etc.)
            difficulty: Mức độ khó (easy, medium, hard)
            include_pronunciation: Có bao gồm phát âm không
            include_examples: Có bao gồm ví dụ không
            include_synonyms: Có bao gồm từ đồng nghĩa không
            
        Returns:
            Dict: Thông tin chi tiết flashcard
        """
        
        # Tạo prompt dựa trên loại thẻ và ngôn ngữ
        if card_type == "vocabulary" and language == "english":
            prompt = f"""
            Create a detailed flashcard for the English vocabulary word: "{word_or_topic}"
            Difficulty level: {difficulty}
            
            Requirements:
            - Question: English question (e.g., "What does 'abundant' mean?")
            - Answer: English definition/meaning only
            - Pronunciation: IPA pronunciation (if {include_pronunciation})
            - Examples: 2-3 English example sentences (if {include_examples})
            - Synonyms: 2-3 English synonyms (if {include_synonyms})
            - Explanation: Detailed explanation of usage in English
            - Tags: Related keywords in English
            
            Return JSON format:
            {{
                "question": "What does '{word_or_topic}' mean?",
                "answer": "English definition",
                "pronunciation": "/phonetic transcription/",
                "examples": [
                    "Example sentence 1",
                    "Example sentence 2"
                ],
                "synonyms": ["synonym1", "synonym2"],
                "explanation": "Detailed explanation about word usage in English",
                "difficulty": "{difficulty}",
                "tags": ["tag1", "tag2", "vocabulary"]
            }}
            
            Return only JSON, no other text.
            """
        elif card_type == "vocabulary" and language == "vietnamese":
            prompt = f"""
            Create a detailed flashcard for Vietnamese vocabulary: "{word_or_topic}"
            Difficulty level: {difficulty}
            
            Requirements:
            - Question: Question about word meaning in Vietnamese
            - Answer: Detailed definition in Vietnamese
            - Examples: 2-3 example sentences using this word in Vietnamese
            - Synonyms: Vietnamese synonyms (if any)
            - Explanation: Explanation of origin and usage in Vietnamese
            - Tags: Related keywords in Vietnamese
            
            Return JSON in similar format.
            """
        else:
            prompt = f"""
            Create a flashcard for topic: "{word_or_topic}"
            Type: {card_type}
            Language: {language}
            Difficulty level: {difficulty}
            
            Create appropriate question and answer for the card type and difficulty level.
            Use only {language} language in the response.
            
            Return JSON with fields: question, answer, explanation, difficulty, tags
            """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Parse JSON từ response
            json_text = response.text.strip()
            if json_text.startswith("```json"):
                json_text = json_text[7:-3]
            elif json_text.startswith("```"):
                json_text = json_text[3:-3]
                
            flashcard_data = json.loads(json_text)
            
            # Đảm bảo có đầy đủ các trường cần thiết
            result = {
                "question": flashcard_data.get("question", f"Nghĩa của '{word_or_topic}' là gì?"),
                "answer": flashcard_data.get("answer", "Chưa có định nghĩa"),
                "pronunciation": flashcard_data.get("pronunciation", "") if include_pronunciation else "",
                "examples": flashcard_data.get("examples", []) if include_examples else [],
                "synonyms": flashcard_data.get("synonyms", []) if include_synonyms else [],
                "explanation": flashcard_data.get("explanation", ""),
                "difficulty": flashcard_data.get("difficulty", difficulty),
                "tags": flashcard_data.get("tags", [card_type, language])
            }
            
            return result
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Lỗi parse JSON từ Gemini response: {str(e)}")
        except Exception as e:
            raise ValueError(f"Lỗi tạo flashcard: {str(e)}")

# Singleton instance - khởi tạo lazy
_gemini_service_instance = None

def get_gemini_service() -> GeminiService:
    global _gemini_service_instance
    if _gemini_service_instance is None:
        _gemini_service_instance = GeminiService()
    return _gemini_service_instance
