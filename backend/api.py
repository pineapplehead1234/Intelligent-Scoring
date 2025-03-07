from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import tempfile

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = tempfile.gettempdir()
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

transcriber = pipeline(task="automatic-speech-recognition", model="openai/whisper-tiny.en")
similarity_model = SentenceTransformer("all-MiniLM-L6-v2")

def speech2text(speech_file):
    text_dict = transcriber(speech_file, return_timestamps=True)
    return text_dict["text"]

def calculate_similarity(transcripts, standard_answer):
    sentences = transcripts + [standard_answer]
    embeddings = similarity_model.encode(sentences)
    standard_embedding = embeddings[-1]
    scores = []
    for i, embedding in enumerate(embeddings[:-1]):
        score = similarity_model.similarity([embedding], [standard_embedding])[0][0].item()
        rounded_score = round(score, 5)
        scores.append(rounded_score)
    return scores

@app.route("/api/process", methods=["POST"])
def process_files():
    if "files" not in request.files or "standard_answer" not in request.form:
        return jsonify({"error": "Missing files or standard answer"}), 400

    files = request.files.getlist("files")
    standard_answer = request.form["standard_answer"]

    transcripts = []
    for file in files:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        transcript = speech2text(filepath)
        transcripts.append(transcript)

    scores = calculate_similarity(transcripts, standard_answer)
    results = [{"filename": files[i].filename, "transcript": transcripts[i], "score": scores[i]} for i in range(len(files))]

    return jsonify(results)

@app.route("/")
def index():
    return send_from_directory("../frontend/src", "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory("../frontend/src", path)
if __name__ == "__main__":
    app.run(debug=True, port=5000)