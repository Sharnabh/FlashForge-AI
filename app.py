import streamlit as st
import os
import tempfile
import warnings
import requests
import json
import PyPDF2
import docx
import csv
import io
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import time

# Filter out the legacy warning
warnings.filterwarnings("ignore", message=".*legacy.*")

# Set page config
st.set_page_config(page_title="FlashForge-AI", layout="wide")

# Custom CSS for enhanced styling
st.markdown("""
    <style>
        /* Main theme colors */
        :root {
            --primary-color: #6B46C1;
            --secondary-color: #805AD5;
            --accent-color: #9F7AEA;
            --background-color: #F7FAFC;
            --text-color: #2D3748;
            --card-bg: #FFFFFF;
            --card-text: #2D3748;
            --gradient-start: #6B46C1;
            --gradient-end: #9F7AEA;
        }

        /* Global styles */
        .stApp {
            background-color: var(--background-color);
        }

        /* Main container background */
        .main .block-container {
            background-color: var(--background-color);
            padding: 2rem;
        }

        /* Sidebar background */
        .css-1d391kg, .css-1siy2j7 {
            background-color: var(--background-color) !important;
        }

        /* Title styling */
        h1 {
            color: var(--primary-color);
            font-size: 3rem !important;
            font-weight: 700 !important;
            text-align: center;
            padding: 1rem;
            margin-bottom: 2rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }

        /* Subheader styling */
        h3 {
            color: var(--primary-color);
            font-weight: 600 !important;
        }

        /* Sidebar styling */
        .css-1d391kg {
            background-color: var(--card-bg);
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, var(--gradient-start), var(--gradient-end));
            color: white !important;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: all 0.3s ease;
        }

        .stButton > button:hover {
            background: linear-gradient(135deg, var(--gradient-end), var(--gradient-start));
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }

        /* Card styling */
        .card-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }

        .card {
            perspective: 1000px;
            min-height: 200px;
            margin: 10px;
        }

        .card-inner {
            position: relative;
            width: 100%;
            height: 100%;
            min-height: 200px;
            text-align: center;
            transition: transform 0.6s;
            transform-style: preserve-3d;
            cursor: pointer;
        }

        .card:hover .card-inner {
            transform: rotateY(180deg);
        }

        .card-front, .card-back {
            position: absolute;
            width: 100%;
            height: 100%;
            backface-visibility: hidden;
            border-radius: 15px;
            padding: 20px;
            box-sizing: border-box;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--card-bg);
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }

        .card-front {
            background: linear-gradient(135deg, var(--gradient-start), var(--gradient-end));
            color: white;
        }

        .card-back {
            background: linear-gradient(135deg, var(--gradient-end), var(--gradient-start));
            color: white;
            transform: rotateY(180deg);
        }

        .card-content {
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }

        .card h3 {
            margin: 0;
            font-size: 1.2em;
            line-height: 1.4;
            max-width: 100%;
            color: white;
        }

        /* File uploader styling */
        .stFileUploader > div {
            background-color: var(--card-bg);
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border: 2px solid var(--accent-color);
        }

        /* Text area styling */
        .stTextArea > div > div {
            background-color: var(--card-bg);
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border: 2px solid var(--accent-color);
        }

        /* Slider container styling */
        .stSlider > div {
            background-color: var(--card-bg);
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 0.5rem 0;
            border: 2px solid var(--accent-color);
        }

        /* Slider track */
        .stSlider > div > div > div {
            height: 4px;
            border-radius: 2px;
            background: linear-gradient(to right, var(--gradient-start), var(--gradient-end));
        }

        /* Slider thumb */
        .stSlider > div > div > div > div {
            background-color: var(--primary-color);
            border: 2px solid white;
            box-shadow: 0 0 5px rgba(0,0,0,0.2);
        }

        /* Radio button styling */
        .stRadio > div {
            background-color: var(--card-bg);
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border: 2px solid var(--accent-color);
        }

        /* Export buttons styling */
        .export-button {
            background: linear-gradient(135deg, var(--gradient-start), var(--gradient-end));
            color: white !important;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            margin: 0.5rem 0;
            width: 100%;
            transition: all 0.3s ease;
        }

        .export-button:hover {
            background: linear-gradient(135deg, var(--gradient-end), var(--gradient-start));
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }

        /* Text color for all elements */
        .stMarkdown, .stText, .stTextInput, .stTextArea {
            color: var(--text-color);
        }

        /* Ensure text is visible in all states */
        .stButton > button, .stRadio > div, .stSlider > div, .stTextArea > div > div {
            color: var(--text-color) !important;
        }

        /* Radio button text color */
        .stRadio > div > div > div {
            color: var(--text-color) !important;
        }

        /* Slider text color */
        .stSlider > div > div > div > div > div {
            color: var(--text-color) !important;
        }

        @media (min-width: 1200px) {
            .card-container {
                grid-template-columns: repeat(3, 1fr);
            }
        }

        /* Edit mode styles */
        .stExpander {
            background-color: var(--card-bg);
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem 0;
            border: 2px solid var(--accent-color);
        }
        
        .stExpander:hover {
            border-color: var(--primary-color);
        }
        
        /* Text area styling in edit mode */
        .stTextArea > div > div {
            background-color: var(--card-bg);
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border: 2px solid var(--accent-color);
            min-height: 100px;
        }
        
        /* Delete button styling */
        .stButton > button[data-testid="baseButton-secondary"] {
            background-color: #E53E3E !important;
            color: white !important;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: all 0.3s ease;
        }
        
        .stButton > button[data-testid="baseButton-secondary"]:hover {
            background-color: #C53030 !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        /* Checkbox styling */
        .stCheckbox > div {
            background-color: var(--card-bg);
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border: 2px solid var(--accent-color);
            margin: 1rem 0;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize Together AI API
@st.cache_resource
def init_together():
    try:
        api_key = st.secrets["TOGETHER_API_KEY"]
        return api_key
    except Exception as e:
        st.error(f"Error initializing Together AI: {str(e)}")
        return None

api_key = init_together()

# Function to chunk text into smaller pieces
def chunk_text(text, chunk_size=1000, overlap=100):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def generate_with_together(prompt, max_tokens=1024):
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 50,
            "repetition_penalty": 1.1,
            "stop": ["</s>", "[INST]"]
        }
        
        print("\nSending request to Together AI...")
        response = requests.post(
            "https://api.together.xyz/v1/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()["choices"][0]["text"].strip()
            print(f"\nTogether AI Response: {result}")
            return result
        else:
            print(f"\nError: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"\nError in generate_with_together: {str(e)}")
        return None

# Function to generate Q&A pairs for a single chunk
def generate_qa_for_chunk(chunk, num_questions, difficulty, subject):
    try:
        # Prepare the prompt with Llama 3.3's instruction format and subject-specific guidance
        prompt = f"""<s>[INST] <<SYS>>
You are a helpful AI assistant that creates educational flashcards for {subject}. Your task is to create exactly {num_questions} {difficulty.lower()} difficulty questions and answers based on the provided text.

IMPORTANT: You must format each question and answer pair exactly like this:
Q: [Your question here]
A: [Your answer here]

Rules:
1. Each question must start with "Q: "
2. Each answer must start with "A: "
3. Create exactly {num_questions} pairs
4. Make questions {difficulty.lower()} difficulty
5. Keep answers concise but informative
6. Focus on different aspects of the text than the previous questions
7. Format questions and answers appropriately for {subject}:
   - For Biology: Include scientific terms and concepts
   - For History: Include dates, events, and historical context
   - For Computer Science: Include technical terms and programming concepts
   - For Mathematics: Include formulas and step-by-step solutions
   - For Literature: Include themes, characters, and literary devices
   - For General: Focus on key concepts and main ideas
<</SYS>>

Text to analyze: {chunk}

Now create {num_questions} Q&A pairs following the format above, tailored for {subject}. [/INST]</s>"""
        
        print(f"\nGenerating Q&A for chunk with prompt: {prompt}")
        
        # Generate response using Together AI
        generated_text = generate_with_together(prompt)
        if not generated_text:
            print("\nNo response from Together AI")
            return []
            
        print(f"\nGenerated text: {generated_text}")
        
        # Parse Q&A pairs with more robust parsing
        qa_pairs = []
        lines = generated_text.split('\n')
        current_q = None
        current_a = None
        
        print("\nParsing Q&A pairs...")
        for line in lines:
            line = line.strip()
            if not line:  # Skip empty lines
                continue
                
            if line.startswith('Q:'):
                if current_q and current_a:
                    print(f"Adding pair: Q: {current_q}, A: {current_a}")
                    qa_pairs.append({"question": current_q, "answer": current_a})
                current_q = line[2:].strip()
            elif line.startswith('A:'):
                current_a = line[2:].strip()
            elif current_q and not current_a:  # Handle cases where answer might be on next line without A: prefix
                current_a = line
        
        if current_q and current_a:
            print(f"Adding final pair: Q: {current_q}, A: {current_a}")
            qa_pairs.append({"question": current_q, "answer": current_a})
        
        print(f"\nTotal Q&A pairs found: {len(qa_pairs)}")
        
        # If no pairs were found, try to extract them from the text directly
        if not qa_pairs and '?' in generated_text:
            print("\nNo Q&A pairs found, attempting to extract from text...")
            sentences = generated_text.split('.')
            for i in range(len(sentences)-1):
                if '?' in sentences[i]:
                    qa_pairs.append({
                        "question": sentences[i].strip(),
                        "answer": sentences[i+1].strip()
                    })
        
        return qa_pairs
    except Exception as e:
        print(f"\nError generating Q&A for chunk: {str(e)}")
        st.error(f"Error generating Q&A for chunk: {str(e)}")
        return []

# Function to generate Q&A pairs using parallel processing
@st.cache_data(ttl=3600)  # Cache results for 1 hour
def generate_qa_pairs(text, num_questions, difficulty, subject):
    if not text.strip():
        st.warning("Please provide some text or upload a file.")
        return []
    
    try:
        with st.spinner("Generating questions and answers..."):
            print(f"\nInput text length: {len(text.split())} words")
            
            # Ensure text is not too short
            if len(text.split()) < 50:
                st.warning("The text is too short. Please provide more content.")
                return []
            
            # If text is too long, truncate it to a reasonable size
            max_words = 2000  # Maximum words to process
            words = text.split()
            if len(words) > max_words:
                print(f"\nText too long ({len(words)} words), truncating to {max_words} words...")
                text = " ".join(words[:max_words])
            
            # Generate Q&A pairs in a single query
            print(f"\nGenerating {num_questions} questions...")
            qa_pairs = generate_qa_for_chunk(text, num_questions, difficulty, subject)
            
            print(f"\nTotal Q&A pairs generated: {len(qa_pairs)}")
            
            # If we don't have enough pairs, try generating more with a different prompt
            if len(qa_pairs) < num_questions:
                print("\nNot enough pairs generated, trying to generate more...")
                # Try with a different prompt format
                prompt = f"""<s>[INST] <<SYS>>
You are a helpful AI assistant that creates educational flashcards for {subject}. Your task is to create exactly {num_questions - len(qa_pairs)} {difficulty.lower()} difficulty questions and answers based on the provided text.

IMPORTANT: You must format each question and answer pair exactly like this:
Q: [Your question here]
A: [Your answer here]

Rules:
1. Each question must start with "Q: "
2. Each answer must start with "A: "
3. Create exactly {num_questions - len(qa_pairs)} pairs
4. Make questions {difficulty.lower()} difficulty
5. Keep answers concise but informative
6. Focus on different aspects of the text than the previous questions
7. Format questions and answers appropriately for {subject}:
   - For Biology: Include scientific terms and concepts
   - For History: Include dates, events, and historical context
   - For Computer Science: Include technical terms and programming concepts
   - For Mathematics: Include formulas and step-by-step solutions
   - For Literature: Include themes, characters, and literary devices
   - For General: Focus on key concepts and main ideas
<</SYS>>

Text to analyze: {text}

Now create {num_questions - len(qa_pairs)} Q&A pairs following the format above, tailored for {subject}. [/INST]</s>"""
                
                additional_pairs = generate_qa_for_chunk(text, num_questions - len(qa_pairs), difficulty, subject)
                qa_pairs.extend(additional_pairs)
            
            # Shuffle and limit to requested number of questions
            np.random.shuffle(qa_pairs)
            final_pairs = qa_pairs[:num_questions]
            print(f"\nFinal Q&A pairs: {final_pairs}")
            return final_pairs
    except Exception as e:
        print(f"\nError in generate_qa_pairs: {str(e)}")
        st.error(f"Error generating Q&A pairs: {str(e)}")
        return []

# Function to parse uploaded file
def parse_file(uploaded_file):
    if uploaded_file is None:
        return ""
    try:
        file_extension = uploaded_file.name.split(".")[-1].lower()
        if file_extension == "pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            total_pages = len(pdf_reader.pages)
            print(f"\nProcessing PDF with {total_pages} pages...")
            
            # Process pages in chunks to avoid memory issues
            chunk_size = 10  # Process 10 pages at a time
            for i in range(0, total_pages, chunk_size):
                end_page = min(i + chunk_size, total_pages)
                print(f"\nProcessing pages {i+1} to {end_page}...")
                
                for page_num in range(i, end_page):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text.strip():  # Only add non-empty pages
                        text += page_text + "\n\n"
                
                # If we have enough text for Q&A generation, we can stop
                if len(text.split()) > 1000:  # Arbitrary threshold
                    print(f"\nExtracted sufficient text from first {end_page} pages")
                    break
            
            print(f"\nTotal text extracted: {len(text.split())} words")
            return text
        elif file_extension == "txt":
            return uploaded_file.getvalue().decode("utf-8")
        elif file_extension == "docx":
            doc = docx.Document(uploaded_file)
            return " ".join([paragraph.text for paragraph in doc.paragraphs])
        return ""
    except Exception as e:
        st.error(f"Error parsing file: {str(e)}")
        return ""

# Function to export as CSV
def export_csv(qa_pairs):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Question', 'Answer'])
    for qa in qa_pairs:
        writer.writerow([qa['question'], qa['answer']])
    return output.getvalue()

# Function to export as JSON
def export_json(qa_pairs):
    return json.dumps(qa_pairs, indent=2)

# Function to export as Anki format
def export_anki(qa_pairs):
    output = io.StringIO()
    writer = csv.writer(output, delimiter='\t')
    writer.writerow(['Question', 'Answer'])
    for qa in qa_pairs:
        writer.writerow([qa['question'], qa['answer']])
    return output.getvalue()

# Function to export as Quizlet format
def export_quizlet(qa_pairs):
    output = io.StringIO()
    writer = csv.writer(output, delimiter=',')
    writer.writerow(['Term', 'Definition'])
    for qa in qa_pairs:
        writer.writerow([qa['question'], qa['answer']])
    return output.getvalue()

# Function to render flippable cards
def render_flippable_cards(qa_pairs):
    if not qa_pairs:
        print("\nNo Q&A pairs to render")
        return
        
    print(f"\nRendering {len(qa_pairs)} cards")
    
    # Add edit mode toggle
    edit_mode = st.checkbox("✏️ Edit Mode", help="Enable editing of questions and answers")
    
    if edit_mode:
        # Create an editable interface
        st.subheader("📝 Review and Edit Q&A Pairs")
        for i, qa in enumerate(qa_pairs):
            with st.expander(f"Q&A Pair {i+1}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    new_question = st.text_area("Question", qa['question'], key=f"q_{i}")
                with col2:
                    new_answer = st.text_area("Answer", qa['answer'], key=f"a_{i}")
                
                # Update the Q&A pair if modified
                if new_question != qa['question'] or new_answer != qa['answer']:
                    qa_pairs[i] = {"question": new_question, "answer": new_answer}
                
                # Add delete button
                if st.button("🗑️ Delete", key=f"del_{i}"):
                    qa_pairs.pop(i)
                    st.rerun()
    else:
        # Create the cards container
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        
        # Add each card
        for i, qa in enumerate(qa_pairs):
            print(f"\nRendering card {i+1}:")
            print(f"Question: {qa['question']}")
            print(f"Answer: {qa['answer']}")
            card_html = f"""
            <div class="card">
                <div class="card-inner">
                    <div class="card-front">
                        <div class="card-content">
                            <h3>{qa['question']}</h3>
                        </div>
                    </div>
                    <div class="card-back">
                        <div class="card-content">
                            <h3>{qa['answer']}</h3>
                        </div>
                    </div>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
        
        # Close the container
        st.markdown('</div>', unsafe_allow_html=True)

# Title with emoji
st.title("✨ FlashForge-AI ✨")

# Initialize session state for Q&A pairs if not exists
if 'qa_pairs' not in st.session_state:
    st.session_state.qa_pairs = []

# Sidebar
with st.sidebar:
    st.header("🎮 Controls")
    
    # Subject selection
    subject = st.selectbox(
        "📚 Subject",
        ["General", "Biology", "History", "Computer Science", "Mathematics", "Literature"],
        help="Select the subject to tailor the Q&A format"
    )
    
    # Slider for number of questions
    num_questions = st.slider("📊 Number of Questions", min_value=5, max_value=20, value=10)
    
    # Segmented control for difficulty
    difficulty = st.radio("🎯 Difficulty", ["Easy", "Medium", "Hard"])
    
    st.markdown("---")
    
    # Export options (only shown if cards are generated)
    if st.session_state.qa_pairs:
        st.header("📤 Export Flash Cards")
        st.markdown("Choose a format to export your flash cards:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 CSV", use_container_width=True):
                csv_data = export_csv(st.session_state.qa_pairs)
                st.download_button(
                    "Download CSV",
                    csv_data,
                    "flashcards.csv",
                    "text/csv",
                    use_container_width=True
                )
            
            if st.button("📝 Anki", use_container_width=True):
                anki_data = export_anki(st.session_state.qa_pairs)
                st.download_button(
                    "Download Anki",
                    anki_data,
                    "flashcards.txt",
                    "text/plain",
                    use_container_width=True
                )
        
        with col2:
            if st.button("🔷 JSON", use_container_width=True):
                json_data = export_json(st.session_state.qa_pairs)
                st.download_button(
                    "Download JSON",
                    json_data,
                    "flashcards.json",
                    "application/json",
                    use_container_width=True
                )
            
            if st.button("📚 Quizlet", use_container_width=True):
                quizlet_data = export_quizlet(st.session_state.qa_pairs)
                st.download_button(
                    "Download Quizlet",
                    quizlet_data,
                    "flashcards.csv",
                    "text/csv",
                    use_container_width=True
                )

# Main content area
# File uploader
st.subheader("📁 Upload a file")
uploaded_file = st.file_uploader("Choose a file (PDF, TXT, DOCX)", type=["pdf", "txt", "docx"])

# Text input
st.subheader("✍️ Or enter text directly")
text_input = st.text_area("", height=200, placeholder="Enter your text here...")

# Generate button
if st.button("🎲 Generate Flash Cards", type="primary", use_container_width=True):
    # Parse uploaded file or use text input
    input_text = parse_file(uploaded_file) if uploaded_file else text_input
    
    # Generate Q&A pairs
    st.session_state.qa_pairs = generate_qa_pairs(input_text, num_questions, difficulty, subject)

# Display cards
if api_key is not None:
    # Display flippable cards
    render_flippable_cards(st.session_state.qa_pairs)
else:
    st.error("Failed to load the model. Please try refreshing the page.") 