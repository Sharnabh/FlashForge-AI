import streamlit as st
import os
import tempfile
import warnings
import google.generativeai as genai
import PyPDF2
import docx
import json
import csv
import io
import pandas as pd

# Filter out the legacy warning
warnings.filterwarnings("ignore", message=".*legacy.*")

# Set page config
st.set_page_config(page_title="FlashForge-AI", layout="wide")

# Custom CSS for enhanced styling
st.markdown("""
    <style>
        /* Main theme colors */
        :root {
            --primary-color: #4B0082;
            --secondary-color: #9370DB;
            --accent-color: #8A2BE2;
            --background-color: #F8F9FA;
            --text-color: #2C3E50;
        }

        /* Global styles */
        .stApp {
            background-color: var(--background-color);
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
            color: var(--secondary-color);
            font-weight: 600 !important;
        }

        /* Sidebar styling */
        .css-1d391kg {
            background-color: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        /* Button styling */
        .stButton > button {
            background-color: var(--accent-color);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: all 0.3s ease;
        }

        .stButton > button:hover {
            background-color: var(--primary-color);
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
            background: white;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }

        .card-front {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
        }

        .card-back {
            background: linear-gradient(135deg, var(--secondary-color), var(--accent-color));
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
            background-color: white;
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        /* Text area styling */
        .stTextArea > div > div {
            background-color: white;
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        /* Slider container styling - matching radio button area */
        .stSlider > div {
            background-color: white;
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 0.5rem 0;
        }

        /* Slider track */
        .stSlider > div > div > div {
            height: 4px;
            border-radius: 2px;
            background: linear-gradient(to right, var(--secondary-color), var(--accent-color));
        }

        /* Slider thumb */
        .stSlider > div > div > div > div {
            background-color: var(--primary-color);
            border: 2px solid white;
            box-shadow: 0 0 5px rgba(0,0,0,0.2);
        }

        .stSlider > div > div > div > div:hover {
            transform: scale(1.1);
            transition: transform 0.2s ease;
        }

        .stSlider > div > div > div > div:active {
            transform: scale(0.95);
        }

        /* Slider label */
        .stSlider > div > div > div > div > div {
            color: var(--text-color);
            font-weight: 500;
        }

        /* Slider value display */
        .stSlider > div > div > div > div > div > div {
            color: var(--primary-color);
            font-weight: 600;
        }

        /* Radio button styling */
        .stRadio > div {
            background-color: white;
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        /* Export buttons styling */
        .export-button {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            margin: 0.5rem 0;
            width: 100%;
            transition: all 0.3s ease;
        }

        .export-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }

        @media (min-width: 1200px) {
            .card-container {
                grid-template-columns: repeat(3, 1fr);
            }
        }
    </style>
""", unsafe_allow_html=True)

# Initialize Gemini model
@st.cache_resource
def load_model():
    try:
        # Configure the Gemini API
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        return model
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None

model = load_model()

# Function to parse uploaded file
def parse_file(uploaded_file):
    if uploaded_file is None:
        return ""
    try:
        file_extension = uploaded_file.name.split(".")[-1].lower()
        if file_extension == "pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
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

# Function to generate Q&A pairs using Gemini
@st.cache_data(ttl=3600)  # Cache results for 1 hour
def generate_qa_pairs(text, num_questions, difficulty):
    if not text.strip():
        st.warning("Please provide some text or upload a file.")
        return []
    
    try:
        with st.spinner("Generating questions and answers..."):
            prompt = f"""Create {num_questions} {difficulty.lower()} difficulty flash cards based on this text. 
            For each card, provide a question and its answer.
            Format each card as: Q: [question] A: [answer]
            
            Text: {text}"""
            
            response = model.generate_content(prompt)
            content = response.text.strip()
            
            # Parse Q&A pairs
            qa_pairs = []
            lines = content.split('\n')
            current_q = None
            current_a = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('Q:'):
                    if current_q and current_a:
                        qa_pairs.append({"question": current_q, "answer": current_a})
                    current_q = line[2:].strip()
                elif line.startswith('A:'):
                    current_a = line[2:].strip()
            
            if current_q and current_a:
                qa_pairs.append({"question": current_q, "answer": current_a})
            
            return qa_pairs[:num_questions]
    except Exception as e:
        st.error(f"Error generating Q&A pairs: {str(e)}")
        return []

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
        return
        
    # Create the cards container
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    
    # Add each card
    for qa in qa_pairs:
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
    st.session_state.qa_pairs = generate_qa_pairs(input_text, num_questions, difficulty)

# Display cards
if model is not None:
    # Display flippable cards
    render_flippable_cards(st.session_state.qa_pairs)
else:
    st.error("Failed to load the model. Please try refreshing the page.") 