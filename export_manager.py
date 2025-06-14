import json
import csv
import pandas as pd
from typing import List
from flashcard_generator import Flashcard

class ExportManager:
    """Handles exporting flashcards to different formats"""
    
    @staticmethod
    def to_json(flashcards: List[Flashcard], filename: str = "flashcards.json") -> str:
        """Export flashcards to JSON format"""
        data = []
        for card in flashcards:
            data.append({
                "question": card.question,
                "answer": card.answer,
                "difficulty": card.difficulty,
                "topic": card.topic
            })
        
        json_content = json.dumps(data, indent=2, ensure_ascii=False)
        return json_content
    
    @staticmethod
    def to_csv(flashcards: List[Flashcard], filename: str = "flashcards.csv") -> str:
        """Export flashcards to CSV format"""
        data = []
        for card in flashcards:
            data.append({
                "Question": card.question,
                "Answer": card.answer,
                "Difficulty": card.difficulty,
                "Topic": card.topic
            })
        
        df = pd.DataFrame(data)
        return df.to_csv(index=False)
    
    @staticmethod
    def to_anki(flashcards: List[Flashcard], filename: str = "flashcards_anki.txt") -> str:
        """Export flashcards to Anki format (tab-separated)"""
        lines = []
        for card in flashcards:
            # Anki format: Front\tBack\tTags
            tags = f"{card.difficulty.lower()}"
            if card.topic:
                tags += f" {card.topic.lower().replace(' ', '_')}"
            
            line = f"{card.question}\t{card.answer}\t{tags}"
            lines.append(line)
        
        return "\n".join(lines)
    
    @staticmethod
    def to_quizlet(flashcards: List[Flashcard], filename: str = "flashcards_quizlet.txt") -> str:
        """Export flashcards to Quizlet format"""
        lines = []
        for card in flashcards:
            # Quizlet format: Term\tDefinition
            line = f"{card.question}\t{card.answer}"
            lines.append(line)
        
        return "\n".join(lines)
