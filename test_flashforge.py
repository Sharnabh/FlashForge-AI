"""
Test script for FlashForge AI components
"""
import unittest
from flashcard_generator import FlashcardGenerator, Flashcard
from file_handler import FileHandler
from export_manager import ExportManager
import json
import tempfile
import os

class TestFlashForgeAI(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_content = """
        Photosynthesis is the process by which plants convert light energy into chemical energy.
        The overall equation is: 6CO2 + 6H2O + light energy → C6H12O6 + 6O2
        
        There are two main stages:
        1. Light-dependent reactions occur in thylakoids
        2. Light-independent reactions (Calvin cycle) occur in stroma
        """
        
        self.sample_flashcards = [
            Flashcard("What is photosynthesis?", 
                     "The process by which plants convert light energy into chemical energy", 
                     "Easy", "Biology"),
            Flashcard("Where do light-dependent reactions occur?", 
                     "In the thylakoids", 
                     "Medium", "Biology")
        ]
    
    def test_flashcard_creation(self):
        """Test Flashcard dataclass creation"""
        card = Flashcard("Test question", "Test answer", "Easy", "Test Topic")
        self.assertEqual(card.question, "Test question")
        self.assertEqual(card.answer, "Test answer")
        self.assertEqual(card.difficulty, "Easy")
        self.assertEqual(card.topic, "Test Topic")
    
    def test_text_cleaning(self):
        """Test text cleaning functionality"""
        # This requires a FlashcardGenerator instance
        # We'll create a mock test since we need API key for real instance
        pass
    
    def test_export_json(self):
        """Test JSON export functionality"""
        json_content = ExportManager.to_json(self.sample_flashcards)
        parsed = json.loads(json_content)
        
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["question"], "What is photosynthesis?")
        self.assertEqual(parsed[0]["difficulty"], "Easy")
    
    def test_export_csv(self):
        """Test CSV export functionality"""
        csv_content = ExportManager.to_csv(self.sample_flashcards)
        lines = csv_content.strip().split('\n')
        
        # Should have header + 2 data rows
        self.assertEqual(len(lines), 3)
        self.assertIn("Question", lines[0])  # Header
        self.assertIn("photosynthesis", lines[1])  # First card
    
    def test_export_anki(self):
        """Test Anki export functionality"""
        anki_content = ExportManager.to_anki(self.sample_flashcards)
        lines = anki_content.strip().split('\n')
        
        self.assertEqual(len(lines), 2)
        # Anki format: Question\tAnswer\tTags
        first_line = lines[0].split('\t')
        self.assertEqual(len(first_line), 3)
        self.assertEqual(first_line[0], "What is photosynthesis?")
    
    def test_file_handler_txt(self):
        """Test text file handling"""
        test_content = "This is a test content"
        content_bytes = test_content.encode('utf-8')
        
        result = FileHandler.extract_text_from_txt(content_bytes)
        self.assertEqual(result, test_content)
    
    def test_validation(self):
        """Test flashcard validation"""
        valid_cards = [
            Flashcard("Good question?", "Good answer", "Easy", "Topic"),
            Flashcard("Another question?", "Another answer", "Medium", "Topic")
        ]
        
        invalid_cards = [
            Flashcard("", "Answer", "Easy", "Topic"),  # Empty question
            Flashcard("Question?", "", "Easy", "Topic"),  # Empty answer
            Flashcard("Q", "A", "Invalid", "Topic")  # Invalid difficulty
        ]
        
        # This test would require FlashcardGenerator instance
        # We'll create a simple validation function for testing
        def validate_card(card):
            return (len(card.question.strip()) > 10 and 
                   len(card.answer.strip()) > 5 and
                   card.difficulty in ["Easy", "Medium", "Hard"])
        
        for card in valid_cards:
            self.assertTrue(validate_card(card))
        
        for card in invalid_cards:
            self.assertFalse(validate_card(card))

def run_basic_tests():
    """Run basic tests without unittest framework"""
    print("🧪 Running FlashForge AI Tests")
    print("=" * 40)
    
    try:
        # Test 1: Flashcard creation
        print("✓ Testing Flashcard creation...")
        card = Flashcard("Test question", "Test answer", "Easy", "Test Topic")
        assert card.question == "Test question"
        print("  ✓ Flashcard creation works")
        
        # Test 2: Export functionality
        print("✓ Testing export functionality...")
        sample_cards = [
            Flashcard("What is AI?", "Artificial Intelligence", "Easy", "Technology"),
            Flashcard("Define machine learning", "A subset of AI that learns from data", "Medium", "Technology")
        ]
        
        # Test JSON export
        json_content = ExportManager.to_json(sample_cards)
        parsed = json.loads(json_content)
        assert len(parsed) == 2
        print("  ✓ JSON export works")
        
        # Test CSV export
        csv_content = ExportManager.to_csv(sample_cards)
        assert "Question" in csv_content
        assert "Answer" in csv_content
        print("  ✓ CSV export works")
        
        # Test Anki export
        anki_content = ExportManager.to_anki(sample_cards)
        lines = anki_content.strip().split('\n')
        assert len(lines) == 2
        print("  ✓ Anki export works")
        
        # Test 3: File handling
        print("✓ Testing file handling...")
        test_content = "This is test educational content for flashcard generation."
        content_bytes = test_content.encode('utf-8')
        result = FileHandler.extract_text_from_txt(content_bytes)
        assert result == test_content
        print("  ✓ Text file handling works")
        
        print("\n🎉 All basic tests passed!")
        print("=" * 40)
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    # Run basic tests first
    success = run_basic_tests()
    
    if success:
        print("\n🧪 Running detailed unittest suite...")
        # Only run unittest if basic tests pass
        try:
            unittest.main(verbosity=2, exit=False)
        except SystemExit:
            pass  # unittest calls sys.exit, we want to prevent that
    else:
        print("❌ Basic tests failed, skipping unittest suite")
