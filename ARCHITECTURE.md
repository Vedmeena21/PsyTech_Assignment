# System Architecture - Krishna AI Content Analyzer

**Purpose:** This document explains the system architecture for engineers joining the project.

---

## High-Level Overview

This is a **content analysis API** that classifies Hinglish text across three dimensions:
1. **Sentiment:** positive, negative, neutral
2. **Toxicity:** safe, offensive, spam  
3. **Category:** career, love_life, family, health, mood

**Core Challenge:** Hinglish (Hindi-English code-mixing) breaks most NLP tools.

**Our Solution:** Hybrid system combining fast rules with LLM reasoning.

---

## System Components

```
┌──────────────┐
│   Client     │ (React frontend or API consumer)
└──────┬───────┘
       │ HTTP POST /analyze
       ▼
┌──────────────────────────────────────────────┐
│         Flask API Server (app.py)            │
│  - Request validation                        │
│  - Error handling                            │
│  - Response formatting                       │
└──────┬───────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│    DevotionalAnalyzer (models.py)            │
│  - Loads all models at startup               │
│  - Orchestrates classification tasks         │
│  - Combines results from multiple classifiers│
└──────┬───────────────────────────────────────┘
       │
       ├─────────────┬──────────────┬──────────────┐
       ▼             ▼              ▼              ▼
┌─────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│Llama        │ │Toxicity  │ │Sentiment │ │Category  │
│Classifier   │ │BERT      │ │BERT      │ │Embedding │
│(5 tiers)    │ │          │ │          │ │          │
└─────────────┘ └──────────┘ └──────────┘ └──────────┘
```

---

## Data Flow

### Request Path

```
1. Client sends POST /analyze
   Body: {"text": "Kal interview hai, tension ho raha hai"}

2. app.py validates:
   - Request has JSON body
   - "text" field exists
   - Text is not empty

3. app.py calls analyzer.analyze(text)

4. DevotionalAnalyzer delegates:
   - Sentiment → LlamaClassifier.classify_sentiment()
   - Category → LlamaClassifier.classify_category()
   - Toxicity → self._analyze_toxicity() [local BERT]

5. LlamaClassifier runs 5-tier pipeline:
   Tier 1: Compound handler → No match
   Tier 2: Achievement detector → No match
   Tier 3: Family context → No match
   Tier 4: Keywords → Matches "interview" + "tension"
           Returns: {"prediction": "career", "confidence": 0.95, "method": "keywords"}
   
6. DevotionalAnalyzer formats response:
   {
     "sentiment": {"label": "negative", "confidence": 0.85, "method": "keywords"},
     "toxicity": {"label": "safe", "confidence": 0.98},
     "categories": [{"label": "career", "confidence": 0.95, "method": "keywords"}]
   }

7. app.py wraps in success envelope:
   {"success": true, "data": {...}}

8. Client receives response
```

---

## Why This Structure?

### Separation of Concerns

**app.py** - Transport Layer
- **Responsibility:** HTTP protocol, request/response formatting
- **Why separate:** We can swap Flask for FastAPI/gRPC without touching logic
- **What it doesn't do:** No ML, no business rules

**models.py** - Orchestration Layer
- **Responsibility:** Load models, coordinate classifiers, format results
- **Why separate:** Business logic isolated from transport and classification details
- **What it doesn't do:** No HTTP handling, no classification algorithms

**llama_classifier.py** - Classification Engine
- **Responsibility:** Implement 5-tier classification logic
- **Why separate:** Can be tested independently, reused in batch jobs
- **What it doesn't do:** No HTTP, no result formatting

### Why 5 Tiers?

**Design Principle:** Use the simplest method that works.

```
Tier 1-3: Special case handlers (90% confidence, <1ms)
  ↓ (if no match)
Tier 4: Keyword matching (85-95% confidence, <1ms)
  ↓ (if no match)
Tier 5: LLM reasoning (75% confidence, ~800ms)
  ↓ (if Ollama down)
Fallback: Gemini API (60% confidence, ~2-3s)
  ↓ (if API fails)
Final Fallback: Local BERT (50% confidence, <100ms)
```

**Why not just use LLM for everything?**
- Cost: Rules are free, LLM costs compute
- Speed: Rules are 1000x faster
- Reliability: Rules never fail
- Accuracy: Rules are 90%+ when they match

**Trade-off:** Complexity (5 tiers) vs Performance (fast + accurate)

---

## Model Loading Strategy

### Startup Sequence

```python
# models.py __init__()

1. Initialize Llama classifier
   - Connects to Ollama at localhost:11434
   - Tests connection
   - If fails: Marks as unavailable (will use fallback)
   
2. Load Toxicity BERT
   - Downloads from HuggingFace if not cached
   - ~500MB model
   - Loads into memory
   
3. Load Sentiment BERT
   - Downloads from HuggingFace if not cached
   - ~500MB model
   - Loads into memory
   
4. Load Sentence Embedding model
   - Downloads from HuggingFace if not cached
   - ~100MB model
   - Computes embeddings for category templates
```

**Total startup time:** 10-15 seconds

**Why load at startup, not on-demand?**
- **Fail-fast:** If models can't load, we know immediately
- **Predictable latency:** First request isn't slow
- **Simpler code:** No lazy loading logic

