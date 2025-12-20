"""
Krishna AI Backend Server

Flask API with:
- Whisper ASR (openai/whisper-small) for speech-to-text
- Multi-task transformer for content analysis
- Audio or text input support

NO keyword logic. NO rules. Pure transformer inference.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import whisper
import tempfile
import os
import unicodedata
import re
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

from multitask_model import Analyzer

app = Flask(__name__)
CORS(app)

# Global instances (loaded once at startup)
asr_model = None
analyzer = None


def load_models():
    """Load Whisper and Analyzer models at startup."""
    global asr_model, analyzer
    
    print("=" * 50)
    print("🚀 Krishna AI Backend Starting...")
    print("=" * 50)
    
    # Load Whisper ASR
    print("\n📢 Loading Whisper ASR model (small)...")
    asr_model = whisper.load_model("small")
    print("✅ Whisper loaded successfully")
    
    # Load Multi-task Analyzer
    print("\n🧠 Loading Multi-task NLP model...")
    checkpoint_path = os.path.join(os.path.dirname(__file__), "checkpoints", "model.pt")
    if os.path.exists(checkpoint_path):
        analyzer = Analyzer(checkpoint_path=checkpoint_path)
    else:
        analyzer = Analyzer()
    print("✅ Analyzer loaded successfully")
    
    print("\n" + "=" * 50)
    print("✅ All models ready!")
    print("=" * 50 + "\n")


def transliterate_to_latin(text: str) -> str:
    """
    Convert any Devanagari (Hindi) script to Latin/Roman script.
    
    This ensures Hinglish is ALWAYS in romanized form:
    - "मैं" → "main"
    - "किसी" → "kisi"
    - English text passes through unchanged
    
    Args:
        text: Input text (may contain Devanagari, English, or mix)
    
    Returns:
        Text with all Devanagari converted to Latin script
    """
    try:
        # Transliterate Devanagari → Latin (ITRANS/ISO scheme)
        # This handles Hindi/Sanskrit scripts
        romanized = transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS)
        return romanized
    except:
        # If transliteration fails, return original (already in Latin)
        return text


def clean_text(text: str) -> str:
    """
    Basic text normalization (non-semantic).
    
    - Unicode normalization (NFC)
    - Lowercasing
    - Whitespace cleanup
    - Remove control characters
    
    NO keyword processing. NO semantic changes.
    """
    if not text:
        return ""
    
    # Unicode normalization
    text = unicodedata.normalize("NFC", text)
    
    # Remove control characters (keep letters, numbers, punctuation, spaces)
    text = "".join(char for char in text if not unicodedata.category(char).startswith("C") or char in "\n\t")
    
    # Normalize whitespace (collapse multiple spaces)
    text = " ".join(text.split())
    
    return text.strip()


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "message": "Krishna AI Backend is running",
        "models": {
            "whisper": asr_model is not None,
            "analyzer": analyzer is not None
        }
    })


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Main analysis endpoint.
    
    Accepts:
    - Audio file (multipart/form-data with 'audio' field)
    - Text JSON (application/json with 'text' field)
    
    Returns:
    {
        "success": true,
        "transcription": "original or transcribed text",
        "data": {
            "sentiment": {"label": "positive", "confidence": 0.85},
            "toxicity": {"label": "safe", "confidence": 0.95},
            "categories": [{"label": "career", "confidence": 0.72}]
        }
    }
    """
    try:
        text = None
        
        # Check for audio input
        if "audio" in request.files:
            audio_file = request.files["audio"]
            
            # Save to temp file for Whisper
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                audio_file.save(tmp.name)
                tmp_path = tmp.name
            
            try:
                # Transcribe with Whisper - ENGLISH for Hinglish support
                # English mode handles code-switching naturally:
                # - English words → English
                # - Hindi words → Romanized (e.g., "mujhe", "nahi")
                result = asr_model.transcribe(
                    tmp_path, 
                    language="en",  # English handles Hinglish code-switching
                    task="transcribe"
                )
                text = result["text"]
                
                # CRITICAL: Convert any Devanagari to Latin script
                # Whisper sometimes outputs Hindi in Devanagari even in English mode
                text = transliterate_to_latin(text)
                
            finally:
                # Clean up temp file
                os.unlink(tmp_path)
        
        # Check for text input
        elif request.is_json and "text" in request.json:
            text = request.json["text"]
        
        else:
            return jsonify({
                "success": False,
                "error": "No input provided. Send 'audio' file or 'text' in JSON body."
            }), 400
        
        # Validate text
        if not text or not text.strip():
            return jsonify({
                "success": False,
                "error": "Empty input provided"
            }), 400
        
        # Basic normalization (non-semantic)
        text = clean_text(text)
        
        # Multi-task inference
        result = analyzer.analyze(text)
        
        return jsonify({
            "success": True,
            "transcription": text,
            "data": result
        })
    
    except Exception as e:
        print(f"❌ Error in /analyze: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/test", methods=["GET"])
def test():
    """Test endpoint with sample Hinglish queries."""
    samples = [
        "Kal interview hai, bahut tension ho rahi hai",
        "First salary mili aaj, bahut khush hun",
        "Girlfriend se breakup ho gaya, dil toot gaya",
        "Maa ki tabiyat theek nahi hai, hospital jana padega",
        "Office mein bore ho raha hun, kuch exciting chahiye"
    ]
    
    results = []
    for text in samples:
        result = analyzer.analyze(text)
        results.append({
            "input": text,
            "output": result
        })
    
    return jsonify({
        "success": True,
        "test_results": results
    })


# Load models when module is imported
load_models()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 50010))
    print(f"\n🌐 Starting server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
