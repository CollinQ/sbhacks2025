from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from supabase import create_client, Client
from scripts import gemini_video_processing as gemini
import os

# Load environment variables
load_dotenv()

url: str = os.environ.get("SUPABASE_PROJECT_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/process_video', methods=['POST'])
def process_video():
    try:
        data = request.get_json()
        video_url = data.get('video_url')
        
        if not video_url:
            return jsonify({"error": "No video URL provided"}), 400
            
        # Process the video using Gemini
        result = gemini.main()
        
        return jsonify({
            "status": "success",
            "message": "Video processing completed",
            "data": result
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/init', methods=['GET'])
def init():
    try:
        # First create auth user
        auth_response = supabase.auth.sign_up({
            "email": "bbobbqq@gmail.com",
            "password": "example-password"
        })
        
        # Get the user ID from auth response
        user_id = auth_response.user.id
        
        # Now insert into our users table with the auth user ID
        response = supabase.table("users").insert({
            "id": user_id,
            "email": "bbobbqq@gmail.com",
            "full_name": "Bob Qia"
        }).execute()
        
        return jsonify({"status": "success", "data": response.data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Server is running"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
