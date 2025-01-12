from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from supabase import create_client, Client
from scripts import gemini_video_processing as gemini
import os
from postautomation.automate import FacebookSessionManager
import requests
import tempfile
# Load environment variables
load_dotenv()

url: str = os.environ.get("SUPABASE_PROJECT_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

# Initialize Flask app
app = Flask(__name__)
# Enable CORS with support for credentials
CORS(app, supports_credentials=True, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

@app.route('/api/post_to_facebook', methods=['POST'])
def post_to_facebook():
    try:
        data = request.get_json()
        items = data.get('items', [])
        print(f"[INFO] Received {len(items)} items")

        results = []
        session_manager = FacebookSessionManager()
        session_manager.init_driver()

        try:
            # Facebook login code
            if not session_manager.load_session():
                email = os.getenv("FB_EMAIL")
                password = os.getenv("FB_PASSWORD")
                if not session_manager.login(email, password):
                    raise Exception("Facebook login failed")

            for item in items:
                try:
                    # Image processing
                    temp_dir = tempfile.gettempdir()
                    image_url = item['image_url']
                    image_ext = os.path.splitext(image_url.split('?')[0])[1] or '.jpg'
                    temp_image_path = os.path.join(temp_dir, f"temp_image_{item['id']}{image_ext}")

                    response = requests.get(image_url)
                    with open(temp_image_path, 'wb') as f:
                        f.write(response.content)

                    success = session_manager.create_marketplace_listing(
                        title=item['title'],
                        price=int(item['price']),
                        image_path=temp_image_path,
                        category="Miscellaneous",
                        condition=item['condition'],
                        description=item['description']
                    )

                    os.remove(temp_image_path)

                    if success:
                        try:
                            # Update database status immediately after successful posting
                            supabase.table('items')\
                                    .update({'status': 'listed'})\
                                    .eq('id', item['id'])\
                                    .execute()
                            print(f"[INFO] Updated status to 'listed' for item: {item['id']}")
                        except Exception as db_error:
                            print(f"[ERROR] Failed to update status for item {item['id']}: {str(db_error)}")
                            success = False  # Mark as failed if database update fails

                    results.append({
                        "item_id": item['id'],
                        "title": item['title'],
                        "success": success,
                        "message": "Posted successfully" if success else "Failed to create listing"
                    })

                except Exception as item_error:
                    results.append({
                        "item_id": item['id'],
                        "title": item['title'],
                        "success": False,
                        "message": str(item_error)
                    })
                print(f"[INFO] Completed posting item: '{item['title']}' (ID: {item['id']})")

            return jsonify({
                "status": "success",
                "results": results,
                "message": f"Processed {len(items)} items"
            }), 200

        finally:
            session_manager.quit()

    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

@app.route('/api/process_video', methods=['POST'])
def process_video():
    try:
        data = request.get_json()
        video_url = data.get('video_url')
        
        if not video_url:
            return jsonify({"error": "No video URL provided"}), 400

        print("[DEBUG] Received video_url:", video_url)
            
        try:
            # Process the video using Gemini
            path_to_video_file = os.environ.get("PATH_TO_VIDEO_FILE") + video_url
            print(f"[INFO] Path to video file: {path_to_video_file}")

            result = gemini.main(path_to_video_file=path_to_video_file)
            print("[DEBUG] Gemini result:", result)
            
            # Convert any float prices to integers before returning
            if isinstance(result, list):
                for item in result:
                    if 'price' in item:
                        item['price'] = int(float(item['price']))
            
            return jsonify({
                "status": "success",
                "message": "Video processing completed",
                "data": result
            }), 200
            
        except Exception as e:
            print("[ERROR] Error in Gemini processing:", str(e))
            return jsonify({
                "status": "error",
                "message": f"Error in video processing: {str(e)}"
            }), 500
        
    except Exception as e:
        print("[ERROR] Error in route:", str(e))
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
