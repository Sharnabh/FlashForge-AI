import streamlit as st
import os
import tempfile
import warnings
import google.generativeai as genai
import PyPDF2
import docx

# Filter out the legacy warning
warnings.filterwarnings("ignore", message=".*legacy.*")

# Set page config
st.set_page_config(page_title="Flash Card Game", layout="wide")

# Title
st.title("Flash Card Game")

# File uploader
uploaded_file = st.file_uploader("Upload a file (PDF, TXT, DOCX)", type=["pdf", "txt", "docx"])

# Text input
text_input = st.text_area("Or enter text directly:")

# Slider for number of questions
num_questions = st.slider("Number of Questions", min_value=5, max_value=20, value=10)

# Segmented control for difficulty
difficulty = st.radio("Difficulty", ["Easy", "Medium", "Hard"])

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

# Function to render flippable cards
def render_flippable_cards(qa_pairs):
    if not qa_pairs:
        return
        
    # Add CSS for the cards
    st.markdown("""
    <style>
    .card-container {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        justify-content: center;
        padding: 20px;
    }
    .card {
        perspective: 1000px;
        width: 300px;
        height: 200px;
        margin: 10px;
    }
    .card-inner {
        position: relative;
        width: 100%;
        height: 100%;
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
        border: 1px solid #ccc;
        border-radius: 10px;
        padding: 20px;
        box-sizing: border-box;
        display: flex;
        align-items: center;
        justify-content: center;
        background: white;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .card-back {
        transform: rotateY(180deg);
    }
    .card h3 {
        margin: 0;
        font-size: 1.2em;
        line-height: 1.4;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create the cards container
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    
    # Add each card
    for qa in qa_pairs:
        card_html = f"""
        <div class="card">
            <div class="card-inner">
                <div class="card-front">
                    <h3>{qa['question']}</h3>
                </div>
                <div class="card-back">
                    <h3>{qa['answer']}</h3>
                </div>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
    
    # Close the container
    st.markdown('</div>', unsafe_allow_html=True)

# Main app logic
if model is not None:
    # Parse uploaded file or use text input
    input_text = parse_file(uploaded_file) if uploaded_file else text_input

    # Generate Q&A pairs
    qa_pairs = generate_qa_pairs(input_text, num_questions, difficulty)

    # Display flippable cards
    render_flippable_cards(qa_pairs)
else:
    st.error("Failed to load the model. Please try refreshing the page.") 