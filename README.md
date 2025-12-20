# Krishna AI Content Analyzer

A production-ready **Hinglish content moderation and devotional tagging system** integrated with a real-time React frontend and a Multi-Task Transformer backend.

## Features

### 1. Native Web Speech API (Frontend)
- **Browser-Native Recognition:** Utilizes the Web Speech API (`window.webkitSpeechRecognition`) for low-latency speech input.
- **Hinglish Optimization:** Configured with `hi-IN` (Hindi) locale to accurately capture mixed-script input (e.g., "मुझे जॉब नहीं मिल रही").
- **Real-time Processing:** Direct speech-to-text without heavy backend audio file transfers.

### 2. Multi-Task NLP Classification (Backend)
Single XLM-RoBERTa transformer with 3 specialized heads:

#### Sentiment Analysis
- Classes: Positive, Neutral, Negative
- Confidence scores for each prediction

#### Toxicity Detection
- Classes: Safe, Offensive/Hate Speech, Spam/Promotion
- Policy-based content moderation

#### Devotional Category Tagging (Multi-label)
- Career, Love Life, Family Issues, Health Issues, Mood Issues

## Architecture

```
User Voice Input (Browser)
   ↓
Web Speech API (hi-IN)
   ↓
Transcribed Text (Devanagari/Hinglish)
   ↓
Text Normalization (Backend)
   ↓
XLM-RoBERTa Multi-Task Model
   ├── Sentiment Head
   ├── Toxicity Head
   └── Category Head
   ↓
Probabilistic Outputs + Confidence Scores
   ↓
UI Display (React)
```

**Key Design Principles:**
- **Client-Side ASR:** Offloads speech recognition to the browser for speed and privacy.
- **Single Model Inference:** One backend call handles sentiment, toxicity, and categorization.
- **Professional UI:** Clean, single-screen interface optimized for Chrome/Edge.

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- 8GB+ RAM

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start backend server
python app.py
```

Backend runs on: **http://localhost:50010**

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend runs on: **http://localhost:3000**

## Model Details

### Dataset
- **5,000 synthetic Hinglish samples**
- Distribution:
  - Sentiment: 45% negative, 30% neutral, 25% positive
  - Toxicity: 85% safe, 10% offensive, 5% spam
  - Categories: Multi-label with mood_issues dominance

## Project Structure

```
krishna-ai-dashboard/
├── backend/
│   ├── app.py                 # Flask API + NLP Inference
│   ├── multitask_model.py     # Multi-task transformer model
│   ├── train.py               # Training script
│   ├── generate_data.py       # Synthetic data generator
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── src/
│   │   └── App.jsx           # React UI with Native Web Speech
│   ├── public/
│   └── package.json
├── .gitignore
└── README.md
```
