from flask import Flask, request, jsonify, render_template
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
import string

nltk.download('punkt')

app = Flask(__name__)

faqs = {
    "What is your return policy?": "Our return policy allows returns within 30 days of purchase.",
    "How long does shipping take?": "Shipping usually takes 3-5 business days.",
    "Do you offer international shipping?": "Yes, we ship to most countries worldwide.",
    "How can I track my order?": "You can track your order using the tracking link sent to your email.",
    "What payment methods do you accept?": "We accept credit cards, debit cards, and PayPal."
}

questions = list(faqs.keys())
answers = list(faqs.values())

vectorizer = TfidfVectorizer()

def preprocess(text):
    tokens = nltk.word_tokenize(text.lower())
    tokens = [t for t in tokens if t not in string.punctuation]
    return " ".join(tokens)

processed_questions = [preprocess(q) for q in questions]
tfidf_matrix = vectorizer.fit_transform(processed_questions)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_question = request.json.get("message")
    processed = preprocess(user_question)
    user_vec = vectorizer.transform([processed])
    similarity = cosine_similarity(user_vec, tfidf_matrix)
    idx = similarity.argmax()
    best_match = answers[idx]
    return jsonify({"response": best_match})

if __name__ == "__main__":
    app.run(debug=True)
