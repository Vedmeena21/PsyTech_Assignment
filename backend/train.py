"""
Training Script for Multi-Task Hinglish Classifier (5K Dataset)

Loads data from train_5000.jsonl and trains the model
"""

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import AutoTokenizer
import json
import os
from multitask_model import MultiTaskModel, SENTIMENT_LABELS, TOXICITY_LABELS, CATEGORY_LABELS


class HinglishDataset(Dataset):
    """Dataset for multi-task training."""
    
    def __init__(self, data: list, tokenizer, max_length: int = 128):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        # Label mappings
        self.sentiment_to_idx = {label: i for i, label in enumerate(SENTIMENT_LABELS)}
        self.toxicity_to_idx = {label: i for i, label in enumerate(TOXICITY_LABELS)}
        self.category_to_idx = {label: i for i, label in enumerate(CATEGORY_LABELS)}
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        
        # Tokenize text
        tokens = self.tokenizer(
            item["text"],
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt"
        )
        
        # Sentiment label (single class)
        sentiment_label = self.sentiment_to_idx[item["sentiment"]]
        
        # Toxicity label (single class)
        toxicity_label = self.toxicity_to_idx[item["toxicity"]]
        
        # Category labels (multi-label binary vector)
        category_labels = torch.zeros(len(CATEGORY_LABELS))
        for cat in item["categories"]:
            if cat in self.category_to_idx:
                category_labels[self.category_to_idx[cat]] = 1.0
        
        return {
            "input_ids": tokens["input_ids"].squeeze(0),
            "attention_mask": tokens["attention_mask"].squeeze(0),
            "sentiment_label": torch.tensor(sentiment_label),
            "toxicity_label": torch.tensor(toxicity_label),
            "category_labels": category_labels
        }


def compute_class_weights(data: list) -> dict:
    """Compute class weights for imbalanced data."""
    from collections import Counter
    
    # Count sentiment classes
    sentiment_counts = Counter([d["sentiment"] for d in data])
    sentiment_weights = {
        label: len(data) / (len(SENTIMENT_LABELS) * count)
        for label, count in sentiment_counts.items()
    }
    
    # Count toxicity classes
    toxicity_counts = Counter([d["toxicity"] for d in data])
    toxicity_weights = {
        label: len(data) / (len(TOXICITY_LABELS) * max(count, 1))
        for label, count in toxicity_counts.items()
    }
    
    return {
        "sentiment": [sentiment_weights.get(label, 1.0) for label in SENTIMENT_LABELS],
        "toxicity": [toxicity_weights.get(label, 1.0) for label in TOXICITY_LABELS]
    }


def load_jsonl(filepath: str) -> list:
    """Load data from JSONL file."""
    data = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line))
    return data


