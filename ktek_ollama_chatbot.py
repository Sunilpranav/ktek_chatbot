# ktek_ollama_chatbot.py
"""
Offline/Locally-backed friendly chatbot using:
 - Ollama local model for general questions
 - sentence-transformers + FAISS for K Tek FAQ retrieval
 - pyttsx3 for optional voice output (toggle with /voice)
 - Console UI with commands: /voice, /faqadd, /faqsave, /clear, /exit
"""

import json, random, threading, subprocess, shutil, os
from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

# ----------------------  VOICE SETUP  ----------------------
try:
    import pyttsx3
    tts_engine = pyttsx3.init()
    TTS_AVAILABLE = True
except Exception:
    TTS_AVAILABLE = False
    tts_engine = None

def speak_async(text):
    if not TTS_AVAILABLE:
        return
    def _speak(t):
        try:
            tts_engine.say(t)
            tts_engine.runAndWait()
        except RuntimeError:
            pass
    threading.Thread(target=_speak, args=(text,), daemon=True).start()

# ----------------------  CONFIG  ----------------------
OLLAMA_MODEL = "llama3"     # or "mistral", "phi", etc.
FAQ_PATH = Path("ktek.json")
RETRIEVAL_THRESHOLD = 0.60
OLLAMA_TIMEOUT = 60

# ----------------------  FAQ SETUP  ----------------------
if FAQ_PATH.exists():
    with open(FAQ_PATH, "r", encoding="utf-8") as f:
        raw_faqs = json.load(f)
