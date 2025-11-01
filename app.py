from flask import Flask, render_template, request, jsonify
import subprocess, json
from sentence_transformers import SentenceTransformer
import faiss, numpy as np

app = Flask(__name__)

# Load FAQ and model
with open("ktek.json", "r", encoding="utf-8") as f:
    faqs = json.load(f)
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
questions = [f["question"] for f in faqs]
answers = [f["answer"] for f in faqs]
q_emb = embed_model.encode(questions, convert_to_numpy=True, normalize_embeddings=True)
index = faiss.IndexFlatIP(q_emb.shape[1])
index.add(q_emb)

def retrieve_faq(query):
    qv = embed_model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    D, I = index.search(qv, 1)
    if D[0][0] >= 0.6:
        return answers[int(I[0][0])]
    return None

def call_ollama(prompt):
    cmd = ["ollama", "run", "llama3"]
    try:
        result = subprocess.run(cmd, input=prompt.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        return result.stdout.decode().strip()
    except Exception as e:
        return f"(Error calling Ollama: {e})"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_input = data.get("message", "")
    faq_ans = retrieve_faq(user_input)
    if faq_ans:
        return jsonify({"response": faq_ans + " (From K Tek FAQ)"})
    llm_reply = call_ollama(user_input)
    return jsonify({"response": llm_reply})

if __name__ == "__main__":
    app.run(debug=True)
