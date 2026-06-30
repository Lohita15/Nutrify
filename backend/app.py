from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
from werkzeug.utils import secure_filename
import pandas as pd
import traceback
import math

# --- YOLO IMPORTS ---
from ultralytics import YOLO
from PIL import Image

# Get the project root directory
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend')

# Add backend to path for imports
sys.path.insert(0, BACKEND_DIR)
try:
    from nutrify_utils.preprocessing import ResultFormatter
except ImportError:
    # Dummy class in case nutrify_utils is missing during testing
    class ResultFormatter:
        @staticmethod
        def format_error(msg): return {"success": False, "error": msg}

# Initialize Flask app
app = Flask(__name__, 
            static_folder=os.path.join(FRONTEND_DIR, 'css'),
            static_url_path='/css',
            template_folder=FRONTEND_DIR)
CORS(app)

# Configuration
UPLOAD_FOLDER = os.path.join(BACKEND_DIR, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Global variables for YOLO Model and Data
yolo_model = None
container_model = None
calorie_dict = {}
grams_dict={}
last_result = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def initialize_yolo_model():
    """Initialize the YOLO Segmentation model and Load Calories database"""
    global yolo_model, calorie_dict
    try:
        print("\n" + "="*60)
        print("🔄 Initializing YOLO Instance Segmentation Model...")
        print("="*60)
        
       # 1. Load Calories Database (Bulletproof CSV/XLSX Loader)
        calories_dir = os.path.join(BACKEND_DIR, 'model', 'calories')
        csv_path = os.path.join(calories_dir, 'calories.csv')
        xlsx_path = os.path.join(calories_dir, 'calories.xlsx')
        
        try:
            # Try to load CSV first, if not, try Excel
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                print("✓ Found calories.csv!")
            else:
                df = pd.read_excel(xlsx_path)
                print("✓ Found calories.xlsx!")
                
            # Create a clean dictionary mapping food names to calories
            # .strip() removes accidental spaces at the end of the Excel cells!
            names = df.iloc[:, 0].astype(str).str.lower().str.strip().str.replace(' ', '_')
            cals = df.iloc[:, 1]
            grams = df.iloc[:, 2]

            global calorie_dict, grams_dict
            calorie_dict = dict(zip(names, cals))
            grams_dict = dict(zip(names, grams))
            
            print(f"✓ Calories & Weights database loaded! ({len(calorie_dict)} food items ready)")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not load calories file. Error: {e}")
            print("⚠️ Make sure your file is in backend/model/calories/ and you ran 'pip install openpyxl'")
            calorie_dict = {}

       
        # 2. Load BOTH YOLO Models
        food_model_path = os.path.join(BACKEND_DIR, 'model', 'classifier', 'best.pt')
        container_path = os.path.join(BACKEND_DIR, 'model', 'classifier', 'containers.pt')
        
        global food_model, container_model
        food_model = YOLO(food_model_path)
        container_model = YOLO(container_path)

        print(f"✓ BOTH YOLO Models loaded successfully!")
        print("="*60 + "\n")
        return True
            
    except Exception as e:
        print(f"❌ Error initializing YOLO model: {e}")
        return False

# ==================== ROUTES ====================

@app.route('/')
def index():
    html_file = os.path.join(FRONTEND_DIR, 'index.html')
    with open(html_file, 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/upload')
def upload_page():
    html_file = os.path.join(FRONTEND_DIR, 'upload.html')
    with open(html_file, 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/results')
def results_page():
    html_file = os.path.join(FRONTEND_DIR, 'results.html')
    with open(html_file, 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/css/<path:filename>')
def serve_css(filename):
    css_dir = os.path.join(FRONTEND_DIR, 'css')
    return send_from_directory(css_dir, filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    js_dir = os.path.join(FRONTEND_DIR, 'js')
    return send_from_directory(js_dir, filename)

@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ==================== API ENDPOINTS ====================

@app.route('/api/upload_meal', methods=['POST'])
def upload_meal():
    global last_result
    
    try:
        if 'image' not in request.files:
            return jsonify(ResultFormatter.format_error("No image provided")), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify(ResultFormatter.format_error("No image selected")), 400
        
        if not allowed_file(file.filename):
            return jsonify(ResultFormatter.format_error("Invalid file type.")), 400
        
        # Save original file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        if food_model is None or container_model is None:
            return jsonify(ResultFormatter.format_error("Models are not loaded on the server.")), 500
        
        # --- TWO-BRAIN INFERENCE LOGIC ---
        print(f"🔍 Running Dual-YOLO inference on {filename}...")
        try:
            food_results = food_model.predict(source=file_path, conf=0.15, iou=0.7)
            container_results = container_model.predict(source=file_path, conf=0.5)
            
            food_result = food_results[0]
            container_result = container_results[0]
            
            if len(food_result.boxes) == 0:
                return jsonify(ResultFormatter.format_error("No food detected in the image.")), 400

            # 1. EXTRACT CONTAINERS
            containers = []
            if len(container_result.boxes) > 0:
                for box in container_result.boxes:
                    coords = box.xyxy[0].tolist() 
                    class_id = int(box.cls[0].item())
                    container_name = container_result.names[class_id].lower() # 'bowl' or 'plate'
                    containers.append({"type": container_name, "box": coords})

            # 2. MATCH FOOD TO CONTAINERS
            food_summary = {} # Will store like: {"Biryani (bowl)": {"name": "Biryani", "count": 1, "container": "bowl"}}
            names_dict = food_result.names 

            for food_box in food_result.boxes:
                class_id = int(food_box.cls[0].item())
                raw_name = names_dict[class_id]
                display_name = raw_name.replace('_', ' ').title()
                
                # Find the dead-center of the food
                f_coords = food_box.xyxy[0].tolist()
                center_x = (f_coords[0] + f_coords[2]) / 2
                center_y = (f_coords[1] + f_coords[3]) / 2
                
                served_in = "plate" # Default assumption
                
                # Check if center is inside a bowl/plate
                for container in containers:
                    c_xmin, c_ymin, c_xmax, c_ymax = container["box"]
                    if (c_xmin <= center_x <= c_xmax) and (c_ymin <= center_y <= c_ymax):
                        served_in = container["type"]
                        break
                
                # Group foods that share a name AND a container
                summary_key = f"{display_name}_{served_in}"
                if summary_key in food_summary:
                    food_summary[summary_key]['count'] += 1
                else:
                    food_summary[summary_key] = {'name': display_name, 'container': served_in, 'count': 1}

            
           
            # 3. APPLY SMART PORTION MATH
            # 3. APPLY SMART PORTION MATH
            detailed_foods = []
            display_strings = [] 
            total_calories = 0
            
            for key, data in food_summary.items():
                name = data['name']
                count = data['count']
                container = data['container']
                
                raw_name_key = name.lower().replace(' ', '_')
                
                # Fetch BOTH values from our Excel dictionaries!
                base_cal = calorie_dict.get(raw_name_key, 250) 
                base_grams = grams_dict.get(raw_name_key, 100) # Defaults to 100g if missing
                
                # The Contextual Multiplier!
                if container == "bowl":
                    adjusted_base_cal = int(base_cal * 1.5)
                    grams_per_unit = int(base_grams * 1.5) # Scale the Excel weight by 1.5x
                    unit_label = "Katori"
                else:
                    adjusted_base_cal = int(base_cal)
                    grams_per_unit = int(base_grams) # Use the exact Excel weight!
                    unit_label = "Portion"
                
                item_total_cals = adjusted_base_cal * count
                total_calories += item_total_cals
                
                # Package it for the frontend
                detailed_foods.append({
                    "name": name,
                    "count": count,
                    "container": container,
                    "base_calories": adjusted_base_cal,
                    "grams_per_unit": grams_per_unit 
                })
                
                display_strings.append(f"{name} ({count} {unit_label})")
            
            print(f"✓ Packaged Data: {display_strings} | Initial Total: {total_calories} kcal")
            
            # --- MAKE SURE THIS IS INTACT! ---
            if total_calories > 800:
                recommendation = "High calorie meal. Consider portion control! ⚠️"
            elif total_calories < 300:
                recommendation = "Light snack. Good for a quick energy boost! ⚡"
            else:
                recommendation = "Balanced portion. Perfect for a healthy meal! 🥗"
            
            # Save the result
            last_result = {
                "food_items": display_strings, 
                "detailed_foods": detailed_foods, 
                "total_calories": total_calories,
                "recommendation": recommendation,
                "filename": filename
            }
            
            return jsonify({
                "success": True,
                "food_items": display_strings, 
                "detailed_foods": detailed_foods, 
                "total_calories": total_calories,
                "recommendation": recommendation,
                "filename": filename
            }), 200
            
        except Exception as e:
           print("❌ Inference error:")
           traceback.print_exc()
           return jsonify(ResultFormatter.format_error(f"Could not analyze meal: {str(e)}")), 500
            
    

@app.route('/api/meal_analysis_result', methods=['GET'])
def get_meal_result():
    global last_result
    
    if last_result:
        return jsonify({
            "success": True,
            "data": last_result
        }), 200
    else:
        return jsonify({
            "success": False,
            "error": "No analysis result available",
            "data": None
        }), 404

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "model_loaded": yolo_model is not None,
        "service": "NutriFy API"
    }), 200

@app.route('/<path:filename>')
def serve_html(filename):
    try:
        if filename.endswith('.html'):
            html_file = os.path.join(FRONTEND_DIR, filename)
            if os.path.exists(html_file):
                with open(html_file, 'r', encoding='utf-8') as f:
                    return f.read()
        return "File not found", 404
    except Exception as e:
        return f"Error: {str(e)}", 500
    
 
initialize_yolo_model()
if __name__ == "__main__":
    

    print("🚀 Starting NutriFy Server...")

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False
    )
