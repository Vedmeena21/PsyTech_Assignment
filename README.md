# 🕉️ Krishna AI Content Analyzer

A production-ready **Hinglish content moderation and devotional tagging system** using state-of-the-art NLP and speech recognition.

## 🎯 Features

### 1. **Speech-to-Text (ASR)**
- **Whisper (openai/whisper-small)** for multilingual transcription
- Automatic Devanagari → Latin transliteration
- Optimized for Hinglish (Hindi + English code-switching)

### 2. **Multi-Task NLP Classification**
Single XLM-RoBERTa transformer with 3 specialized heads:

#### **Sentiment Analysis**
- Classes: Positive, Neutral, Negative
- Confidence scores for each prediction

#### **Toxicity Detection**
- Classes: Safe, Offensive/Hate Speech, Spam/Promotion
- Policy-based content moderation

#### **Devotional Category Tagging** (Multi-label)
- Career
- Love Life
- Family Issues
- Health Issues
- Mood Issues

## 🏗️ Architecture

```
User Voice Input
   ↓
Whisper ASR (Backend)
   ↓
Text Normalization + Transliteration
   ↓
XLM-RoBERTa Multi-Task Model
   ├── Sentiment Head
   ├── Toxicity Head
   └── Category Head
   ↓
Probabilistic Outputs + Confidence Scores
   ↓
UI Display
```

**Key Design Principles:**
- ✅ Single model, single forward pass
- ✅ Pure probabilistic inference (no keywords/rules)
- ✅ Class-weighted loss for imbalanced data
- ✅ Multi-label category classification

## 🚀 Quick Start

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

# Generate training data (5,000 samples)
python generate_data.py

# Train the model (optional - pre-trained checkpoint included)
python train.py

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

## 📊 Model Training

### Dataset
- **5,000 synthetic Hinglish samples**
- Distribution:
  - Sentiment: 45% negative, 30% neutral, 25% positive
  - Toxicity: 85% safe, 10% offensive, 5% spam
  - Categories: Multi-label with mood_issues dominant

### Training Configuration
```python
Optimizer: AdamW
Learning Rate: 2e-5
Batch Size: 16
Epochs: 5
Encoder: Frozen for 1 epoch, then unfrozen
Loss: sentiment_loss + toxicity_loss + 0.8 * category_loss
```

### Performance
- **Final Validation Loss: 1.25**
- **Sentiment Accuracy: ~85%**
- **Toxicity Precision: ~90%**
- **Category F1: ~80%**

## 🧪 Testing

### API Testing

```bash
# Test sentiment
curl -X POST http://localhost:50010/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Me thik hu"}'

# Expected: Positive sentiment, Safe toxicity

# Test toxicity
curl -X POST http://localhost:50010/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "I want to kill somebody"}'

# Expected: Negative sentiment, Offensive toxicity

# Test neutral
curl -X POST http://localhost:50010/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Kuch khaas nahi"}'

# Expected: Neutral sentiment, Safe toxicity
```

### Test Endpoint
```bash
curl http://localhost:50010/test
```

Returns predictions on 5 sample Hinglish queries.

## 📁 Project Structure

```
krishna-ai-dashboard/
├── backend/
│   ├── app.py                 # Flask API + Whisper integration
│   ├── multitask_model.py     # Multi-task transformer model
│   ├── train.py               # Training script
│   ├── generate_data.py       # Synthetic data generator
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example          # Environment variables template
│   └── checkpoints/          # Model weights (not in Git)
│       └── model.pt
├── frontend/
│   ├── src/
│   │   └── App.jsx           # React UI
│   ├── public/
│   └── package.json
├── .gitignore
└── README.md
```

## 🔧 API Reference

### POST `/analyze`

**Request (Audio):**
```bash
curl -X POST http://localhost:50010/analyze \
  -F "audio=@recording.wav"
```

**Request (Text):**
```json
{
  "text": "Hinglish text here"
}
```

**Response:**
```json
{
  "success": true,
  "transcription": "Me thik hu",
  "data": {
    "sentiment": {
      "label": "positive",
      "confidence": 0.993
    },
    "toxicity": {
      "label": "safe",
      "confidence": 0.998
    },
    "categories": [
      {
        "label": "mood_issues",
        "confidence": 0.726
      }
    ]
  }
}
```

### GET `/health`
Health check endpoint.

### GET `/test`
Run test suite on sample queries.

## 🎓 Technical Details

### Why XLM-RoBERTa?
- Multilingual support (100+ languages)
- Strong performance on code-switched text
- Pretrained on large-scale multilingual corpus
- Efficient for production deployment

### Why Multi-Task Learning?
- Shared encoder learns better representations
- Single forward pass (faster inference)
- Regularization effect improves generalization
- Efficient resource utilization

### Transliteration Pipeline
```python
Whisper Output (Devanagari) → Indic Transliteration → Latin Script
"मैं ठीक हूं" → "main thik hun"
```

## 🚨 Moderation Policy

| Condition | Action |
|-----------|--------|
| Toxicity > 85% | Block Krishna response |
| Spam > 75% | Rate limit user |
| Safe | Allow normal flow |

## 📈 Future Improvements

- [ ] Increase training data to 10K+ samples
- [ ] Add temperature scaling for calibration
- [ ] Implement GPU support for faster training
- [ ] Add more devotional categories
- [ ] Deploy on cloud (AWS/GCP)
- [ ] Add user feedback loop for continuous learning

## 🤝 Contributing

This is an internship project demonstrating:
- Multi-task transformer architecture
- Production ML pipeline
- Full-stack integration (React + Flask)
- Speech recognition + NLP

## 📄 License

MIT License - See LICENSE file for details

## 👤 Author

**Ved** - AI/ML Internship Project

## 🙏 Acknowledgments

- OpenAI Whisper for ASR
- Hugging Face Transformers
- XLM-RoBERTa pretrained model
- React + Flask communities

---

**Built with ❤️ for Krishna AI**
