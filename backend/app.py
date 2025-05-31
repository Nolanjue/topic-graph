from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

@app.route("/submit", methods=["POST"])
def receive_data():
    data = request.get_json()
    chunks = data.get("chunks", [])
    similarities = data.get("similarities", [])
    topics = data.get("topics", [])

    return jsonify({
        "status": "received",
        "num_chunks": len(chunks),
        "sample_similarity": similarities[0][:3] if similarities else [],
        "topics": topics[:3]
    })

if __name__ == "__main__":
    app.run(debug=True, port=5001)
