
# AI-Powered Lesson Creation Tool

## Overview

The AI-Powered Lesson Creation Tool is a Streamlit-based application that helps instructors create structured, research-supported lessons from a lesson title and learning objective.

The application researches learning resources, generates a 45-minute lesson, evaluates factual accuracy and instructional quality, and allows instructors to review, edit, save, preview, and export the final lesson.

## Key Features

- **AI-powered research:** Finds relevant websites, books, and educational videos.
- **Lesson generation:** Creates structured lessons based on the learning objective.
- **45-minute lesson planning:** Organizes content into timed instructional segments.
- **Factual Quality Control (QC Layer 1):** Evaluates research support and factual accuracy.
- **Instructional Quality Control (QC Layer 2):** Reviews lesson structure, clarity, learning alignment, and teaching quality.
- **Instructor review and editing:** Allows instructors to modify and save generated content.
- **AI recommendations:** Provides recommendations to improve lesson quality.
- **Preview and export:** Previews the final lesson and exports it into supported document formats.
- **Lesson management:** Saves and retrieves previously created lessons.

## Technology Stack

- Python
- Streamlit
- Google Gemini API
- SQLite
- python-docx
- PDF export library
- Research and quality-control modules

## Application Workflow

1. The instructor enters a lesson title and learning objective.
2. The research engine searches for relevant learning resources.
3. The lesson generator creates a structured 45-minute lesson.
4. QC Layer 1 evaluates factual accuracy and research quality.
5. QC Layer 2 evaluates instructional quality.
6. The instructor reviews and edits the generated lesson.
7. Recommendations can be applied to improve the lesson.
8. The final lesson is previewed and exported.

## Project Structure

- `app.py` – Streamlit application and user interface.
- `config.py` – Application configuration.
- `core/` – Research, lesson generation, and quality-control modules.
- `database/` – SQLite database operations.
- `integrations/` – Gemini API integration.
- `requirements.txt` – Python dependencies.
- `.env` – Local environment variables (not included in public submissions).

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd AI_Lesson_Creation_Tool
```

### 2. Create and activate a virtual environment

Windows:

```powershell
py -3.10 -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root and add your Gemini API key and the model configuration expected by `config.py`.

Do not upload your actual API key to GitHub.

### 5. Run the application

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal.

## Test Sc

# AI_Lesson_Creation_Tool
AI-powered lesson creation, research, and instructional quality evaluation platform.
 