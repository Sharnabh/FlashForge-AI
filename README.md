# Flash Card Game

A Streamlit app that generates flash cards using Flan T5 Large. Upload a PDF, TXT, or DOCX file, or enter text directly, and generate flippable Q&A cards based on the input.

## Features

- Upload PDF, TXT, or DOCX files, or enter text directly.
- Select the number of questions (5-20) and difficulty (Easy, Medium, Hard).
- Generate Q&A pairs using Flan T5 Large.
- Display flippable cards with a smooth flip animation.

## Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the app:
   ```
   streamlit run app.py
   ```

## Usage

- Upload a file or enter text in the text area.
- Adjust the slider to select the number of questions.
- Choose the difficulty level.
- View the generated flippable cards.

## Dependencies

- streamlit
- transformers
- torch
- PyPDF2
- python-docx

## License

MIT 