def train_model(
    train_data: list,
    val_data: list = None,
    epochs: int = 5,
    batch_size: int = 16,
    learning_rate: float = 2e-5,
    freeze_epochs: int = 1,
    checkpoint_path: str = "checkpoints/model.pt"
):
    """Train the multi-task model."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🔧 Training on device: {device}")
    
    # Initialize tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained("xlm-roberta-base")
    model = MultiTaskModel().to(device)
    
    # Create datasets
    train_dataset = HinglishDataset(train_data, tokenizer)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    
    if val_data:
        val_dataset = HinglishDataset(val_data, tokenizer)
        val_loader = DataLoader(val_dataset, batch_size=batch_size)
    
    # Compute class weights
    class_weights = compute_class_weights(train_data)
    
    # Loss functions with class weights
    sentiment_criterion = nn.CrossEntropyLoss(
        weight=torch.tensor(class_weights["sentiment"]).to(device)
    )
    toxicity_criterion = nn.CrossEntropyLoss(
        weight=torch.tensor(class_weights["toxicity"]).to(device)
    )
    category_criterion = nn.BCEWithLogitsLoss()
    
    # Optimizer
    optimizer = AdamW(model.parameters(), lr=learning_rate)
    
    # Training loop
    print(f"\n🚀 Starting training for {epochs} epochs...")
    print(f"   Training samples: {len(train_data)}")
    print(f"   Batch size: {batch_size}")
    print(f"   Learning rate: {learning_rate}")
    print(f"   Freeze encoder for: {freeze_epochs} epoch(s)")
    
    best_val_loss = float("inf")
    
    for epoch in range(epochs):
        # Freeze/unfreeze encoder
        if epoch < freeze_epochs:
            for param in model.encoder.parameters():
                param.requires_grad = False
            print(f"\n📌 Epoch {epoch + 1}/{epochs} (encoder FROZEN)")
        else:
            for param in model.encoder.parameters():
                param.requires_grad = True
            if epoch == freeze_epochs:
                print(f"\n🔓 Epoch {epoch + 1}/{epochs} (encoder UNFROZEN)")
            else:
                print(f"\n📊 Epoch {epoch + 1}/{epochs}")
        
        model.train()
        total_loss = 0.0
        
        for batch_idx, batch in enumerate(train_loader):
            # Move to device
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            sentiment_labels = batch["sentiment_label"].to(device)
            toxicity_labels = batch["toxicity_label"].to(device)
            category_labels = batch["category_labels"].to(device)
            
            # Forward pass
            optimizer.zero_grad()
            outputs = model(input_ids, attention_mask)
            
            # Compute losses
            sentiment_loss = sentiment_criterion(outputs["sentiment"], sentiment_labels)
            toxicity_loss = toxicity_criterion(outputs["toxicity"], toxicity_labels)
            category_loss = category_criterion(outputs["categories"], category_labels)
            
            # Combined loss (as specified)
            loss = sentiment_loss + toxicity_loss + 0.8 * category_loss
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
            if (batch_idx + 1) % 50 == 0:
                print(f"   Batch {batch_idx + 1}/{len(train_loader)}: loss = {loss.item():.4f}")
        
        avg_train_loss = total_loss / len(train_loader)
        print(f"   Average train loss: {avg_train_loss:.4f}")
        
        # Validation
        if val_data:
            model.eval()
            val_loss = 0.0
            
            with torch.no_grad():
                for batch in val_loader:
                    input_ids = batch["input_ids"].to(device)
                    attention_mask = batch["attention_mask"].to(device)
                    sentiment_labels = batch["sentiment_label"].to(device)
                    toxicity_labels = batch["toxicity_label"].to(device)
                    category_labels = batch["category_labels"].to(device)
                    
                    outputs = model(input_ids, attention_mask)
                    
                    sentiment_loss = sentiment_criterion(outputs["sentiment"], sentiment_labels)
                    toxicity_loss = toxicity_criterion(outputs["toxicity"], toxicity_labels)
                    category_loss = category_criterion(outputs["categories"], category_labels)
                    
                    loss = sentiment_loss + toxicity_loss + 0.8 * category_loss
                    val_loss += loss.item()
            
            avg_val_loss = val_loss / len(val_loader)
            print(f"   Validation loss: {avg_val_loss:.4f}")
            
            # Save best model
            if avg_val_loss < best_val_loss:
                best_val_loss = avg_val_loss
                os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
                torch.save(model.state_dict(), checkpoint_path)
                print(f"   ✅ Saved best model to {checkpoint_path}")
    
    # Save final model if no validation data
    if not val_data:
        os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
        torch.save(model.state_dict(), checkpoint_path)
        print(f"\n✅ Training complete! Model saved to {checkpoint_path}")
    else:
        print(f"\n✅ Training complete! Best model saved to {checkpoint_path}")
    
    return model


if __name__ == "__main__":
    print("=" * 60)
    print("🎯 Multi-Task Hinglish Classifier Training (5K Dataset)")
    print("=" * 60)
    
    # Load data from JSONL
    print("\n📂 Loading data from train_5000.jsonl...")
    all_data = load_jsonl("train_5000.jsonl")
    print(f"   Loaded {len(all_data)} samples")
    
    # Split data (80% train, 20% validation)
    import random
    random.shuffle(all_data)
    split_idx = int(len(all_data) * 0.8)
    train_data = all_data[:split_idx]
    val_data = all_data[split_idx:]
    
    print(f"   Train samples: {len(train_data)}")
    print(f"   Validation samples: {len(val_data)}")
    
    # Train model
    model = train_model(
        train_data=train_data,
        val_data=val_data,
        epochs=5,
        batch_size=16,
        learning_rate=2e-5,
        freeze_epochs=1,
        checkpoint_path="checkpoints/model.pt"
    )
    
    print("\n" + "=" * 60)
    print("✅ Training complete!")
    print("   Restart the backend to load the trained model.")
    print("=" * 60)
