import streamlit as st
import os
import tempfile
import warnings
from transformers.models.t5.tokenization_t5 import T5Tokenizer
from transformers.models.t5.modeling_t5 import T5ForConditionalGeneration
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

# Load Flan T5 Large model and tokenizer
@st.cache_resource
def load_model():
    try:
        model_name = "google/flan-t5-large"
        with st.spinner("Loading model and tokenizer..."):
            tokenizer = T5Tokenizer.from_pretrained(model_name, legacy=False)
            model = T5ForConditionalGeneration.from_pretrained(model_name)
        return model, tokenizer
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None, None

model, tokenizer = load_model()

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

# Function to generate Q&A pairs using Flan T5 Large
@st.cache_data(ttl=3600)  # Cache results for 1 hour
def generate_qa_pairs(text, num_questions, difficulty):
    if not text.strip():
        st.warning("Please provide some text or upload a file.")
        return []
    
    try:
        with st.spinner("Generating questions and answers..."):
            # First generate questions
            question_prompt = f"Generate {num_questions} {difficulty.lower()} questions based on the following text: {text}"
            question_inputs = tokenizer(question_prompt, return_tensors="pt", max_length=512, truncation=True)
            question_outputs = model.generate(
                **question_inputs,
                max_length=256,  # Reduced max length
                num_beams=num_questions,  # Match num_beams with num_questions
                num_return_sequences=num_questions,
                early_stopping=True,
                no_repeat_ngram_size=2,
                do_sample=True,  # Enable sampling for faster generation
                top_k=50,        # Limit vocabulary to top 50 tokens
                top_p=0.95       # Nucleus sampling
            )
            
            qa_pairs = []
            progress_bar = st.progress(0)
            
            for i, question_output in enumerate(question_outputs):
                question = tokenizer.decode(question_output, skip_special_tokens=True)
                if not question.endswith("?"):
                    question += "?"
                
                # Generate answer for each question
                answer_prompt = f"Answer the following question based on the text: {text}\nQuestion: {question}"
                answer_inputs = tokenizer(answer_prompt, return_tensors="pt", max_length=512, truncation=True)
                answer_output = model.generate(
                    **answer_inputs,
                    max_length=256,  # Reduced max length
                    num_beams=5,     # Keep this at 5 for answer generation
                    early_stopping=True,
                    do_sample=True,  # Enable sampling for faster generation
                    top_k=50,        # Limit vocabulary to top 50 tokens
                    top_p=0.95       # Nucleus sampling
                )
                answer = tokenizer.decode(answer_output[0], skip_special_tokens=True)
                
                qa_pairs.append({"question": question, "answer": answer})
                
                # Update progress
                progress = (i + 1) / len(question_outputs)
                progress_bar.progress(progress)
            
            return qa_pairs
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
if model is not None and tokenizer is not None:
    # Parse uploaded file or use text input
    input_text = parse_file(uploaded_file) if uploaded_file else text_input

    # Generate Q&A pairs
    qa_pairs = generate_qa_pairs(input_text, num_questions, difficulty)

    # Display flippable cards
    render_flippable_cards(qa_pairs)
else:
    st.error("Failed to load the model. Please try refreshing the page.") 