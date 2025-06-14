import streamlit as st
import os
from typing import List
from flashcard_generator import FlashcardGenerator, Flashcard
from file_handler import FileHandler
from export_manager import ExportManager

def main():
    st.set_page_config(
        page_title="FlashForge AI - Flashcard Generator",
        page_icon="🎯",
        layout="wide"
    )
    
    st.title("🎯 FlashForge AI - LLM-Powered Flashcard Generator")
    st.markdown("Transform your educational content into effective flashcards using AI")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "OpenAI API Key", 
            type="password",
            help="Enter your OpenAI API key to generate flashcards"
        )
        
        # Subject selection
        subject_type = st.selectbox(
            "Subject Type",
            ["General", "Biology", "History", "Computer Science", "Mathematics", "Physics", "Chemistry", "Literature"]
        )
        
        # Number of flashcards
        num_cards = st.slider("Number of flashcards", min_value=5, max_value=20, value=12)
        
        # Advanced options
        with st.expander("Advanced Options"):
            include_topics = st.checkbox("Include topic categorization", value=True)
            include_difficulty = st.checkbox("Include difficulty levels", value=True)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📝 Input Content")
        
        # Input method selection
        input_method = st.radio(
            "Choose input method:",
            ["📁 File Upload", "✏️ Direct Text Input"]
        )
        
        content = ""
        filename = ""
        
        if input_method == "📁 File Upload":
            uploaded_file = st.file_uploader(
                "Upload your educational content",
                type=['txt', 'pdf', 'docx'],
                help="Supported formats: PDF, DOCX, TXT"
            )
            
            if uploaded_file:
                try:
                    with st.spinner("Processing file..."):
                        filename, content = FileHandler.process_uploaded_file(uploaded_file)
                    st.success(f"✅ File '{filename}' processed successfully!")
                    
                    # Show content preview
                    with st.expander("Content Preview"):
                        st.text_area("", content[:500] + "..." if len(content) > 500 else content, height=150)
                        
                except Exception as e:
                    st.error(f"❌ Error processing file: {str(e)}")
        
        else:  # Direct text input
            content = st.text_area(
                "Paste your educational content here:",
                height=300,
                placeholder="Enter textbook excerpts, lecture notes, or any educational material..."
            )
    
    with col2:
        st.header("🎯 Generated Flashcards")
        
        if st.button("🚀 Generate Flashcards", type="primary", disabled=not (api_key and content)):
            if not api_key:
                st.error("❌ Please enter your OpenAI API key")
            elif not content.strip():
                st.error("❌ Please provide some content to generate flashcards")
            else:
                try:
                    with st.spinner("Generating flashcards... This may take a moment."):
                        generator = FlashcardGenerator(api_key)
                        flashcards = generator.generate_flashcards(
                            content=content,
                            subject_type=subject_type,
                            num_cards=num_cards,
                            include_topics=include_topics
                        )
                        
                        # Validate flashcards
                        valid_flashcards = generator.validate_flashcards(flashcards)
                        
                        if valid_flashcards:
                            st.success(f"✅ Generated {len(valid_flashcards)} flashcards!")
                            st.session_state.flashcards = valid_flashcards
                        else:
                            st.error("❌ No valid flashcards could be generated. Please try with different content.")
                            
                except Exception as e:
                    st.error(f"❌ Error generating flashcards: {str(e)}")
    
    # Display generated flashcards
    if 'flashcards' in st.session_state and st.session_state.flashcards:
        st.header("📚 Review & Edit Flashcards")
        
        flashcards = st.session_state.flashcards
        
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Cards", len(flashcards))
        with col2:
            easy_count = sum(1 for card in flashcards if card.difficulty == "Easy")
            st.metric("Easy", easy_count)
        with col3:
            medium_count = sum(1 for card in flashcards if card.difficulty == "Medium")
            st.metric("Medium", medium_count)
        with col4:
            hard_count = sum(1 for card in flashcards if card.difficulty == "Hard")
            st.metric("Hard", hard_count)
        
        # Display and edit flashcards
        edited_flashcards = []
        
        for i, card in enumerate(flashcards):
            with st.expander(f"📇 Flashcard {i+1} - {card.difficulty} - {card.topic}", expanded=False):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    question = st.text_area(
                        "Question:",
                        value=card.question,
                        key=f"q_{i}",
                        height=100
                    )
                
                with col2:
                    answer = st.text_area(
                        "Answer:",
                        value=card.answer,
                        key=f"a_{i}",
                        height=100
                    )
                
                col3, col4 = st.columns([1, 1])
                with col3:
                    difficulty = st.selectbox(
                        "Difficulty:",
                        ["Easy", "Medium", "Hard"],
                        index=["Easy", "Medium", "Hard"].index(card.difficulty),
                        key=f"d_{i}"
                    )
                
                with col4:
                    topic = st.text_input(
                        "Topic:",
                        value=card.topic,
                        key=f"t_{i}"
                    )
                
                edited_flashcards.append(Flashcard(question, answer, difficulty, topic))
        
        # Update session state with edited flashcards
        st.session_state.flashcards = edited_flashcards
        
        # Export section
        st.header("📤 Export Flashcards")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📄 Export as JSON"):
                json_content = ExportManager.to_json(edited_flashcards)
                st.download_button(
                    label="💾 Download JSON",
                    data=json_content,
                    file_name="flashcards.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("📊 Export as CSV"):
                csv_content = ExportManager.to_csv(edited_flashcards)
                st.download_button(
                    label="💾 Download CSV",
                    data=csv_content,
                    file_name="flashcards.csv",
                    mime="text/csv"
                )
        
        with col3:
            if st.button("🎴 Export for Anki"):
                anki_content = ExportManager.to_anki(edited_flashcards)
                st.download_button(
                    label="💾 Download Anki",
                    data=anki_content,
                    file_name="flashcards_anki.txt",
                    mime="text/plain"
                )
        
        with col4:
            if st.button("📚 Export for Quizlet"):
                quizlet_content = ExportManager.to_quizlet(edited_flashcards)
                st.download_button(
                    label="💾 Download Quizlet",
                    data=quizlet_content,
                    file_name="flashcards_quizlet.txt",
                    mime="text/plain"
                )

if __name__ == "__main__":
    main()
