import os
import json
import google.generativeai as genai
from transformers import pipeline
import requests

class DevotionalAnalyzer:
    def __init__(self):
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        
        genai.configure(api_key=api_key)
        
        # Use Gemini for fallback only
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Configure generation settings
        self.generation_config = {
            "temperature": 0.3,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 512,
        }
        
        # Initialize Llama 3.2 classifier (primary)
        print("Initializing Llama 3.2 classifier...")
        from llama_classifier import LlamaClassifier
        self.llama_classifier = LlamaClassifier()
        print("✅ Llama classifier ready")
        
        # Load dedicated sentiment analysis model (fallback)
        print("Loading sentiment analysis model...")
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-xlm-roberta-base-sentiment",
            tokenizer="cardiffnlp/twitter-xlm-roberta-base-sentiment"
        )
        print("✅ Sentiment model loaded successfully")
        
        # Load local toxicity detection model (small, fast, works offline)
        print("Loading toxicity detection model...")
        self.toxicity_analyzer = pipeline(
            "text-classification",
            model="unitary/toxic-bert",
            top_k=None
        )
        print("✅ Toxicity model loaded successfully")
        
        # Load sentence embedding model for category classification (fallback)
        print("Loading embedding model for category classification...")
        from sentence_transformers import SentenceTransformer
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Embedding model loaded successfully")
        
        # Define category templates with example phrases (more specific to reduce false positives)
        self.category_templates = {
            "career": [
                # Job search & interviews
                "job nahi mil rahi", "interview fail", "interview achha gaya",
                "interview mein selected", "interview diya", "job interview",
                "promotion nahi mila", "career growth", "work stress", 
                # Office & workplace
                "office problems", "boss issues", "salary problem", 
                "job search", "unemployment", "fired from job",
                "office politics", "work pressure", "colleague issue",
                # Generic workplace
                "office ja raha", "meeting hai", "appraisal", "team lead",
                "naukri mil gayi", "naukri", "kaam",
                # Hindi/Hinglish
                "नौकरी नहीं मिल रही", "करियर की समस्या", "काम में परेशानी",
                "इंटरव्यू", "नौकरी की तलाश", "ऑफिस की समस्या"
            ],
            "love_life": [
                "girlfriend breakup", "boyfriend left", "relationship problems",
                "love marriage", "propose karna hai", "pyaar mein dhoka",
                "breakup ho gaya", "partner cheating", "love failure",
                # Marriage related
                "shaadi nahi ho rahi", "marriage", "wedding",
                "प्यार में धोखा", "रिश्ते की समस्या", "शादी की समस्या",
                "girlfriend ne choda", "boyfriend issue", "dating problem"
            ],
            "family": [
                "papa se fight", "mummy naraz", "family problems", "parents issue",
                "sibling fight", "ghar mein kalesh", "family tension",
                "parents divorce", "family conflict", "home issues",
                # Generic family/home
                "ghar par hun", "papa khush", "brother se ladai", "sister",
                "परिवार में झगड़ा", "माता-पिता से लड़ाई", "घर की समस्या",
                "father angry", "mother upset", "brother sister fight"
            ],
            "health": [
                "bimar hun", "health problem", "pain hai", "doctor ke paas",
                "medicine", "hospital", "illness", "disease", "surgery",
                "chronic pain", "medical issue", "body ache",
                # Specific conditions
                "fever", "headache", "stomach pain", "tabiyat",
                # Hindi
                "बीमार हूं", "स्वास्थ्य समस्या", "दर्द है"
            ],
            "mood": [
                # English
                "depressed", "sad", "anxiety", "mental health",
                "tension", "stress", "worried", "upset", "lonely",
                "suicidal thoughts", "panic attack", "emotional",
                "feeling low", "not happy", "crying", "hopeless",
                # Hinglish (key additions for better detection)
                "udaas hun", "dukhi hun", "khush nahi hun",
                "bahut tension hai", "depressed hun", "sad hun",
                "anxiety hai", "stress mein hun", "worried hun",
                "akela hun", "lonely feel kar raha hun",
                # Positive mood (important!)
                "khush hun", "happy hun", "mast hun", "badiya hai",
                "achha feel kar raha hun", "perfect hai", "theek hai",
                # Negative mood variations
                "pareshan hun", "bura lag raha hai", "galat ho raha hai",
                "kuch achha nahi", "sab kuch bura",
                # Pure Hindi
                "उदास हूं", "दुखी हूं", "चिंतित हूं", "तनाव में हूं",
                "अकेला हूं", "परेशान हूं", "खुश हूं"
            ]
        }
        
        # Pre-compute embeddings for all category templates
        print("Computing category embeddings...")
        self.category_embeddings = {}
        for category, phrases in self.category_templates.items():
            self.category_embeddings[category] = self.embedding_model.encode(phrases)
        print("✅ Category classification ready")
    
    def analyze(self, text: str) -> dict:
        """
        Analyze devotional content using Llama 3.2 5-tier system with Gemini fallback
        
        Args:
            text: User input text (Hinglish)
        
        Returns:
            dict: {
                "sentiment": {"label": str, "confidence": float},
                "toxicity": {"label": str, "confidence": float},
                "categories": [{"label": str, "confidence": float}, ...]
            }
        """
        
        try:
            # Use Llama 3.2 classifier (5-tier system)
            sentiment_result = self.llama_classifier.classify_sentiment(text)
            category_result = self.llama_classifier.classify_category(text)
            
            # Gemini fallback if Llama returns None
            if not sentiment_result:
                print("DEBUG: Using Gemini fallback for sentiment")
                try:
                    from few_shot_classifier import FewShotClassifier
                    gemini = FewShotClassifier()
                    gemini_sent = gemini.classify_sentiment(text)
                    sentiment_result = {"prediction": gemini_sent, "confidence": 0.60, "method": "gemini"}
                except Exception as e:
                    print(f"Gemini sentiment failed: {e}")
                    # Final fallback to ML model
                    ml_sent = self._analyze_sentiment(text)
                    sentiment_result = {"prediction": ml_sent["label"], "confidence": ml_sent["confidence"], "method": "ml_model"}
            
            if not category_result:
                print("DEBUG: Using Gemini fallback for category")
                try:
                    from few_shot_classifier import FewShotClassifier
                    gemini = FewShotClassifier()
                    gemini_cat = gemini.classify_category(text)
                    category_result = {"prediction": gemini_cat[0]["label"] if gemini_cat else "mood", "confidence": 0.60, "method": "gemini"}
                except Exception as e:
                    print(f"Gemini category failed: {e}")
                    # Final fallback to ML model
                    ml_cat = self._analyze_categories(text)
                    category_result = {"prediction": ml_cat[0]["label"] if ml_cat else "mood", "confidence": ml_cat[0]["confidence"] if ml_cat else 0.5, "method": "ml_model"}
            
            # Toxicity always uses local BERT (100% working)
            toxicity_result = self._analyze_toxicity(text)
            
            # Format response
            return {
                "sentiment": {
                    "label": sentiment_result["prediction"],
                    "confidence": sentiment_result["confidence"],
                    "method": sentiment_result["method"]
                },
                "toxicity": toxicity_result,
                "categories": [{
                    "label": category_result["prediction"],
                    "confidence": category_result["confidence"],
                    "method": category_result["method"]
                }]
            }
            
        except Exception as e:
            print(f"Analysis error: {e}")
            import traceback
            traceback.print_exc()
            return self._get_default_response()
    
    def _analyze_sentiment(self, text: str) -> dict:
        """Use dedicated transformer model for sentiment analysis"""
        try:
            result = self.sentiment_analyzer(text)[0]
            
            # Map model labels to our format
            label_map = {
                "positive": "positive",
                "neutral": "neutral",
                "negative": "negative",
                "LABEL_0": "negative",  # Some models use LABEL_X format
                "LABEL_1": "neutral",
                "LABEL_2": "positive"
            }
            
            label = label_map.get(result['label'].lower(), result['label'].lower())
            confidence = float(result['score'])
            
            return {
                "label": label,
                "confidence": round(confidence, 2)
            }
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            return {"label": "neutral", "confidence": 0.5}
    
    
    
    def _analyze_toxicity(self, text: str) -> dict:
        """
        Local toxicity detection using transformer model
        Fast, offline, no API calls
        """
        try:
            # Run toxicity classification
            results = self.toxicity_analyzer(text)
            
            # Results format: [[{"label": "toxic", "score": 0.99}, {"label": "obscene", "score": 0.01}, ...]]
            if results and len(results) > 0:
                scores = results[0]
                
                # Find toxic score
                toxic_score = 0.0
                for item in scores:
                    if item['label'] == 'toxic':
                        toxic_score = item['score']
                        break
                
                print(f"DEBUG: Toxicity score: {toxic_score:.2f}")
                
                # Classify based on toxic score
                if toxic_score > 0.7:
                    return {"label": "offensive", "confidence": round(toxic_score, 2)}
                elif toxic_score > 0.4:
                    return {"label": "offensive", "confidence": round(toxic_score, 2)}
                else:
                    # Check for spam keywords
                    if self._is_spam(text):
                        return {"label": "spam", "confidence": 0.85}
                    return {"label": "safe", "confidence": round(1.0 - toxic_score, 2)}
            
            return {"label": "safe", "confidence": 0.75}
            
        except Exception as e:
            print(f"Toxicity detection error: {e}")
            return {"label": "safe", "confidence": 0.5}
    
    def _is_spam(self, text: str) -> bool:
        """Simple spam detection"""
        spam_keywords = ['buy', 'sale', 'discount', 'offer', 'click here', 'limited time', 'deal', 'promotion']
        text_lower = text.lower()
        spam_count = sum(1 for kw in spam_keywords if kw in text_lower)
        return spam_count >= 2
    
    
    def _analyze_categories(self, text: str) -> list:
        """
        Local category classification using sentence embeddings
        Computes similarity between input text and category templates
        """
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np
            
            # Encode the input text
            text_embedding = self.embedding_model.encode([text])
            
            # Calculate similarity with each category
            category_scores = {}
            for category, template_embeddings in self.category_embeddings.items():
                # Compute cosine similarity with all templates in this category
                similarities = cosine_similarity(text_embedding, template_embeddings)[0]
                # Use max similarity as the category score
                category_scores[category] = float(np.max(similarities))
            
            print(f"DEBUG: Category scores: {category_scores}")
            
            # Filter categories with confidence > 0.40 (balanced threshold)
            # Captures valid categories while filtering noise
            categories = [
                {"label": cat, "confidence": round(score, 2)}
                for cat, score in category_scores.items()
                if score > 0.40  # Lowered from 0.45
            ]
            categories.sort(key=lambda x: x['confidence'], reverse=True)
            
            # Return top 2 most relevant categories
            return categories[:2]
            
        except Exception as e:
            print(f"Category classification error: {e}")
            return []
    
    def _get_default_response(self):
        """Fallback response if everything fails"""
        return {
            "sentiment": {"label": "neutral", "confidence": 0.5},
            "toxicity": {"label": "safe", "confidence": 0.9},
            "categories": []
        }
