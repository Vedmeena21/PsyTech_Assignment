"""
Synthetic Hinglish Dataset Generator for Krishna AI
Generates 5,000 high-quality training samples with realistic distribution
"""

import json
import random

random.seed(42)

TOTAL_SAMPLES = 5000

sentiments = ["positive", "neutral", "negative"]
sentiment_weights = [0.25, 0.30, 0.45]

toxicity_labels = ["safe", "offensive", "spam"]
toxicity_weights = [0.85, 0.10, 0.05]

categories = [
    "career",
    "love_life",
    "family_issues",
    "health_issues",
    "mood_issues"
]

# Hinglish sentence templates (semantic, not keyword-driven)
templates = {
    "career": [
        "Career ko lekar kaafi confusion chal rahi hai",
        "Job ke pressure ki wajah se stress mehsoos ho raha hai",
        "Apni skills improve karne ka soch raha hoon",
        "Office mein growth slow lag rahi hai",
        "Future career decision mushkil lag raha hai",
        "Work life balance maintain karna tough hai",
        "Professional goals achieve karne ki koshish kar raha hun",
        "Job satisfaction kam lag rahi hai",
        "Career switch ka soch raha hun",
        "Office politics se pareshan hun",
        "Promotion ke chances kam lag rahe hain",
        "New project mila hai exciting hai",
        "Boss ke saath understanding achhi hai",
        "Team ke saath collaboration achha chal raha hai",
        "Salary increment ki umeed hai"
    ],
    "love_life": [
        "Relationship mein understanding ki kami mehsoos hoti hai",
        "Partner ke saath bonding strong ho rahi hai",
        "Love life ko lekar mixed emotions hain",
        "Relationship ke future ko lekar doubt hai",
        "Emotional attachment decision ko tough bana raha hai",
        "Partner mujhe support kar raha hai",
        "Relationship mein trust issues hain",
        "Love life stable chal rahi hai",
        "Partner ke saath communication better ho raha hai",
        "Breakup ke baad recovery mushkil hai",
        "Naye relationship ki soch raha hun",
        "Partner ke expectations samajh nahi aa rahe",
        "Love life mein clarity aa rahi hai",
        "Relationship goals align ho rahe hain",
        "Partner ke saath future plan kar rahe hain"
    ],
    "family_issues": [
        "Parivaar ke expectations pressure create kar rahe hain",
        "Ghar ke issues mann ko disturb kar dete hain",
        "Family support se strength milti hai",
        "Family responsibilities badh rahi hain",
        "Parivaar ke saath balance banana mushkil hai",
        "Parents ke decisions samajh nahi aa rahe",
        "Siblings ke saath bonding achhi hai",
        "Family gatherings mein enjoy kar raha hun",
        "Ghar ke conflicts resolve ho rahe hain",
        "Family ke saath time spend karna achha lagta hai",
        "Parents ki health ko lekar chinta hai",
        "Family ke financial issues hain",
        "Ghar mein peace maintain karna mushkil hai",
        "Family traditions follow karna achha lagta hai",
        "Relatives ke saath relations achhe hain"
    ],
    "health_issues": [
        "Health ko lekar thodi chinta rehti hai",
        "Neend aur routine bigad gaya hai",
        "Stress ka effect health par dikh raha hai",
        "Health improve ho rahi hai par patience chahiye",
        "Mental aur physical balance maintain karna mushkil hai",
        "Exercise routine start kiya hai",
        "Diet improve karne ki koshish kar raha hun",
        "Health checkup karwana hai",
        "Fitness goals achieve kar raha hun",
        "Mental health pe focus kar raha hun",
        "Chronic pain se deal kar raha hun",
        "Energy levels better ho rahe hain",
        "Health conscious ban raha hun",
        "Medical treatment chal raha hai",
        "Wellness journey pe hun"
    ],
    "mood_issues": [
        "Aaj mann thoda heavy lag raha hai",
        "Emotions stable nahi lag rahe",
        "Mann shaant karne ki koshish kar raha hoon",
        "Thoughts kaafi overwhelming lag rahe hain",
        "Emotional clarity dheere dheere aa rahi hai",
        "Aaj mood achha hai",
        "Peaceful feel ho raha hai",
        "Anxiety ho rahi hai",
        "Khush hun aaj",
        "Udaas feel kar raha hun",
        "Motivated feel kar raha hun",
        "Bore ho raha hun",
        "Excited hun",
        "Frustrated hun",
        "Relaxed feel ho raha hai",
        "Tension free hun",
        "Stressed out hun",
        "Happy vibes aa rahe hain",
        "Emotional roller coaster chal raha hai",
        "Mann shaant hai"
    ]
}

