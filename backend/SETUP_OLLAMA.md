# Ollama Setup Guide

Quick installation guide for Llama 3.2 3B on Mac.

## Installation

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
```

## Download Model

```bash
# Download Llama 3.2 3B (2GB)
ollama pull llama3.2:3b
```

## Start Server

```bash
# Start Ollama (keep this terminal open)
ollama serve
```

Server runs at: `http://localhost:11434`

## Verify

```bash
# Test the installation
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:3b",
  "prompt": "Hello",
  "stream": false
}'
```

## Troubleshooting

### Port already in use
```bash
# Kill existing Ollama process
pkill ollama

# Restart
ollama serve
```

### Model not found
```bash
# List installed models
ollama list

# Re-download if needed
ollama pull llama3.2:3b
```

### Slow responses
- First request loads the model (~2-3 seconds)
- Subsequent requests are faster (<1 second)

---

**That's it!** Ollama is ready for the Krishna AI backend.
