"""
Language Detection and Response System
Ensures AI responds in the same language as the user's query
"""

from typing import Dict, Optional, Tuple
import re
from collections import Counter

class LanguageDetectionSystem:
    """Advanced language detection and response language management"""
    
    def __init__(self):
        # Language indicators with weighted confidence scores
        self.language_indicators = {
            'tr': {
                'common_words': ['ve', 'bir', 'bu', 'için', 'ile', 'da', 'de', 'mi', 'mı', 'mu', 'mü', 
                                'ne', 'nasıl', 'nedir', 'hangi', 'kim', 'nerede', 'neden', 'kaç', 
                                'var', 'yok', 'evet', 'hayır', 'merhaba', 'teşekkür', 'lütfen'],
                'suffixes': ['ler', 'lar', 'mız', 'miz', 'nız', 'niz', 'yor', 'iyor', 'uyor'],
                'characters': ['ş', 'ğ', 'ı', 'ö', 'ü', 'ç'],
                'question_patterns': [r'\b\w+\s+(mı|mi|mu|mü)\b', r'\bne\s+\w+', r'\bnasıl\s+\w+'],
                'weight': 1.5  # Turkish has unique characters, so higher weight
            },
            'fr': {
                'common_words': ['et', 'le', 'la', 'les', 'un', 'une', 'de', 'du', 'des', 'je', 'tu', 
                                'il', 'elle', 'nous', 'vous', 'ils', 'elles', 'qui', 'que', 'quoi', 
                                'où', 'quand', 'comment', 'pourquoi', 'avec', 'sans', 'pour', 'dans',
                                'bonjour', 'merci', 's\'il vous plaît'],
                'suffixes': ['tion', 'ment', 'iste', 'eur', 'euse', 'ité', 'isme'],
                'characters': ['é', 'è', 'ê', 'à', 'ç', 'ù', 'ô', 'î'],
                'question_patterns': [r'\best-ce que\b', r'\bqu\'est-ce\b', r'\bcomment\s+\w+'],
                'weight': 1.2
            },
            'en': {
                'common_words': ['the', 'is', 'are', 'was', 'were', 'and', 'or', 'but', 'in', 'on', 
                                'at', 'to', 'for', 'of', 'with', 'what', 'where', 'when', 'why', 
                                'how', 'who', 'which', 'can', 'could', 'would', 'should', 'hello',
                                'thanks', 'please'],
                'suffixes': ['ing', 'tion', 'ment', 'ness', 'able', 'ible', 'ful', 'less'],
                'characters': [],  # English uses standard ASCII
                'question_patterns': [r'\bwhat\s+\w+', r'\bhow\s+\w+', r'\bwhy\s+\w+'],
                'weight': 1.0  # Base weight
            }
        }
        
        # Language-specific prompt instructions
        self.language_prompts = {
            'tr': """
ÖNEMLI: Bu kullanıcı Türkçe konuşuyor. MUTLAKA Türkçe yanıt ver.
Yanıtın tamamen Türkçe olmalı, hiçbir şekilde Fransızca veya İngilizce kelime kullanma.
Türkçe dilbilgisi kurallarına uy ve profesyonel Türkçe kullan.
""",
            'fr': """
IMPORTANT: Cet utilisateur parle français. Répondez OBLIGATOIREMENT en français.
Votre réponse doit être entièrement en français, n'utilisez pas de mots en anglais ou en turc.
Utilisez un français professionnel et respectez la grammaire française.
""",
            'en': """
IMPORTANT: This user speaks English. You MUST respond in English.
Your entire response must be in English, do not use French or Turkish words.
Use professional English and proper grammar.
"""
        }
        
        # Technical terms that are language-agnostic
        self.technical_terms = {
            'python', 'javascript', 'sql', 'html', 'css', 'api', 'rest', 'git', 'docker',
            'kubernetes', 'aws', 'azure', 'linux', 'windows', 'macos', 'excel', 'word',
            'powerpoint', 'photoshop', 'autocad', 'wordpress', 'react', 'node.js', 'mysql'
        }
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect language of the input text
        Returns: (language_code, confidence_score)
        """
        if not text:
            return 'fr', 0.5  # Default to French for NETZ
        
        text_lower = text.lower()
        scores = {'tr': 0, 'fr': 0, 'en': 0}
        
        # Remove technical terms for better language detection
        for term in self.technical_terms:
            text_lower = text_lower.replace(term, '')
        
        # Calculate scores for each language
        for lang, indicators in self.language_indicators.items():
            # Check common words
            word_count = 0
            words = text_lower.split()
            for word in indicators['common_words']:
                if word in words:
                    word_count += 1
            
            if len(words) > 0:
                scores[lang] += (word_count / len(words)) * 40 * indicators['weight']
            
            # Check characters
            char_count = sum(1 for char in text if char in indicators['characters'])
            if len(text) > 0:
                scores[lang] += (char_count / len(text)) * 30 * indicators['weight']
            
            # Check suffixes
            suffix_matches = sum(1 for suffix in indicators['suffixes'] 
                               if any(word.endswith(suffix) for word in words))
            scores[lang] += suffix_matches * 5 * indicators['weight']
            
            # Check question patterns
            pattern_matches = sum(1 for pattern in indicators['question_patterns']
                                if re.search(pattern, text_lower, re.IGNORECASE))
            scores[lang] += pattern_matches * 10 * indicators['weight']
        
        # Special cases for very short queries
        if len(text.split()) <= 3:
            # Look for specific greeting patterns
            if any(greeting in text_lower for greeting in ['merhaba', 'selam', 'nasılsın']):
                scores['tr'] += 50
            elif any(greeting in text_lower for greeting in ['bonjour', 'salut', 'bonsoir']):
                scores['fr'] += 50
            elif any(greeting in text_lower for greeting in ['hello', 'hi', 'hey']):
                scores['en'] += 50
        
        # Find language with highest score
        detected_lang = max(scores, key=scores.get)
        max_score = scores[detected_lang]
        
        # Calculate confidence (0-1 scale)
        total_score = sum(scores.values())
        confidence = max_score / total_score if total_score > 0 else 0
        
        # If confidence is too low, check for strong indicators
        if confidence < 0.6:
            # Check for very strong Turkish indicators
            if any(char in text for char in ['ş', 'ğ', 'ı']):
                return 'tr', 0.9
            # Check for strong French indicators
            elif any(phrase in text_lower for phrase in ['s\'il vous plaît', 'qu\'est-ce', 'est-ce que']):
                return 'fr', 0.9
        
        return detected_lang, confidence
    
    def get_language_instruction(self, detected_language: str, confidence: float) -> str:
        """
        Get language-specific instruction for the AI model
        """
        if confidence < 0.5:
            # Low confidence, provide multi-language instruction
            return """
