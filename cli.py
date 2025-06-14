"""
CLI version of FlashForge AI for testing and demonstration
"""
import sys
import os
from pathlib import Path
from flashcard_generator import FlashcardGenerator, Flashcard
from file_handler import FileHandler
from export_manager import ExportManager

def main():
    print("🎯 FlashForge AI - CLI Version")
    print("=" * 50)
    
    # Get API key
    api_key = input("Enter your OpenAI API key: ").strip()
    if not api_key:
        print("❌ API key is required!")
        return
    
    # Choose input method
    print("\nChoose input method:")
    print("1. File upload")
    print("2. Direct text input")
    print("3. Use sample content")
    
    choice = input("Select option (1-3): ").strip()
    
    content = ""
    subject_type = "General"
    
    if choice == "1":
        file_path = input("Enter file path: ").strip()
        try:
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                return
            
            with open(file_path, 'rb') as f:
                # Create a mock uploaded file object
                class MockFile:
                    def __init__(self, path, content):
                        self.name = os.path.basename(path)
                        self.content = content
                    
                    def read(self):
                        return self.content
                
                file_content = f.read()
                mock_file = MockFile(file_path, file_content)
                filename, content = FileHandler.process_uploaded_file(mock_file)
                print(f"✅ Processed file: {filename}")
                
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return
    
    elif choice == "2":
        print("\nEnter your educational content (press Ctrl+Z on Windows or Ctrl+D on Unix when done):")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            content = '\n'.join(lines)
    
    elif choice == "3":
        print("\nAvailable sample content:")
        print("1. Biology - Photosynthesis")
        print("2. Computer Science - Data Structures")
        
        sample_choice = input("Select sample (1-2): ").strip()
        
        if sample_choice == "1":
            content_file = "sample_biology_content.txt"
            subject_type = "Biology"
        elif sample_choice == "2":
            content_file = "sample_cs_content.txt"
            subject_type = "Computer Science"
        else:
            print("❌ Invalid choice!")
            return
        
        try:
            with open(content_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✅ Loaded sample content from {content_file}")
        except Exception as e:
            print(f"❌ Error loading sample: {e}")
            return
    
    else:
        print("❌ Invalid choice!")
        return
    
    if not content.strip():
        print("❌ No content provided!")
        return
    
    # Get subject type if not already set
    if subject_type == "General":
        print("\nSubject types:")
        subjects = ["General", "Biology", "History", "Computer Science", "Mathematics", "Physics", "Chemistry", "Literature"]
        for i, subj in enumerate(subjects, 1):
            print(f"{i}. {subj}")
        
        try:
            subj_choice = int(input("Select subject (1-8): ")) - 1
            if 0 <= subj_choice < len(subjects):
                subject_type = subjects[subj_choice]
        except ValueError:
            pass
    
    # Get number of flashcards
    try:
        num_cards = int(input("Number of flashcards to generate (5-20, default 12): ") or "12")
        num_cards = max(5, min(20, num_cards))
    except ValueError:
        num_cards = 12
    
    print(f"\n🚀 Generating {num_cards} {subject_type} flashcards...")
    print("This may take 10-30 seconds...")
    
    try:
        generator = FlashcardGenerator(api_key)
        flashcards = generator.generate_flashcards(
            content=content,
            subject_type=subject_type,
            num_cards=num_cards,
            include_topics=True
        )
        
        valid_flashcards = generator.validate_flashcards(flashcards)
        
        if not valid_flashcards:
            print("❌ No valid flashcards could be generated!")
            return
        
        print(f"\n✅ Generated {len(valid_flashcards)} flashcards!")
        print("=" * 50)
        
        # Display flashcards
        for i, card in enumerate(valid_flashcards, 1):
            print(f"\n📇 FLASHCARD {i}")
            print(f"Topic: {card.topic}")
            print(f"Difficulty: {card.difficulty}")
            print(f"Question: {card.question}")
            print(f"Answer: {card.answer}")
            print("-" * 30)
        
        # Export options
        print("\n📤 Export Options:")
        print("1. JSON")
        print("2. CSV") 
        print("3. Anki")
        print("4. Quizlet")
        print("5. Skip export")
        
        export_choice = input("Select export format (1-5): ").strip()
        
        if export_choice == "1":
            content = ExportManager.to_json(valid_flashcards)
            filename = "flashcards.json"
        elif export_choice == "2":
            content = ExportManager.to_csv(valid_flashcards)
            filename = "flashcards.csv"
        elif export_choice == "3":
            content = ExportManager.to_anki(valid_flashcards)
            filename = "flashcards_anki.txt"
        elif export_choice == "4":
            content = ExportManager.to_quizlet(valid_flashcards)
            filename = "flashcards_quizlet.txt"
        else:
            print("✅ Flashcards generated successfully!")
            return
        
        # Save file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Flashcards exported to {filename}")
        
    except Exception as e:
        print(f"❌ Error generating flashcards: {e}")

if __name__ == "__main__":
    main()
