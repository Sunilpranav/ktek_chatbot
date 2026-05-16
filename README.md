# 🤖 K TEK Chatbot

An AI-powered chatbot for **K TEK Computer Center** with two modes — a **Flask web app** and an **offline console chatbot**. It uses semantic search over a custom FAQ knowledge base for instant answers, and falls back to a locally-running **LLaMA 3** model via Ollama for general queries.

---

## 📌 About the Project

The K TEK Chatbot provides an intelligent conversational assistant for K TEK Computer Center students and visitors. It combines:

- **Semantic FAQ retrieval** using `sentence-transformers` + `FAISS` for fast, accurate answers about K TEK courses, fees, and contact details.
- **LLaMA 3 via Ollama** as a local LLM fallback for questions outside the FAQ scope — no cloud API needed.
- **Two interfaces:** a Flask web app with a browser UI, and a feature-rich console chatbot with voice support.

---

## ✨ Features

### Both Modes
- 🔍 **Semantic Search** — Uses `all-MiniLM-L6-v2` embeddings + FAISS vector index for context-aware FAQ matching
- 🧠 **LLaMA 3 Fallback** — Routes unanswered questions to a locally-running Ollama model
- 📚 **Rich FAQ Knowledge Base** — Covers K TEK courses, fees, contact info, programming topics, and general computer science (`ktek.json`)
- ⚡ **Similarity Threshold** — FAQ answers are only used when confidence score is ≥ 0.60, ensuring accuracy

### Web App (`app.py`)
- 🌐 **Browser Interface** — Flask-powered web UI served via `index.html`
- 📡 **REST API** — `/ask` endpoint accepts POST requests and returns JSON responses
- 🏷️ **Source Labelling** — Responses from the FAQ are labelled `(From K Tek FAQ)` for transparency

### Console Chatbot (`ktek_ollama_chatbot.py`)
- 🗣️ **Voice Output** — Optional text-to-speech via `pyttsx3` (toggle on/off with `/voice`)
- ➕ **Live FAQ Management** — Add new Q&A pairs at runtime with `/faqadd` and persist them with `/faqsave`
- 🎨 **Friendly Responses** — Random friendly openers for a warm conversational feel
- ⌨️ **Console Commands:**

| Command | Action |
|---------|--------|
| `/voice` | Toggle voice output on/off |
| `/faqadd` | Add a new FAQ entry at runtime |
| `/faqsave` | Save all FAQs to `ktek.json` |
| `/clear` | Clear the terminal screen |
| `/exit` | Exit the chatbot |

---

## 🗂️ Project Structure

```
ktek_chatbot/
├── app.py                   # Flask web app (browser-based chatbot)
├── ktek_ollama_chatbot.py   # Full-featured console chatbot with voice
├── ktek.json                # FAQ knowledge base (questions & answers)
└── index.html               # Web UI for the Flask app
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Web Backend | Python, Flask |
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`) |
| Vector Search | FAISS (`IndexFlatIP`) |
| Local LLM | Ollama + LLaMA 3 (`llama3`) |
| Voice Output | `pyttsx3` |
| Frontend | HTML, CSS, JavaScript |
| Data Store | JSON (`ktek.json`) |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai) installed locally
- LLaMA 3 model pulled via Ollama

### 1. Install Ollama & Pull LLaMA 3

```bash
# Install Ollama from https://ollama.ai
ollama pull llama3
```

### 2. Clone the Repository

```bash
git clone https://github.com/Sunilpranav/ktek_chatbot.git
cd ktek_chatbot
```

### 3. Create a Virtual Environment & Install Dependencies

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

pip install flask sentence-transformers faiss-cpu numpy pyttsx3
```

### 4A. Run the Web App

```bash
python app.py
```

Then open your browser at `http://localhost:5000`

### 4B. Run the Console Chatbot

```bash
python ktek_ollama_chatbot.py
```

---

## 📐 How It Works

```
User sends a question
        ↓
Encode query with sentence-transformers
        ↓
Search FAISS index (similarity ≥ 0.60?)
       ↙           ↘
     YES              NO
      ↓                ↓
Return FAQ answer   Build prompt with context
(labelled as FAQ)   → Send to Ollama (LLaMA 3)
                        ↓
                   Return LLM response
```

---

## 📖 FAQ Knowledge Base

The `ktek.json` file includes Q&A pairs covering:

- K TEK location, contact, courses, fees, and certificates
- Programming languages — Python, Java, HTML, CSS, SQL
- Computer science concepts — OS, networking, databases, cloud
- General knowledge — AI, internet, hardware, data structures
- Local context — Erode district, Kodumudi, Tamil Nadu

New entries can be added at runtime via `/faqadd` in the console, or by editing `ktek.json` directly.

---

## 🔮 Future Enhancements

- 🌍 Multi-language support (Tamil + English)
- 📱 WhatsApp / Telegram bot integration
- 🗃️ Persistent chat history
- 🔄 Auto-refresh FAQ embeddings on file update
- 🎨 Enhanced web UI with chat history and typing indicators

---

## 👨‍💻 Developer

Developed by **Sunilpranav**

- GitHub: [@Sunilpranav](https://github.com/Sunilpranav)
- K TEK Website: [k-tek.netlify.app](https://k-tek.netlify.app)
- Contact: kteckcsckmd@gmail.com | +91 88707 70486

---

## 📄 License

This project is open source and available for educational and personal use.
