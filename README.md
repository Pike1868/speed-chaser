# Speed Chaser

**Speed Chaser** is a lightweight, local-first AI assistant designed for developers, engineers, and technical users. It uses semantic search (FAISS + embeddings) and OpenRouter to power a self-referencing, context-aware CLI chatbot.

## 🚀 Features

- ✅ Local document ingestion (PDFs, code, Markdown, plain text)
- ✅ Fast semantic search with FAISS and Sentence Transformers
- ✅ GPU acceleration support for fast embeddings
- ✅ Guided conversational mode with auto-context injection
- ✅ Flexible configuration via `.env`
- ✅ Self-awareness — ask it about its own code and behavior!
- ✅ Easily extensible and Open Source friendly

## 📦 Setup

1. Clone the repo:

```bash
git clone https://github.com/yourname/speed-chaser.git
cd speed-chaser
```

2. Create a virtual environment:

```bash
python3 -m venv env
source env/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on the provided example:

```bash
cp .env.example .env
```

Set your OpenRouter API key inside `.env`:

```env
OPENROUTER_API_KEY=your-key-here
```

## 🧠 Usage

### Ingest project files

```bash
python app.py --ingest --path .
```

This creates a local vector index of all files (PDF, `.py`, `.md`, `.txt`, etc.)

### Start interactive chat

```bash
python app.py --guided
```

Now every user input will be enhanced with relevant local context from your project files.

### Ask questions

```text
You: What's in config.py?
You: Are you using my GPU?
You: Can you generate documentation for ingest.py?
```

## ⚙️ Configuration

See `config.py` for defaults. You can also define context modes:

```python
CONTEXTS = {
    "self-reference": {
        "folder": ".",
        "prompt": "You're reading your own codebase and explaining how it works."
    },
    "demo": {
        "folder": "refs/demo",
        "prompt": "You're demoing Speed Chaser for a fictional support company."
    }
}
```

## 💡 GPU Support

Speed Chaser uses `torch.cuda.is_available()` to detect GPU usage.

You can configure it with `.env`:

```env
EMBEDDING_DEVICE=auto  # or "cuda" or "cpu"
```

## 🛡️ Security Tip

Don't commit your `.env` or any sensitive documents in `refs/`.

## 📁 Recommended .gitignore

```
.env
vectorstore/
__pycache__/
*.pyc
*.pkl
.idea/
.vscode/
refs/TestDocument.pdf
```

## 🪪 License

This project is licensed under the MIT License.


## Project Structure
```
speed-chaser/
├── adapters/              # Optional integrations (e.g., linear, github, etc)
│   └── README.md
├── docs/                  # Auto-generated or user-added documentation
├── refs/                  # Reference files to be ingested (PDFs, code, etc.)
├── utils/
│   └── pdf_parser.py      # PDF parsing utility using PyMuPDF
├── vectorstore/           # FAISS index + metadata (auto-generated)
├── app.py                 # Main CLI entry point
├── config.py              # Configuration settings and context definitions
├── retriever.py           # Handles semantic search with FAISS
├── ingest.py              # Chunks and embeds files into vectorstore
├── requirements.txt       # Python package dependencies
├── .env.example           # Example environment configuration
├── .gitignore             # Files/folders excluded from version control
└── README.md              

```