else:
    raw_faqs = [
    # ---------- K TEK COMPUTER CENTER ----------
    {
        "question": "what is k tek computer center",
        "answer": "K TEK Computer Center is a professional computer training institute in Kodumudi, Erode district, Tamil Nadu. It offers practical computer education, programming courses, and IT services for students and professionals."
    },
    {
        "question": "where is k tek located",
        "answer": "K TEK Computer Center is located near Railway Station Road, Kodumudi, Erode district, Tamil Nadu, India."
    },
    {
        "question": "how to contact k tek",
        "answer": "You can contact K TEK by phone at +91 88707 70486, or by email at kteckcsckmd@gmail.com. Website: https://k-tek.netlify.app/."
    },
    {
        "question": "what courses are offered in k tek",
        "answer": "K TEK offers C, C++, Java, Python, HTML, CSS, MS Office, DCA, COA, Tally, and web development training."
    },
    {
        "question": "what is the course fee in k tek",
        "answer": "Course fees usually start at ₹2000 for short-term programs, depending on the duration and specialization."
    },
    {
        "question": "does k tek provide certificates",
        "answer": "Yes, K TEK provides a valid course completion certificate after successful training."
    },
    {
        "question": "what is special about k tek",
        "answer": "K TEK focuses on practical, project-based learning and offers individual attention to each student."
    },

    # ---------- EDUCATIONAL GENERAL ----------
    {
        "question": "what is a computer",
        "answer": "A computer is an electronic device that processes data according to instructions. It performs input, processing, output, and storage operations."
    },
    {
        "question": "what is programming",
        "answer": "Programming is the process of writing instructions (code) that a computer can understand to perform specific tasks."
    },
    {
        "question": "what is java programming",
        "answer": "Java is a high-level, object-oriented programming language developed by Sun Microsystems. It is platform-independent and widely used for web, mobile, and enterprise applications."
    },
    {
        "question": "what is python",
        "answer": "Python is a high-level, interpreted programming language known for its simplicity and readability. It’s used in data science, AI, web development, and automation."
    },
    {
        "question": "what is html",
        "answer": "HTML (HyperText Markup Language) is the standard language for creating web pages and web applications."
    },
    {
        "question": "what is css",
        "answer": "CSS (Cascading Style Sheets) defines the style and layout of web pages — colors, fonts, spacing, etc."
    },
    {
        "question": "what is artificial intelligence",
        "answer": "Artificial Intelligence (AI) is the simulation of human intelligence by computers — including learning, reasoning, and problem-solving."
    },
    {
        "question": "what is machine learning",
        "answer": "Machine Learning is a branch of AI where computers learn from data and improve their performance without being explicitly programmed."
    },
    {
        "question": "what is an operating system",
        "answer": "An operating system (OS) is system software that manages hardware, software resources, and provides services for computer programs. Examples: Windows, Linux, macOS."
    },

    # ---------- SCIENCE & GENERAL KNOWLEDGE ----------
    {
        "question": "what is a tree",
        "answer": "A tree is a perennial plant with a long trunk, branches, and leaves. Trees produce oxygen and are vital for the environment."
    },
    {
        "question": "tell me about erode district",
        "answer": "Erode is a district in Tamil Nadu, India, known for its textile industries, turmeric production, and agriculture. The Kaveri River flows through it."
    },
    {
        "question": "who is the father of computer",
        "answer": "Charles Babbage is known as the Father of the Computer for designing the Analytical Engine in the 1830s."
    },
    {
        "question": "what is internet",
        "answer": "The Internet is a global network of interconnected computers that share information and communication services worldwide."
    },
    {
        "question": "what is the solar system",
        "answer": "The Solar System consists of the Sun and all celestial objects bound to it by gravity — including planets, moons, asteroids, and comets."
    },
    {
        "question": "what is electricity",
        "answer": "Electricity is the flow of electric charge, typically through conductors like copper wire, used to power devices and machines."
    },
    {
        "question": "what is water",
        "answer": "Water is a chemical substance composed of hydrogen and oxygen (H₂O). It’s essential for all known forms of life."
    },

    # ---------- ADDITIONAL EDUCATIONAL ----------
    {
        "question": "what is data structure",
        "answer": "A data structure is a way of organizing and storing data efficiently in a computer so it can be used effectively. Examples: arrays, linked lists, stacks, queues."
    },
    {
        "question": "what is a database",
        "answer": "A database is an organized collection of structured information stored electronically, usually managed by a Database Management System (DBMS)."
    },
    {
        "question": "what is sql",
        "answer": "SQL (Structured Query Language) is used to manage and manipulate relational databases. It allows creating, reading, updating, and deleting data."
    },
    {
        "question": "what is web development",
        "answer": "Web development is the process of building websites and web applications using technologies like HTML, CSS, JavaScript, and frameworks."
    },
    {
        "question": "what is cloud computing",
        "answer": "Cloud computing delivers computing services — like servers, storage, and databases — over the Internet instead of local hardware."
    },
    {
        "question": "what is cybersecurity",
        "answer": "Cybersecurity involves protecting systems, networks, and data from digital attacks and unauthorized access."
    },
    {
        "question": "what is networking",
        "answer": "Networking is the process of connecting computers and devices to share resources and data. Examples include LAN, WAN, and the Internet."
    },
    {
        "question": "what is ms office",
        "answer": "Microsoft Office is a suite of productivity software including Word, Excel, PowerPoint, and Outlook, used for office work and document management."
    },
    {
        "question": "what is tally",
        "answer": "Tally is accounting software used for financial management, GST, and payroll processing in businesses."
    },
    {
        "question": "what is dca course",
        "answer": "DCA stands for Diploma in Computer Applications. It covers basics like MS Office, Internet, and programming fundamentals."
    },
    {
        "question": "what is coa course",
        "answer": "COA stands for Certificate in Office Automation. It teaches typing, document preparation, Excel, and PowerPoint."
    },
    {
        "question": "what is coding",
        "answer": "Coding is the process of converting ideas or logic into instructions that a computer can execute."
    }
]

    with open(FAQ_PATH, "w", encoding="utf-8") as f:
        json.dump(raw_faqs, f, indent=2, ensure_ascii=False)

FAQS = [(item["question"].strip(), item["answer"].strip()) for item in raw_faqs]

# ----------------------  BUILD EMBEDDINGS  ----------------------
print("Loading sentence-transformers model... (please wait)")
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

questions = [q for q, _ in FAQS]
answers = [a for _, a in FAQS]
q_emb = embed_model.encode(questions, convert_to_numpy=True, normalize_embeddings=True)
dim = q_emb.shape[1]
index = faiss.IndexFlatIP(dim)
index.add(q_emb)

# ----------------------  OLLAMA CHECK  ----------------------
def check_ollama():
    return shutil.which("ollama") is not None

