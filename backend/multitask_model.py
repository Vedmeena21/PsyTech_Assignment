"""
Multi-Task Transformer Model for Krishna AI Content Analyzer

Single XLM-RoBERTa encoder with 3 classification heads:
- Sentiment: positive, neutral, negative
- Toxicity: safe, offensive, spam  
- Category: career, love_life, family_issues, health_issues, mood_issues (multi-label)

NO keyword logic. NO rules. Pure probabilistic inference.
"""

import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer

# Fixed label definitions
SENTIMENT_LABELS = ["positive", "neutral", "negative"]
TOXICITY_LABELS = ["safe", "offensive", "spam"]
CATEGORY_LABELS = ["career", "love_life", "family_issues", "health_issues", "mood_issues"]


class MultiTaskModel(nn.Module):
    """
    Multi-task transformer with shared XLM-RoBERTa encoder
    and 3 task-specific classification heads.
    """
    
    def __init__(self, model_name: str = "xlm-roberta-base"):
        super().__init__()
        
        # Shared encoder
        self.encoder = AutoModel.from_pretrained(model_name)
        hidden_size = self.encoder.config.hidden_size
        
        # Task-specific heads
        self.sentiment_head = nn.Linear(hidden_size, len(SENTIMENT_LABELS))
        self.toxicity_head = nn.Linear(hidden_size, len(TOXICITY_LABELS))
        self.category_head = nn.Linear(hidden_size, len(CATEGORY_LABELS))
    
    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> dict:
        """
        Forward pass through shared encoder and all heads.
        
        Args:
            input_ids: Token IDs [batch_size, seq_len]
            attention_mask: Attention mask [batch_size, seq_len]
        
        Returns:
            dict with logits for each task
        """
        # Get encoder output
        encoder_output = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        
        # Use [CLS] token representation
        cls_embedding = encoder_output.last_hidden_state[:, 0]
        
        # Pass through each head
        return {
            "sentiment": self.sentiment_head(cls_embedding),
            "toxicity": self.toxicity_head(cls_embedding),
            "categories": self.category_head(cls_embedding)
        }


class Analyzer:
    """
    Content analyzer using multi-task transformer.
    Pure probabilistic inference - no rules or keywords.
    """
    
    def __init__(self, checkpoint_path: str = None):
        """
        Initialize analyzer with model and tokenizer.
        
        Args:
            checkpoint_path: Path to trained model weights (optional)
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🔧 Initializing Analyzer on device: {self.device}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained("xlm-roberta-base")
        
        # Load model
        self.model = MultiTaskModel().to(self.device)
        
        # Load trained weights if available
        if checkpoint_path:
            try:
                state_dict = torch.load(checkpoint_path, map_location=self.device)
                self.model.load_state_dict(state_dict)
                print(f"✅ Loaded weights from {checkpoint_path}")
            except Exception as e:
                print(f"⚠️ Could not load weights: {e}")
                print("   Using randomly initialized model")
        else:
            print("⚠️ No checkpoint provided - using untrained model")
            print("   Results will be random until model is trained")
        
        self.model.eval()
        print("✅ Analyzer ready")
    
    def analyze(self, text: str, category_threshold: float = 0.4) -> dict:
        """
        Analyze text and return predictions with confidence scores.
        
        Pure probabilistic inference:
        - Sentiment: softmax -> argmax
        - Toxicity: softmax -> argmax
        - Categories: sigmoid -> threshold
        
        Args:
            text: Input text (Hinglish supported)
            category_threshold: Threshold for multi-label categories
        
        Returns:
            dict with predictions and confidence scores
        """
        # Tokenize input
        tokens = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        ).to(self.device)
        
        # Inference (no gradients needed)
        with torch.no_grad():
            outputs = self.model(
                input_ids=tokens["input_ids"],
                attention_mask=tokens["attention_mask"]
            )
        
        # Compute probabilities
        sentiment_probs = torch.softmax(outputs["sentiment"], dim=-1)[0]
        toxicity_probs = torch.softmax(outputs["toxicity"], dim=-1)[0]
        category_probs = torch.sigmoid(outputs["categories"])[0]
        
        # Get predictions
        sentiment_idx = sentiment_probs.argmax().item()
        toxicity_idx = toxicity_probs.argmax().item()
        
        # Build category list (multi-label with threshold)
        categories = []
        for i, label in enumerate(CATEGORY_LABELS):
            prob = float(category_probs[i])
            if prob > category_threshold:
                categories.append({
                    "label": label,
                    "confidence": round(prob, 3)
                })
        
        # Sort categories by confidence (descending)
        categories.sort(key=lambda x: x["confidence"], reverse=True)
        
        return {
            "sentiment": {
                "label": SENTIMENT_LABELS[sentiment_idx],
                "confidence": round(float(sentiment_probs[sentiment_idx]), 3)
            },
            "toxicity": {
                "label": TOXICITY_LABELS[toxicity_idx],
                "confidence": round(float(toxicity_probs[toxicity_idx]), 3)
            },
            "categories": categories
        }