IMPORTANT: The user's language is unclear. Analyze the query carefully and respond in the same language.
If the query contains Turkish words or characters (ş, ğ, ı, ö, ü, ç), respond in Turkish.
If the query contains French words or accents (é, è, à, ç), respond in French.
Otherwise, respond in English.
NEVER mix languages in your response.
"""
        
        return self.language_prompts.get(detected_language, self.language_prompts['fr'])
    
    def enhance_prompt_with_language(self, system_prompt: str, user_query: str) -> str:
        """
        Enhance system prompt with language detection and instructions
        """
        detected_lang, confidence = self.detect_language(user_query)
        language_instruction = self.get_language_instruction(detected_lang, confidence)
        
        # Add language instruction at the beginning AND end for emphasis
        enhanced_prompt = f"""{language_instruction}

{system_prompt}

{language_instruction}

Remember: Your ENTIRE response must be in {self._get_language_name(detected_lang)}. Do not use any words from other languages."""
        
        return enhanced_prompt, detected_lang, confidence
    
    def _get_language_name(self, lang_code: str) -> str:
        """Get full language name from code"""
        language_names = {
            'tr': 'Turkish',
            'fr': 'French', 
            'en': 'English'
        }
        return language_names.get(lang_code, 'the detected language')
    
    def validate_response_language(self, response: str, expected_lang: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if response is in the expected language
        Returns: (is_correct_language, detected_response_language)
        """
        detected_lang, confidence = self.detect_language(response)
        
        # Allow some flexibility for technical responses
        if confidence < 0.3:
            return True, expected_lang  # Too many technical terms to be sure
        
        return detected_lang == expected_lang, detected_lang
    
    def get_test_phrases(self) -> Dict[str, Dict[str, str]]:
        """Get test phrases for each language"""
        return {
            'tr': {
                'greeting': 'Merhaba, nasılsın?',
                'question': 'NETZ hangi hizmetleri sunuyor?',
                'technical': 'Python programlama eğitimi var mı?'
            },
            'fr': {
                'greeting': 'Bonjour, comment allez-vous?',
                'question': 'Quels services propose NETZ?',
                'technical': 'Avez-vous une formation Python?'
            },
            'en': {
                'greeting': 'Hello, how are you?',
                'question': 'What services does NETZ offer?',
                'technical': 'Do you have Python training?'
            }
        }

# Singleton instance
_language_detector = None

def get_language_detector() -> LanguageDetectionSystem:
    """Get singleton instance of language detector"""
    global _language_detector
    if _language_detector is None:
        _language_detector = LanguageDetectionSystem()
    return _language_detector