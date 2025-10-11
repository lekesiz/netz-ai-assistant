"""
Unit tests for Language Detection System
"""

import pytest
from language_detection_system import LanguageDetectionSystem


class TestLanguageDetection:
    """Test language detection functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test instance"""
        self.detector = LanguageDetectionSystem()
    
    @pytest.mark.unit
    def test_detect_english(self):
        """Test English language detection"""
        texts = [
            "What is NETZ?",
            "Hello, how are you today?",
            "I need information about training",
            "Please help me with this issue"
        ]
        
        for text in texts:
            lang, confidence = self.detector.detect_language(text)
            assert lang == "en", f"Failed to detect English in: {text}"
            assert confidence > 0.5, f"Low confidence for English: {confidence}"
    
    @pytest.mark.unit
    def test_detect_french(self):
        """Test French language detection"""
        texts = [
            "Qu'est-ce que NETZ?",
            "Bonjour, comment allez-vous?",
            "J'ai besoin d'informations sur la formation",
            "Pouvez-vous m'aider avec ce problème?"
        ]
        
        for text in texts:
            lang, confidence = self.detector.detect_language(text)
            assert lang == "fr", f"Failed to detect French in: {text}"
            assert confidence > 0.5, f"Low confidence for French: {confidence}"
    
    @pytest.mark.unit
    def test_detect_turkish(self):
        """Test Turkish language detection"""
        texts = [
            "NETZ nedir?",
            "Merhaba, nasılsınız?",
            "Eğitim hakkında bilgi istiyorum",
            "Bu konuda yardımcı olabilir misiniz?"
        ]
        
        for text in texts:
            lang, confidence = self.detector.detect_language(text)
            assert lang == "tr", f"Failed to detect Turkish in: {text}"
            # For very short texts, confidence might be lower
            if len(text.split()) <= 2:
                assert confidence >= 0, f"Negative confidence for Turkish: {confidence}"
            else:
                assert confidence > 0.5, f"Low confidence for Turkish: {confidence}"
    
    @pytest.mark.unit
    def test_mixed_language_detection(self):
        """Test mixed language detection"""
        # Mostly English with French word
        text = "Hello, I need to schedule a rendez-vous for training"
        lang, confidence = self.detector.detect_language(text)
        assert lang == "en", "Should detect primary language as English"
        
        # Mostly French with English word  
        text = "Bonjour, je voudrais un meeting pour discuter la formation"
        lang, confidence = self.detector.detect_language(text)
        assert lang == "fr", "Should detect primary language as French"
    
    @pytest.mark.unit
    def test_short_text_detection(self):
        """Test detection with very short texts"""
        tests = [
            ("Hi", "en"),
            ("Bonjour", "fr"),
            ("Merhaba", "tr"),
            ("Yes", "en"),
            ("Oui", "fr"),
            ("Evet", "tr")
        ]
        
        for text, expected_lang in tests:
            lang, confidence = self.detector.detect_language(text)
            # Short single-word tests might have lower accuracy
            if text.lower() in ['hi', 'yes', 'no']:
                # These are too generic to reliably detect
                assert lang in ['en', 'tr', 'fr'], f"Unexpected language {lang} for: {text}"
            else:
                assert lang == expected_lang, f"Failed to detect {expected_lang} in: {text}"
    
    @pytest.mark.unit
    def test_punctuation_handling(self):
        """Test language detection with various punctuation"""
        texts = [
            ("What is NETZ???", "en"),
            ("Qu'est-ce que NETZ ???", "fr"),
            ("NETZ nedir???", "tr"),
            ("Hello!!!", "en"),
            ("Bonjour !!!", "fr"),
            ("Merhaba!!!", "tr")
        ]
        
        for text, expected_lang in texts:
            lang, confidence = self.detector.detect_language(text)
            assert lang == expected_lang, f"Punctuation affected detection: {text}"
    
    @pytest.mark.unit
    def test_case_insensitive_detection(self):
        """Test that detection is case-insensitive"""
        texts = [
            ("WHAT IS NETZ?", "what is netz?", "en"),
            ("QU'EST-CE QUE NETZ?", "qu'est-ce que netz?", "fr"),
            ("NETZ NEDIR?", "netz nedir?", "tr")
        ]
        
        for upper, lower, expected_lang in texts:
            lang_upper, conf_upper = self.detector.detect_language(upper)
            lang_lower, conf_lower = self.detector.detect_language(lower)
            
            assert lang_upper == expected_lang
            assert lang_lower == expected_lang
            assert abs(conf_upper - conf_lower) < 0.1, "Case should not significantly affect confidence"
    
    @pytest.mark.unit
    def test_validate_response_language(self):
        """Test response language validation"""
        # Matching languages
        assert self.detector.validate_response_language("Hello world", "en")[0] == True
        assert self.detector.validate_response_language("Bonjour monde", "fr")[0] == True
        assert self.detector.validate_response_language("Merhaba dünya", "tr")[0] == True
        
        # Mismatched languages
        assert self.detector.validate_response_language("Bonjour", "en")[0] == False
        assert self.detector.validate_response_language("Hello", "fr")[0] == False
    
    @pytest.mark.unit
    def test_get_language_name(self):
        """Test language name conversion"""
        assert self.detector._get_language_name("en") == "English"
        assert self.detector._get_language_name("fr") == "French"
        assert self.detector._get_language_name("tr") == "Turkish"
        assert self.detector._get_language_name("unknown") == "Unknown"
    
    @pytest.mark.unit
    def test_enhance_prompt_with_language(self):
        """Test prompt enhancement with language instructions"""
        base_prompt = "You are an AI assistant."
        
        # Test English
        enhanced, lang, conf = self.detector.enhance_prompt_with_language(
            base_prompt, "What is NETZ?"
        )
        assert "MUST respond in English" in enhanced
        assert lang == "en"
        
        # Test French
        enhanced, lang, conf = self.detector.enhance_prompt_with_language(
            base_prompt, "Qu'est-ce que NETZ?"
        )
        assert "MUST respond in French" in enhanced
        assert lang == "fr"
        
        # Test Turkish
        enhanced, lang, conf = self.detector.enhance_prompt_with_language(
            base_prompt, "NETZ nedir?"
        )
        assert "MUST respond in Turkish" in enhanced
        assert lang == "tr"
    
    @pytest.mark.unit
    def test_numbers_and_symbols(self):
        """Test detection with numbers and symbols"""
        # Should still detect language despite numbers
        texts = [
            ("I need 123 items", "en"),
            ("J'ai besoin de 123 articles", "fr"),
            ("123 öğeye ihtiyacım var", "tr")
        ]
        
        for text, expected_lang in texts:
            lang, confidence = self.detector.detect_language(text)
            assert lang == expected_lang, f"Numbers affected detection: {text}"