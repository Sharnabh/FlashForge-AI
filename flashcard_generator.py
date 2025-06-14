import openai
import json
import re
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class Flashcard:
    """Data class for flashcard representation"""
    question: str
    answer: str
    difficulty: str = "Medium"
    topic: str = ""

class FlashcardGenerator:
    """Core flashcard generation logic using OpenAI"""
    
    def __init__(self, api_key: str):
        """Initialize with OpenAI API key"""
        self.client = openai.OpenAI(api_key=api_key)
        
    def generate_flashcards(
        self, 
        content: str, 
        subject_type: str = "General",
        num_cards: int = 12,
        include_topics: bool = True
    ) -> List[Flashcard]:
        """Generate flashcards from content using OpenAI"""
        
        if not content.strip():
            raise ValueError("Content cannot be empty")
        
        # Create optimized prompt
        prompt = self._create_prompt(content, subject_type, num_cards, include_topics)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert educational content creator specializing in creating effective flashcards for learning."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            flashcards_text = response.choices[0].message.content
            return self._parse_flashcards(flashcards_text)
            
        except Exception as e:
            raise Exception(f"Error generating flashcards: {str(e)}")
    
    def _create_prompt(self, content: str, subject_type: str, num_cards: int, include_topics: bool) -> str:
        """Create optimized prompt for flashcard generation"""
        
        topic_instruction = ""
        if include_topics:
            topic_instruction = "\n- Include a relevant topic/category for each flashcard"
        
        # Subject-specific guidance
        subject_guidance = {
            "Biology": "Focus on biological processes, terminology, systems, and relationships between concepts.",
            "History": "Focus on dates, events, causes and effects, key figures, and historical significance.",
            "Computer Science": "Focus on algorithms, data structures, programming concepts, complexity analysis, and technical definitions.",
            "Mathematics": "Focus on formulas, theorems, problem-solving methods, and mathematical relationships.",
            "Physics": "Focus on laws, formulas, phenomena, experiments, and physical relationships.",
            "Chemistry": "Focus on chemical reactions, compounds, elements, bonding, and chemical processes.",
            "Literature": "Focus on themes, characters, literary devices, plot elements, and author techniques."
        }
        
        specific_guidance = subject_guidance.get(subject_type, "Focus on key concepts, definitions, and important relationships.")
        
        prompt = f"""Create {num_cards} high-quality flashcards from the following {subject_type} educational content.

SUBJECT-SPECIFIC GUIDANCE:
{specific_guidance}

REQUIREMENTS:
- Generate exactly {num_cards} flashcards
- Each flashcard should have: Question, Answer, Difficulty (Easy/Medium/Hard){topic_instruction}
- Questions should be clear, specific, and test understanding (not just memorization)
- Answers should be complete, accurate, and self-contained
- Vary difficulty levels: ~30% Easy, ~50% Medium, ~20% Hard
- Cover the most important concepts, avoiding trivial details
- Use active voice and clear language
- Ensure questions are answerable from the provided content

DIFFICULTY GUIDELINES:
- Easy: Basic definitions, simple facts, direct recall
- Medium: Understanding relationships, applying concepts, explanations
- Hard: Analysis, synthesis, complex problem-solving, critical thinking

STRICT FORMAT (follow exactly):
FLASHCARD 1:
Question: [Clear, specific question]
Answer: [Complete, accurate answer]
Difficulty: [Easy/Medium/Hard]
Topic: [Relevant topic/category]

FLASHCARD 2:
Question: [Clear, specific question]
Answer: [Complete, accurate answer]  
Difficulty: [Easy/Medium/Hard]
Topic: [Relevant topic/category]

CONTENT TO PROCESS:
{content[:3500]}

Generate the flashcards now following the exact format above:"""
        return prompt
    
    def _parse_flashcards(self, response_text: str) -> List[Flashcard]:
        """Parse flashcards from LLM response with improved robustness"""
        flashcards = []
        
        # Clean up the response text
        response_text = response_text.strip()
        
        # Split by flashcard markers - try multiple patterns
        card_blocks = []
        
        # Pattern 1: FLASHCARD N:
        if "FLASHCARD" in response_text:
            card_blocks = re.split(r'FLASHCARD\s+\d+:', response_text)[1:]
        
        # Pattern 2: Card N: or numbered lists
        elif re.search(r'Card\s+\d+:|^\d+\.', response_text, re.MULTILINE):
            card_blocks = re.split(r'(?:Card\s+\d+:|\d+\.)', response_text)[1:]
        
        # Pattern 3: Just split by multiple newlines if no clear markers
        else:
            # Try to split by double newlines and look for question/answer patterns
            potential_blocks = response_text.split('\n\n')
            card_blocks = [block for block in potential_blocks if 'Question:' in block and 'Answer:' in block]
        
        for block in card_blocks:
            try:
                # Extract question - multiple patterns
                question = ""
                question_patterns = [
                    r'Question:\s*(.+?)(?=\nAnswer:|Answer:)',
                    r'Q:\s*(.+?)(?=\nA:|A:)',
                    r'Question:\s*(.+?)(?=\n|$)'
                ]
                
                for pattern in question_patterns:
                    question_match = re.search(pattern, block, re.DOTALL | re.IGNORECASE)
                    if question_match:
                        question = question_match.group(1).strip()
                        break
                
                # Extract answer - multiple patterns  
                answer = ""
                answer_patterns = [
                    r'Answer:\s*(.+?)(?=\nDifficulty:|Difficulty:)',
                    r'A:\s*(.+?)(?=\nDifficulty:|Difficulty:)',
                    r'Answer:\s*(.+?)(?=\n|$)'
                ]
                
                for pattern in answer_patterns:
                    answer_match = re.search(pattern, block, re.DOTALL | re.IGNORECASE)
                    if answer_match:
                        answer = answer_match.group(1).strip()
                        break
                
                # Extract difficulty
                difficulty = "Medium"  # default
                difficulty_patterns = [
                    r'Difficulty:\s*(.+?)(?=\nTopic:|Topic:|$)',
                    r'Level:\s*(.+?)(?=\nTopic:|Topic:|$)'
                ]
                
                for pattern in difficulty_patterns:
                    difficulty_match = re.search(pattern, block, re.DOTALL | re.IGNORECASE)
                    if difficulty_match:
                        diff_text = difficulty_match.group(1).strip()
                        if diff_text in ["Easy", "Medium", "Hard"]:
                            difficulty = diff_text
                        break
                
                # Extract topic (optional)
                topic = ""
                topic_patterns = [
                    r'Topic:\s*(.+?)(?=\n|$)',
                    r'Category:\s*(.+?)(?=\n|$)'
                ]
                
                for pattern in topic_patterns:
                    topic_match = re.search(pattern, block, re.DOTALL | re.IGNORECASE)
                    if topic_match:
                        topic = topic_match.group(1).strip()
                        break
                
                # Clean up extracted text
                question = self._clean_text(question)
                answer = self._clean_text(answer)
                topic = self._clean_text(topic)
                
                if question and answer:
                    flashcards.append(Flashcard(
                        question=question,
                        answer=answer,
                        difficulty=difficulty,
                        topic=topic
                    ))
            except Exception as e:
                continue  # Skip malformed cards
        
        return flashcards
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove markdown formatting
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.+?)\*', r'\1', text)      # Italic
        text = re.sub(r'`(.+?)`', r'\1', text)        # Code
        
        # Remove leading/trailing punctuation if it seems erroneous
        text = re.sub(r'^[^\w\s]+|[^\w\s.!?]+$', '', text)
        
        return text
    
    def validate_flashcards(self, flashcards: List[Flashcard]) -> List[Flashcard]:
        """Validate and clean flashcards"""
        valid_cards = []
        
        for card in flashcards:
            # Basic validation
            if (len(card.question.strip()) > 10 and 
                len(card.answer.strip()) > 5 and
                card.difficulty in ["Easy", "Medium", "Hard"]):
                valid_cards.append(card)
        
        return valid_cards
