print("FlashForge AI Demo")
print("==================")
from flashcard_generator import Flashcard
from export_manager import ExportManager

# Create sample flashcards
cards = [
    Flashcard("What is AI?", "Artificial Intelligence", "Easy", "Technology"),
    Flashcard("Define ML?", "Machine Learning - subset of AI", "Medium", "Technology")
]

print(f"Created {len(cards)} flashcards")
print("JSON export working:", len(ExportManager.to_json(cards)) > 0)
print("Demo complete!")