OLLAMA_AVAILABLE = check_ollama()
if OLLAMA_AVAILABLE:
    print(f"Ollama ready ✅ using model: {OLLAMA_MODEL}")
else:
    print("⚠️ Ollama not found — install from https://ollama.ai and pull a model with `ollama pull llama3`")

# ----------------------  FUNCTIONS  ----------------------
def retrieve_faq(query):
    qv = embed_model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    D, I = index.search(qv, 1)
    score = float(D[0][0])
    idx = int(I[0][0])
    return (answers[idx], score) if score >= 0 else (None, 0.0)

def call_ollama(prompt):
    if not OLLAMA_AVAILABLE:
        return "(Ollama not installed locally.)"
    cmd = ["ollama", "run", OLLAMA_MODEL]
    try:
        proc = subprocess.run(cmd, input=prompt.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=OLLAMA_TIMEOUT)
        if proc.returncode != 0:
            return f"(Ollama error) {proc.stderr.decode()}"
        return proc.stdout.decode().strip()
    except Exception as e:
        return f"(Error calling Ollama: {e})"

def craft_prompt(question, context=None):
    sysmsg = (
        "You are a friendly and knowledgeable assistant. "
        "If the user's question is about K TEK Computer Center, use the provided FAQ context accurately. "
        "Otherwise, answer with general knowledge. Be concise, friendly, and clear."
    )
    prompt = f"System: {sysmsg}\n"
    if context:
        prompt += f"\nK-TEK-INFO:\n{context}\n"
    prompt += f"\nUser: {question}\nAssistant:"
    return prompt

FRIENDLY_OPENERS = ["Sure! 😊", "Got it 😎", "Absolutely — here's that:", "Happy to help!"]

def friendly_prefix(text):
    return f"{random.choice(FRIENDLY_OPENERS)} {text}"

# ----------------------  MAIN LOOP  ----------------------
VOICE_ON = TTS_AVAILABLE
welcome = "Hi! I'm your K TEK Assistant — ask me anything about our courses or any general question!"
print(friendly_prefix(welcome))
if VOICE_ON: speak_async(welcome)

print("\nCommands: /voice (toggle), /faqadd, /faqsave, /clear, /exit\n")

try:
    while True:
        user = input("You > ").strip()
        if not user:
            continue

        cmd = user.lower()
        if cmd in ("/exit", "/quit"):
            bye = "Goodbye! 👋"
            print("Bot >", bye)
            if VOICE_ON: speak_async(bye)
            break
        elif cmd == "/voice":
            VOICE_ON = not VOICE_ON
            print("Bot >", f"Voice mode {'ON' if VOICE_ON else 'OFF'}")
            if VOICE_ON: speak_async("Voice turned on")
            continue
        elif cmd == "/clear":
            os.system('cls' if os.name == 'nt' else 'clear')
            continue
        elif cmd == "/faqadd":
            q = input("New FAQ question: ").strip()
            a = input("New FAQ answer: ").strip()
            if q and a:
                FAQS.append((q, a))
                vec = embed_model.encode([q], convert_to_numpy=True, normalize_embeddings=True)
                index.add(vec)
                print("Bot > FAQ added.")
            continue
        elif cmd == "/faqsave":
            with open(FAQ_PATH, "w", encoding="utf-8") as f:
                json.dump([{"question": q, "answer": a} for q, a in FAQS], f, indent=2, ensure_ascii=False)
            print(f"Bot > Saved {len(FAQS)} FAQs.")
            continue

        # Try FAQ
        faq_answer, score = retrieve_faq(user)
        if faq_answer and score >= RETRIEVAL_THRESHOLD:
            reply = friendly_prefix(faq_answer + "  (From K Tek FAQ)")
            print("Bot >", reply)
            if VOICE_ON: speak_async(reply)
            continue

        # Otherwise, ask Ollama
        context = faq_answer if faq_answer and score > 0.3 else None
        prompt = craft_prompt(user, context)
        print("Bot > (thinking... using Ollama locally)")
        llm_reply = call_ollama(prompt)
        reply = friendly_prefix(llm_reply)
        print("Bot >", reply)
        if VOICE_ON: speak_async(reply)

except KeyboardInterrupt:
    print("\nBot > Bye 👋")