offensive_templates = [
    "Tum log bilkul bekaar baatein karte ho",
    "Yeh sab faltu hai time waste hai",
    "Tumhari baat mein koi sense nahi",
    "Bakwas band karo",
    "Kisi ko maarna chahta hun",
    "I want to kill somebody",
    "Sab chutiye hain",
    "Duniya jalaa dunga",
    "Violence is the answer",
    "Suicide karna chahta hun",
    "Mujhe marna hai",
    "Tujhe maar dunga",
    "I hate everyone",
    "Sab ko khatam kar dunga",
    "Main apne aap ko hurt karunga"
]

spam_templates = [
    "Guaranteed success ke liye yahan join karo",
    "Is app se paisa double hoga",
    "Limited offer hai abhi click karo",
    "Fast money earning opportunity",
    "Free iPhone milega abhi register karo",
    "1 crore jeetne ka mauka link click karo",
    "Work from home earn 50000 daily",
    "Buy now 50% off limited time",
    "Click here for free money",
    "Lottery winner claim now"
]

# Positive phrases for variety
positive_templates = [
    "Me thik hu",
    "Main theek hun",
    "Sab achha hai",
    "Sab theek chal raha hai",
    "Bahut mast feel kar raha hun",
    "Aaj mood achha hai",
    "Happy hun aaj",
    "Khush hun main",
    "Life achhi chal rahi hai",
    "Everything is good",
    "I am fine",
    "I am doing well",
    "Feeling great today",
    "Aaj relax feel ho raha hai",
    "Tension free hun aaj",
    "Bahut energy hai aaj",
    "Mazaa aa raha hai",
    "Achha lag raha hai",
    "Sab kuch badiya hai",
    "All good"
]

# Neutral phrases
neutral_templates = [
    "Kya chal raha hai",
    "Kuch khaas nahi",
    "Normal hai sab",
    "Theek thak chal raha hai",
    "Aise hi",
    "Bas normal",
    "Kuch special nahi",
    "Same old same old",
    "Routine chal raha hai",
    "Nothing much",
    "Bas aise hi",
    "Kuch naya nahi"
]

def pick_categories():
    """Pick 1-3 categories with mood_issues bias"""
    num = random.choice([1, 1, 2, 2, 3])
    chosen = random.sample(categories, num)
    # 60% chance to include mood_issues
    if random.random() < 0.6 and "mood_issues" not in chosen:
        chosen.append("mood_issues")
    return list(set(chosen))

def generate_text(cats, toxicity, sentiment):
    """Generate Hinglish text based on categories, toxicity, and sentiment"""
    if toxicity == "offensive":
        return random.choice(offensive_templates)
    if toxicity == "spam":
        return random.choice(spam_templates)
    
    # For positive sentiment, sometimes use simple positive phrases
    if sentiment == "positive" and random.random() < 0.3:
        return random.choice(positive_templates)
    
    # For neutral sentiment, sometimes use simple neutral phrases
    if sentiment == "neutral" and random.random() < 0.2:
        return random.choice(neutral_templates)
    
    # Otherwise, combine category templates
    if not cats:
        cats = ["mood_issues"]
    
    parts = []
    for c in cats:
        parts.append(random.choice(templates[c]))
    
    # Join with connectors
    connectors = [" aur ", " par ", " lekin ", ", "]
    if len(parts) == 1:
        return parts[0]
    else:
        return random.choice(connectors).join(parts[:2])

data = []

for _ in range(TOTAL_SAMPLES):
    sentiment = random.choices(sentiments, sentiment_weights)[0]
    toxicity = random.choices(toxicity_labels, toxicity_weights)[0]
    
    if toxicity == "spam":
        cats = []
    else:
        cats = pick_categories()
    
    text = generate_text(cats if cats else ["mood_issues"], toxicity, sentiment)
    
    sample = {
        "text": text,
        "sentiment": sentiment,
        "toxicity": toxicity,
        "categories": cats
    }
    
    data.append(sample)

# Write to JSONL
with open("train_5000.jsonl", "w", encoding="utf-8") as f:
    for row in data:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

print("✅ Generated train_5000.jsonl with 5000 samples")
print(f"\n📊 Distribution:")
print(f"   Sentiment: {sum(1 for d in data if d['sentiment']=='positive')} positive, "
      f"{sum(1 for d in data if d['sentiment']=='neutral')} neutral, "
      f"{sum(1 for d in data if d['sentiment']=='negative')} negative")
print(f"   Toxicity: {sum(1 for d in data if d['toxicity']=='safe')} safe, "
      f"{sum(1 for d in data if d['toxicity']=='offensive')} offensive, "
      f"{sum(1 for d in data if d['toxicity']=='spam')} spam")
