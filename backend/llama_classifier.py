"""
Llama 3.2 Classifier - 5-Tier Hybrid System
Complete production-ready implementation for Hinglish classification
"""
import requests
import json
import re
from typing import Dict, Optional, List

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TIER 1: COMPOUND STATEMENT HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def handle_compound_statements(text: str) -> Optional[str]:
    """
    Handles 'X par/but Y' statements - negative part dominates
    Examples:
    - "Job achhi hai par ghar se door" → negative
    - "Salary mili par kam hai" → negative
    """
    text_lower = text.lower()
    
    # Check for compound patterns
    compound_patterns = [" par ", " but ", " lekin ", " magar "]
    has_compound = any(pattern in text_lower for pattern in compound_patterns)
    
    if not has_compound:
        return None
    
    # Negative indicators after "par/but"
    negative_after = ["door", "kam", "nahi", "problem", "tension", "mushkil", "difficult"]
    
    # Check if negative part comes after compound word
    for pattern in compound_patterns:
        if pattern in text_lower:
            after_part = text_lower.split(pattern, 1)[1] if pattern in text_lower else ""
            if any(neg in after_part for neg in negative_after):
                return "negative"
    
    return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TIER 2: ACHIEVEMENT DETECTOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def detect_achievement_sentiment(text: str) -> Optional[str]:
    """
    Achievements = always positive
    Examples:
    - "First salary mili" → positive
    - "Promotion mil gaya" → positive
    - "Interview clear hua" → positive
    """
    text_lower = text.lower()
    
    # Achievement patterns: [achievement word] + [success word]
    achievement_words = ["salary", "promotion", "job", "project", "increment", "appraisal"]
    success_words = ["mili", "mil gaya", "mil gayi", "clear", "selected", "success", "ban gaya"]
    
    # Check for achievement + success combination
    has_achievement = any(word in text_lower for word in achievement_words)
    has_success = any(word in text_lower for word in success_words)
    
    if has_achievement and has_success:
        # Make sure there's no negation
        negations = ["nahi", "not", "cancel", "reject", "fail"]
        has_negation = any(neg in text_lower for neg in negations)
        
        if not has_negation:
            return "positive"
    
    return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TIER 3: FAMILY CONTEXT DETECTOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def detect_family_vs_personal(text: str) -> Optional[str]:
    """
    Distinguish family member's issues vs family relationships
    Examples:
    - "Maa ki tabiyat" → health (her health)
    - "Maa se baat nahi" → family (relationship)
    - "Bhai ki engagement" → family (his event)
    """
    text_lower = text.lower()
    
    family_members = ["maa", "papa", "bhai", "behen", "father", "mother", "sister", "brother"]
    has_family_member = any(member in text_lower for member in family_members)
    
    if not has_family_member:
        return None
    
    # Health indicators - if present, it's about their health
    health_indicators = ["tabiyat", "bimar", "health", "doctor", "hospital", "medicine", "checkup"]
    has_health = any(indicator in text_lower for indicator in health_indicators)
    
    if has_health:
        return "health"
    
    # Family events - sibling's events are family category
    family_events = ["engagement", "shaadi", "wedding", "marriage"]
    has_event = any(event in text_lower for event in family_events)
    
    if has_event and ("bhai" in text_lower or "behen" in text_lower or "sister" in text_lower or "brother" in text_lower):
        return "family"
    
    # Relationship issues - communication with family
    relationship_words = ["baat", "fight", "gussa", "naraz", "communication", "talk"]
    has_relationship = any(word in text_lower for word in relationship_words)
    
    if has_relationship:
        return "family"
    
    return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TIER 4: KEYWORD MATCHING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_category_by_keywords(text: str) -> Optional[str]:
    """Strong keyword rules - 95% confidence"""
    text_lower = text.lower()
    
    # Define strong keywords for each category
    career_kw = ["salary", "job", "boss", "client", "office", "interview", "promotion", 
                 "meeting", "work", "colleague", "project", "increment", "appraisal",
                 "resignation", "presentation", "team", "manager"]
    
    love_kw = ["propose", "dating", "girlfriend", "boyfriend", "crush", "breakup", 
               "relationship", "love", "valentine", "ex", "partner"]
    
    family_kw = ["maa", "papa", "bhai", "behen", "family", "shaadi", "engagement",
                 "parents", "father", "mother", "sister", "brother", "relatives",
                 "gharwale", "dadi", "nani"]
    
    health_kw = ["doctor", "hospital", "medicine", "bimar", "tabiyat", "checkup", 
                 "health", "treatment", "surgery", "fever", "pain", "covid",
                 "dentist", "gym", "fitness", "diet", "blood pressure"]
    
    mood_kw = ["bore", "lonely", "akela", "depressed", "anxiety", "tension", 
               "stress", "excited", "peaceful", "motivate", "sad", "khush"]
    
    # Count matches
    career_score = sum(1 for kw in career_kw if kw in text_lower)
    love_score = sum(1 for kw in love_kw if kw in text_lower)
    family_score = sum(1 for kw in family_kw if kw in text_lower)
    health_score = sum(1 for kw in health_kw if kw in text_lower)
    mood_score = sum(1 for kw in mood_kw if kw in text_lower)
    
    scores = {
        "career": career_score,
        "love_life": love_score,
        "family": family_score,
        "health": health_score,
        "mood": mood_score
    }
    
    max_score = max(scores.values())
    
    # If 2+ matches, return category
    if max_score >= 2:
        return max(scores, key=scores.get)
    
    # Single strong indicator
    if "interview" in text_lower or "client" in text_lower or "boss" in text_lower:
        return "career"
    if "girlfriend" in text_lower or "boyfriend" in text_lower or "propose" in text_lower:
        return "love_life"
    if "doctor" in text_lower or "hospital" in text_lower:
        return "health"
    
    return None


