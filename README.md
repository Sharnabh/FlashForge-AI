# FlashForge-AI

FlashForge-AI is a Streamlit application that leverages the Together AI API to generate educational flashcards from user-provided text or documents. It's designed to help students and learners quickly create study materials from their notes, textbooks, or any other text-based content.

## Features

-   **Multiple Input Methods**: Upload PDF, TXT, or DOCX files, or simply paste text directly into the application.
-   **Customizable Generation**:
    -   Select the subject to tailor the Q&A generation (e.g., Physics, Chemistry, History).
    -   Choose the number of flashcards to generate (5-20).
    -   Set the difficulty level (Easy, Medium, Hard).
-   **Interactive Flashcards**: View the generated Q&A pairs as interactive, flippable cards.
-   **Edit and Review**: An "Edit Mode" allows you to review, modify, or delete the generated Q&A pairs.
-   **Multi-language Support**: Translate the flashcards into several languages, including Spanish, French, German, and more.
-   **Multiple Export Formats**: Export your flashcard sets for use in other applications. Supported formats include:
    -   CSV
    -   JSON
    -   Anki (.txt)
    -   Quizlet (.txt)

## Setup

To run FlashForge-AI locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd FlashForge-AI
    ```

2.  **Install dependencies:**
    It's recommended to use a virtual environment.
    ```bash
    python -m venv venv
    venv\Scripts\activate  # On Windows
    # source venv/bin/activate  # On macOS/Linux
    ```
    Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up API Key:**
    This application uses the Together AI API. You'll need to get an API key from [Together.ai](https://www.together.ai/).

    -   Create a file named `.streamlit/secrets.toml` in the project root directory.
    -   Add your API key to this file as follows:
        ```toml
        TOGETHER_API_KEY = "your-api-key-here"
        ```

4.  **Run the app:**
    ```bash
    streamlit run app.py
    ```
    The application will open in your default web browser.

## Usage

1.  **Configure Generation**: In the sidebar, select the subject, number of questions, and difficulty level.
2.  **Provide Content**:
    -   Use the file uploader to select a PDF, TXT, or DOCX file.
    -   Or, paste your text into the text area.
3.  **Generate**: Click the "Generate Flash Cards" button.
4.  **Review**:
    -   The generated flashcards will appear in the main area. Hover over a card to flip it and see the answer.
    -   Use the "Language" dropdown to translate the cards.
    -   Enable "Edit Mode" to modify the questions and answers.
5.  **Export**:
    -   If you're satisfied with the flashcards, use the export buttons in the sidebar to download them in your preferred format.

## Dependencies

The main dependencies are listed in `requirements.txt` and include:
-   `streamlit`
-   `requests`
-   `PyPDF2`
-   `python-docx`
-   `pandas`
-   `numpy`

## License

This project is licensed under the MIT License.