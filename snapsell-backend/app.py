from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Server is running"}), 200

@app.route('/api/test', methods=['GET'])
def test_route():
    return jsonify({"message": "Hello from SnapSell Backend!"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