def get_sentiment_by_keywords(text: str) -> Optional[str]:
    """Strong sentiment indicators"""
    text_lower = text.lower()
    
    # Positive indicators
    positive_kw = ["mili", "selected", "clear", "success", "promotion", "increase", 
                   "achha", "khush", "happy", "mast", "badiya", "fix ho gayi",
                   "mil gaya", "ban gaya", "selected"]
    
    # Negative indicators
    negative_kw = ["cancel", "nahi", "fight", "problem", "tension", "breakup", 
                   "reject", "fail", "gussa", "sad", "udaas", "dukhi", "bore",
                   "door", "ignore", "theek nahi"]
    
    # Neutral indicators
    neutral_kw = ["kya", "kaise", "plan", "karwani hai", "chahiye", "karu"]
    
    # Count matches
    pos_count = sum(1 for kw in positive_kw if kw in text_lower)
    neg_count = sum(1 for kw in negative_kw if kw in text_lower)
    neu_count = sum(1 for kw in neutral_kw if kw in text_lower)
    
    # Strong negative patterns
    if "nahi hua" in text_lower or "theek nahi" in text_lower or "nahi mil" in text_lower:
        return "negative"
    
    # Strong negative (2+ negative words)
    if neg_count >= 2:
        return "negative"
    
    # Strong positive (2+ positive words)
    if pos_count >= 2:
        return "positive"
    
    # Single strong indicator
    if neg_count > pos_count and neg_count >= 1:
        return "negative"
    elif pos_count > neg_count and pos_count >= 1:
        return "positive"
    elif neu_count >= 1 and pos_count == 0 and neg_count == 0:
        return "neutral"
    
    return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TIER 5: LLAMA 3.2 WITH CHAIN-OF-THOUGHT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class LlamaClassifier:
    """
    Llama 3.2 classifier with chain-of-thought reasoning
    Uses 5-tier pipeline for maximum accuracy
    """
    
    def __init__(self, ollama_url="http://localhost:11434"):
        self.ollama_url = ollama_url
        self.api_endpoint = f"{ollama_url}/api/generate"
        self.model = "llama3.2:3b"
        
        # Test Ollama availability
        self.ollama_available = self._test_ollama()
        if self.ollama_available:
            print("✅ Ollama connected: llama3.2:3b")
        else:
            print("⚠️  Ollama not available - will use fallback")
        
        # Sentiment examples (20 total)
        self.sentiment_examples = [
            ("First salary mili aaj", "positive", "achievement"),
            ("Client meeting cancel ho gayi", "negative", "disappointment"),
            ("Propose karne ka plan bana raha hu", "positive", "hopeful"),
            ("Boss se fight ho gayi", "negative", "conflict"),
            ("Bhai ki engagement hai next month", "positive", "family joy"),
            ("Job achhi hai par ghar se door", "negative", "problem dominates"),
            ("Promotion ka chance lag raha", "positive", "opportunity"),
            ("Interview clear nahi hua", "negative", "failure"),
            ("Kya karu samajh nahi aa raha", "neutral", "question"),
            ("Health checkup karwani hai", "neutral", "planning"),
            ("Maa ki tabiyat theek nahi", "negative", "worry"),
            ("Girlfriend se breakup ho gaya", "negative", "loss"),
            ("Naya project mila office mein", "positive", "achievement"),
            ("Crush ne baat nahi ki", "negative", "rejection"),
            ("Family dinner plan kar rahe", "positive", "anticipation"),
            ("Salary increase ki umeed hai", "positive", "hope"),
            ("Papa gussa hain mujhse", "negative", "conflict"),
            ("Doctor ne medicine change kar di", "neutral", "update"),
            ("Bore ho raha hu ghar pe", "negative", "dissatisfaction"),
            ("Shaadi ki date fix ho gayi", "positive", "milestone")
        ]
        
        # Category examples (25 total)
        self.category_examples = [
            ("Client meeting cancel ho gayi", "career", "work context"),
            ("Bhai ki engagement hai", "family", "sibling event"),
            ("Boss se fight ho gayi", "career", "workplace"),
            ("Propose karne ka plan", "love_life", "romantic"),
            ("First salary mili", "career", "work achievement"),
            ("Girlfriend se breakup", "love_life", "relationship"),
            ("Maa ki tabiyat kharab", "health", "health issue"),
            ("Promotion ka chance", "career", "work progression"),
            ("Papa gussa hain", "family", "parent conflict"),
            ("Crush ne ignore kiya", "love_life", "romantic"),
            ("Interview clear nahi hua", "career", "job hunting"),
            ("Bore ho raha hu", "mood", "emotional state"),
            ("Health checkup karwani hai", "health", "medical"),
            ("Office mein tension", "career", "work stress"),
            ("Family dinner plan", "family", "family activity"),
            ("Dating app use karu kya", "love_life", "romantic"),
            ("Doctor ne medicine di", "health", "treatment"),
            ("Salary increase chahiye", "career", "compensation"),
            ("Behen ki shaadi", "family", "sibling event"),
            ("Akela feel ho raha hu", "mood", "loneliness"),
            ("Blood pressure high hai", "health", "condition"),
            ("Client presentation hai kal", "career", "work task"),
            ("Valentine's Day ka plan", "love_life", "romantic"),
            ("Maa-Papa se baat nahi", "family", "communication"),
            ("Anxiety ho rahi hai", "mood", "mental state")
        ]
    
    def _test_ollama(self) -> bool:
        """Test if Ollama is running"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def _call_ollama(self, prompt: str) -> Optional[str]:
        """Call Ollama API"""
        try:
            response = requests.post(
                self.api_endpoint,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.9,
                        "top_k": 40,
                        "num_predict": 150
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                return None
                
        except Exception as e:
            print(f"❌ Ollama call failed: {e}")
            return None
    
    def _parse_llama_response(self, response: str, valid_labels: List[str]) -> Optional[str]:
        """Extract classification from Llama's response"""
        if not response:
            return None
        
        # Look for "Classification: <label>" pattern
        match = re.search(r'Classification:\s*(\w+)', response, re.IGNORECASE)
        if match:
            label = match.group(1).lower()
            if label in valid_labels:
                return label
        
        # Fallback: check if any valid label appears in last line
        response_lower = response.lower()
        lines = response_lower.split('\n')
        last_line = lines[-1] if lines else response_lower
        
        for label in valid_labels:
            if label in last_line:
                return label
        
        return None
    
    def _format_sentiment_examples(self) -> str:
        """Format sentiment examples for prompt"""
        formatted = []
        for text, sentiment, reason in self.sentiment_examples:
            formatted.append(f'Input: "{text}"\nReasoning: {reason}\nClassification: {sentiment}\n')
        return "\n".join(formatted)
    
    def _format_category_examples(self) -> str:
        """Format category examples for prompt"""
        formatted = []
        for text, category, reason in self.category_examples:
            formatted.append(f'Input: "{text}"\nReasoning: {reason}\nClassification: {category}\n')
        return "\n".join(formatted)
    
    def classify_sentiment(self, text: str) -> Dict:
        """
        5-tier sentiment classification pipeline
        Returns: {"prediction": str, "confidence": float, "method": str}
        """
        
        # Tier 1: Compound statement handler
        result = handle_compound_statements(text)
        if result:
            return {"prediction": result, "confidence": 0.90, "method": "compound_rule"}
        
        # Tier 2: Achievement detector
        result = detect_achievement_sentiment(text)
        if result:
            return {"prediction": result, "confidence": 0.90, "method": "achievement_rule"}
        
        # Tier 3: Keyword matching
        result = get_sentiment_by_keywords(text)
        if result:
            return {"prediction": result, "confidence": 0.85, "method": "keywords"}
        
        # Tier 4: Llama 3.2 with chain-of-thought
        if self.ollama_available:
            prompt = f"""Analyze this Hinglish text: "{text}"

Think step by step:
1. Key emotional words? (achievements, problems, neutral facts)
2. Emotion expressed? (joy, hope, worry, anger, question)
3. Compound statement? Does negative dominate?

Classify as: positive, neutral, or negative

Examples:
{self._format_sentiment_examples()}

Now analyze: "{text}"
Reasoning:
Classification:"""
            
            llama_response = self._call_ollama(prompt)
            parsed = self._parse_llama_response(llama_response, ["positive", "negative", "neutral"])
            
            if parsed:
                return {"prediction": parsed, "confidence": 0.75, "method": "llama"}
        
        # Tier 5: No result - return None for Gemini fallback
        return None
    
    def classify_category(self, text: str) -> Dict:
        """
        5-tier category classification pipeline
        Returns: {"prediction": str, "confidence": float, "method": str}
        """
        
        # Tier 1: Family context detector
        result = detect_family_vs_personal(text)
        if result:
            return {"prediction": result, "confidence": 0.90, "method": "family_rule"}
        
        # Tier 2: Keyword matching
        result = get_category_by_keywords(text)
        if result:
            return {"prediction": result, "confidence": 0.95, "method": "keywords"}
        
        # Tier 3: Llama 3.2 with disambiguation
        if self.ollama_available:
            prompt = f"""Analyze this Hinglish text: "{text}"

Think step by step:
1. Key context words?
   - Work: salary, job, boss, client, office, meeting, interview
   - Romance: propose, dating, girlfriend, boyfriend, crush, love
   - Family: maa, papa, bhai, behen, family, shaadi, engagement
   - Health: doctor, hospital, medicine, tabiyat, bimar
   - Mood: bore, sad, khush, lonely, tension (standalone)

2. PRIMARY context?
   - "Meeting" + work words = career
   - "Bhai/Behen" + their events = family
   - "Propose" + romantic = love_life

3. Avoid confusion:
   - Family member's health → health
   - Sibling's wedding → family
   - Work meeting → career

Classify as: career, love_life, family, health, mood

Examples:
{self._format_category_examples()}

Now analyze: "{text}"
Reasoning:
Classification:"""
            
            llama_response = self._call_ollama(prompt)
            parsed = self._parse_llama_response(llama_response, ["career", "love_life", "family", "health", "mood"])
            
            if parsed:
                return {"prediction": parsed, "confidence": 0.75, "method": "llama"}
        
        # Tier 4: No result - return None for Gemini fallback
        return None
