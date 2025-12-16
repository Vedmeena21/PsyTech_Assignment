from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

from models import DevotionalAnalyzer

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Initialize analyzer
try:
    analyzer = DevotionalAnalyzer()
    print("✅ DevotionalAnalyzer initialized successfully")
except Exception as e:
    print(f"❌ Error initializing analyzer: {e}")
    analyzer = None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "analyzer_ready": analyzer is not None
    })

@app.route('/analyze', methods=['POST'])
def analyze_text():
    """
    Analyze devotional content
    
    Request body:
        {
            "text": "User input in Hinglish"
        }
    
    Response:
        {
            "success": true,
            "data": {
                "sentiment": {...},
                "toxicity": {...},
                "categories": [...]
            }
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'text' field in request"
            }), 400
        
        text = data['text'].strip()
        
        if not text:
            return jsonify({
                "success": False,
                "error": "Empty text provided"
            }), 400
        
        if not analyzer:
            return jsonify({
                "success": False,
                "error": "Analyzer not initialized. Check API keys."
            }), 500
        
        # Analyze text
        result = analyzer.analyze(text)
        
        return jsonify({
            "success": True,
            "data": result
        })
    
    except Exception as e:
        print(f"Error in /analyze endpoint: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/test', methods=['GET'])
def test_samples():
    """Test endpoint with sample Hinglish queries"""
    samples = [
        "Mujhe job nahi mil rahi hai, Krishna ji help karo",
        "Meri girlfriend ne breakup kar diya, bahut dukh ho raha hai",
        "Papa se bahut fight ho gayi, kya karu?",
        "Health issues hai, doctor se milna chahiye?"
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
        "test_cases": results
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
