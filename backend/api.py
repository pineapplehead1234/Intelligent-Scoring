from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
import torch
import numpy as np

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"   # os.environ 是一个字典，用于访问和修改环境变量。
os.environ["CUDA_VISIBLE_DEVICES"] = "0"              # 可以使用 os.environ["KEY"] 来获取环境变量的值，
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"             # 也可以使用 os.environ["KEY"] = "VALUE" 来设置环境变量的值。
                                                      # OneDNN 加速 TensorFlow 在英特尔 CPU 上的计算的功能被禁用
# 创建线程池
pool = ThreadPoolExecutor(max_workers=5)

app = Flask(__name__)
CORS(app)  # Cross-Origin Resource Sharing，简称 CORS，是一种机制，
# 它使用额外的 HTTP 头来告诉浏览器 让运行在一个 origin (domain) 上的 Web 应用被准许访问来自不同源服务器上的指定资源。
# 当一个跨源 HTTP 请求，例如从一个域名的网页上发起的请求，
# 这个请求的响应将会包含一些 CORS 相关的头信息，
# 浏览器会根据这些头信息来决定是否允许这个请求。

UPLOAD_FOLDER = tempfile.gettempdir()
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# 检查是否有可用的 CUDA 设备，如有则返回 0 并且使用 GPU，否则使用 CPU
device = 0 if torch.cuda.is_available() else -1

transcriber = pipeline(task="automatic-speech-recognition", model="openai/whisper-tiny.en")
similarity_model = SentenceTransformer("all-MiniLM-L6-v2")

def speech2text(speech_file):
    # 调用 transcriber 函数处理语音文件，并返回包含时间戳信息的字典
    text_dict = transcriber(speech_file, return_timestamps=True)
    # 从返回的字典中提取文本内容并返回
    return text_dict["text"]

def calculate_similarity(transcripts, standard_answer):
    sentences = transcripts + [standard_answer]
    embeddings = similarity_model.encode(sentences)
    standard_embedding = embeddings[-1]
    scores = []
    # 将 embeddings 转换为 numpy 数组
    # 将 standard_embedding 转换为 numpy 数组
    # 使用 torch.cosine_similarity 计算余弦相似度
    # 由于 torch.tensor() 只能接受单个 numpy.ndarray 作为输入，不能接受列表，
    # 故 numpy.ndarray 列表创建 torch.tensor 速度极慢 ，
    # 先使用 numpy.array() 把列表转换为单个 numpy.ndarray ，再转换为 torch.tensor
    embeddings_np = np.array(embeddings)
    standard_embedding_np = np.array(standard_embedding)
    for i, embedding in enumerate(embeddings_np[:-1]):
        score = torch.cosine_similarity(torch.tensor([embedding]), torch.tensor([standard_embedding_np]))[0].item()
        rounded_score = round(score, 5)
        scores.append(rounded_score)
    return scores

@app.route("/api/process", methods=["POST"])
def process_files():
    if "files" not in request.files or "standard_answer" not in request.form:
        return jsonify({"error": "Missing files or standard answer"}), 400

    files = request.files.getlist("files")
    standard_answer = request.form["standard_answer"]

    # 先保存所有文件
    file_paths = []
    file_names = []
    for file in files:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        file_paths.append(filepath)
        file_names.append(file.filename)

    # 并行处理语音转文本
    transcript_futures = [pool.submit(speech2text, filepath) for filepath in file_paths]
    transcripts = [future.result() for future in as_completed(transcript_futures)]
    
    # 计算相似度
    scores = calculate_similarity(transcripts, standard_answer)
    
    # 组织结果
    results = [{"filename": file_names[i], "transcript": transcripts[i], "score": scores[i]} 
               for i in range(len(file_names))]

    return jsonify(results)

@app.route("/")
def index():
    return send_from_directory("../frontend/src", "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory("../frontend/src", path)

if __name__ == "__main__":
    app.run(debug=True, port=5000)