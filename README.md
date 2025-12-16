# Krishna AI Devotional Dashboard

A voice-enabled AI dashboard for analyzing devotional content in Hinglish (Hindi + English mix), providing sentiment analysis and content moderation.

## 🎯 Project Idea

An intelligent dashboard that helps analyze user messages to Krishna AI, understanding both emotional sentiment and content safety. Perfect for devotional apps, spiritual guidance platforms, or any Hinglish content moderation needs.

**Key Features:**
- 🎤 Voice input support (Hindi/Hinglish)
- 📊 Sentiment analysis (Positive, Neutral, Negative)
- 🛡️ Content moderation (Safe, Offensive, Spam)
- 🌐 Hinglish support (mixed Hindi-English)
- 🎨 Modern, responsive UI

---

## 🚀 Quick Setup

### Prerequisites
- Python 3.9+
- Node.js 14+
- HuggingFace API token (free)

### 1. Clone & Install

```bash
cd krishna-ai-dashboard

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### 2. Get HuggingFace API Key

1. Go to https://huggingface.co/settings/tokens
2. Create a new token (read access)
3. Copy the token

### 3. Configure Environment

Create `backend/.env`:
```bash
GOOGLE_API_KEY=your_google_api_key_here
PORT=5001
```

Create `frontend/.env`:
```bash
REACT_APP_API_URL=http://localhost:5001
```

### 4. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python app.py
```
Backend runs on: http://localhost:5001

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```
Frontend opens at: http://localhost:3000

---

## 📊 How It Works

### Architecture

```
User Input (Voice/Text in Hinglish)
         ↓
┌────────────────────────────────┐
│   Sentiment Analysis           │
│   (ML Model - Local)           │
│   → Positive/Neutral/Negative  │
└────────────────────────────────┘
         ↓
┌────────────────────────────────┐
│   Toxicity Detection           │
│   (Mistral-7B via HF API)      │
│   → Safe/Offensive/Spam        │
└────────────────────────────────┘
         ↓
    Dashboard Display
```

### Models Used

1. **Sentiment Analysis** (Local)
   - Model: `cardiffnlp/twitter-xlm-roberta-base-sentiment`
   - Multilingual, works with Hinglish
   - Fast, accurate

2. **Toxicity Detection** (API)
   - Model: `mistralai/Mistral-7B-Instruct-v0.2`
   - Policy-based classification
   - No keywords, context-aware

---

## 🎯 Classification Logic

### Sentiment (Working ✅)
- **Positive**: Happy, joyful, grateful expressions
- **Neutral**: Factual statements, questions
- **Negative**: Sad, angry, distressed emotions

### Toxicity (Implementation Ready)
- **Safe**: Emotional distress WITHOUT intent to harm
  - Example: "Main depressed hun" (I'm depressed)
- **Offensive**: ANY desire/intent to harm self or others
  - Example: "I want to kill someone"
- **Spam**: Promotional/advertising content
  - Example: "Buy now! Limited offer!"

---

## 🔧 Troubleshooting

### HuggingFace API Issues
If toxicity detection returns "Offensive" for everything:
- Wait 10-15 minutes for HF Inference API to load model
- Check your HF token is valid
- Conservative failure policy: errors → "Offensive" (by design)

### Port Conflicts
- Backend default: 5001 (change in `backend/.env`)
- Frontend default: 3000 (change in `frontend/.env`)

### Voice Input Not Working
- Use Chrome/Edge (best Web Speech API support)
- Allow microphone permissions
- Select Hindi (India) language

---

## 📁 Project Structure

```
krishna-ai-dashboard/
├── backend/
│   ├── app.py              # Flask API server
│   ├── models.py           # AI analysis logic
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables
├── frontend/
│   ├── src/
│   │   └── App.jsx        # React dashboard UI
│   ├── package.json       # Node dependencies
│   └── .env              # Frontend config
└── README.md             # This file
```

---

## 🎨 Features

- ✅ **Voice Input**: Speak in Hindi/Hinglish
- ✅ **Text Input**: Type your message
- ✅ **Real-time Analysis**: Instant sentiment + toxicity results
- ✅ **Responsive Design**: Works on mobile & desktop
- ✅ **Free Tier**: Uses free APIs (HuggingFace, Google)

---

## 🔐 Privacy & Security

- API keys stored in `.env` (gitignored)
- No data persistence
- All processing via secure APIs
- Voice data not stored

---

## 📝 License

MIT License - Free to use and modify

---

## 🤝 Support

For issues or questions:
1. Check troubleshooting section above
2. Verify API keys are correct
3. Ensure all dependencies installed

---

**Built with ❤️ for the Krishna AI community**