**Trade-off:** Slower startup vs simpler code and predictable performance

---

## Error Handling Philosophy

### Fail-Fast vs Graceful Degradation

**Fail-Fast (Startup):**
```python
# If models can't load, crash immediately
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found")
```
**Why:** Better to not start than serve incorrect results.

**Graceful Degradation (Runtime):**
```python
# If Llama fails, try Gemini
# If Gemini fails, use local BERT
# Always return something
```
**Why:** User experience > perfect accuracy.

### Error Response Format

```json
{
  "success": false,
  "error": "Analysis failed: Ollama connection timeout"
}
```

**Why include error details?**
- Debugging: Frontend can log specific errors
- User feedback: Can show meaningful messages
- Monitoring: Can alert on specific failure types

---

## Configuration Management

### Environment Variables

```
GOOGLE_API_KEY - Gemini API key (optional, for fallback)
PORT - Server port (default: 50010)
```

**Why so few?**
- **Simplicity:** Less configuration = less to break
- **Sensible defaults:** Works out of the box
- **Explicit:** No hidden config files

**What's NOT configurable:**
- Model names (hardcoded for stability)
- Tier thresholds (tuned empirically)
- Ollama URL (standard localhost:11434)

**Trade-off:** Flexibility vs Simplicity

---

## Performance Characteristics

### Latency Breakdown

```
Request validation: <1ms
Tier 1-4 (rules): <1ms
Tier 5 (Llama): ~800ms
BERT toxicity: ~50ms
Response formatting: <1ms

Total (rule hit): ~50ms
Total (LLM hit): ~850ms
Average: ~500ms (60% rules, 40% LLM)
```

### Memory Usage

```
Flask app: ~50MB
Toxicity BERT: ~500MB
Sentiment BERT: ~500MB
Embedding model: ~100MB
Llama (Ollama): ~2GB (separate process)

Total: ~3.2GB
```

### Throughput

```
Single process: ~2 req/sec (LLM bottleneck)
With caching: ~20 req/sec (rules + cache hits)
```

**Scaling strategy:** 
- Horizontal: Run multiple Flask instances
- Vertical: Not effective (LLM is the bottleneck)
- Caching: Most effective (common phrases repeat)

---

## Testing Strategy

### What We Test

1. **Unit tests:** Individual tier logic
2. **Integration tests:** Full pipeline
3. **Accuracy tests:** Labeled Hinglish dataset

### What We Don't Test

1. **ML model internals:** Trust HuggingFace/Meta
2. **Ollama server:** External dependency
3. **Every edge case:** Diminishing returns

**Philosophy:** Test business logic, not libraries.

---

## Deployment Considerations

### Production Checklist

- [ ] Remove `debug=True` from Flask
- [ ] Use gunicorn/uwsgi instead of Flask dev server
- [ ] Set up monitoring (Prometheus + Grafana)
- [ ] Configure log aggregation
- [ ] Set up health check endpoint monitoring
- [ ] Restrict CORS to specific origins
- [ ] Use environment-specific .env files
- [ ] Set up model caching (avoid re-downloads)

### Resource Requirements

**Minimum:**
- 4GB RAM
- 2 CPU cores
- 10GB disk (for models)

**Recommended:**
- 8GB RAM (for multiple workers)
- 4 CPU cores
- 20GB disk (for logs + models)

---

## Future Architecture Changes

### Planned Improvements

1. **Redis caching layer**
   - Cache LLM responses for common phrases
   - Expected: 50% latency reduction

2. **Async processing**
   - Use Celery for batch jobs
   - Expected: 10x throughput for bulk analysis

3. **Model versioning**
   - Track which model version produced each result
   - Why: A/B testing and rollback capability

### Not Planned

- ❌ **Microservices:** Premature for current scale
- ❌ **Kubernetes:** Overkill for single service
- ❌ **GraphQL:** REST is sufficient

---

## Common Pitfalls

### For New Engineers

1. **Don't add business logic to app.py**
   - It's a transport layer only
   - All logic belongs in models.py or llama_classifier.py

2. **Don't bypass the tier system**
   - Tiers exist for performance
   - Going straight to LLM kills latency

3. **Don't hardcode thresholds**
   - Use constants at the top of files
   - Document why each threshold was chosen

4. **Don't silent-fail**
   - Log errors explicitly
   - Return error responses with context

---

## Questions & Answers

**Q: Why not use a single LLM for everything?**
A: Cost and latency. Rules handle 60% of cases in <1ms for free.

**Q: Why Flask instead of FastAPI?**
A: Simplicity. FastAPI's async benefits don't help (LLM is the bottleneck).

**Q: Why local models instead of OpenAI API?**
A: Privacy (devotional content is sensitive) and cost ($0 vs $100s/month).

**Q: Why 5 tiers? Isn't that complex?**
A: Each tier is simple. Complexity is in the coordination, which is explicit.

**Q: How do we improve accuracy?**
A: Fine-tune BERT on labeled Hinglish data. Current accuracy is limited by pre-trained models.

---

**This architecture prioritizes simplicity, explainability, and real-world performance over theoretical elegance.**
