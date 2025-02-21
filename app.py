from flask import Flask, request, render_template, send_file, jsonify
import os
from encode import hide_document_in_audio
from decode import extract_document_from_audio  # Import the fixed function
from utils import allowed_file, convert_to_wav
from models import db  # Import database

app = Flask(__name__)

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db.init_app(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/")
def index():
    """Home Page (Acts as both Index and Dashboard)"""
    return render_template("index.html")

@app.route("/encode", methods=["POST"])
def encode():
    """Encodes a document inside an audio file"""
    if "audio" not in request.files or "document" not in request.files:
        return jsonify({"error": "Missing files"}), 400

    audio = request.files["audio"]
    document = request.files["document"]

    if not allowed_file(audio.filename, {"wav", "mp3"}):
        return jsonify({"error": "Invalid audio file type"}), 400

    if not allowed_file(document.filename, {"docx", "xlsx", "pdf", "pptx", "txt"}):
        return jsonify({"error": "Invalid document file type"}), 400

    audio_path = os.path.join(app.config["UPLOAD_FOLDER"], audio.filename)
    doc_path = os.path.join(app.config["UPLOAD_FOLDER"], document.filename)
    encoded_audio_path = os.path.join(app.config["UPLOAD_FOLDER"], "encoded_audio.wav")

    audio.save(audio_path)
    document.save(doc_path)

    # Convert MP3 to WAV if needed
    audio_path = convert_to_wav(audio_path)

    key = "your_secret_key"  # You can change this to a dynamic key

    try:
        result = hide_document_in_audio(audio_path, doc_path, encoded_audio_path)
        if "Error" in result:
            return jsonify({"error": result}), 400

        return send_file(encoded_audio_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/decode", methods=["POST"])
def decode():
    """Decodes a hidden document from an audio file"""
    if "encoded_audio" not in request.files:
        return jsonify({"error": "No encoded audio file uploaded"}), 400

    encoded_audio = request.files["encoded_audio"]
    if encoded_audio.filename == "":
        return jsonify({"error": "No selected file"}), 400

    audio_path = os.path.join(app.config["UPLOAD_FOLDER"], encoded_audio.filename)
    encoded_audio.save(audio_path)

    key = "your_secret_key"  # Ensure the same key is used for encryption and decryption

    try:
        # Extract the document and get the correct filename
        status, extracted_doc_path = extract_document_from_audio(audio_path, app.config["UPLOAD_FOLDER"])

        if "Error" in status:
            return jsonify({"error": status}), 400

        # Send the extracted document with the correct filename
        return send_file(extracted_doc_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
