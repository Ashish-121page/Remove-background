from flask import Flask, request, jsonify
from rembg import remove
import os
from werkzeug.utils import secure_filename
import requests

# Set environment variable for model
os.environ["OPENBLAS_L2_SIZE"] = "262144"

app = Flask(__name__)

# Function to download u2net.onnx if not present
def download_u2net_model():
    model_path = '/path/to/your/models/u2net.onnx'  # Update this path
    model_url = 'https://github.com/Nkap23/background_removal_AI/raw/main/u2net.onnx'

    if not os.path.exists(model_path):
        print("Downloading u2net.onnx model...")
        response = requests.get(model_url)
        with open(model_path, 'wb') as file:
            file.write(response.content)
        print("Model downloaded.")

# Call the download function on app start
download_u2net_model()

# Directory to store received files
received_files_dir = 'static/received_files'
os.makedirs(received_files_dir, exist_ok=True)
app.config['RECEIVED_FILES'] = received_files_dir

# Directory to store processed files
processed_files_dir = 'static/processed_files'
os.makedirs(processed_files_dir, exist_ok=True)
app.config['PROCESSED_FILES'] = processed_files_dir

@app.route('/')
def index():
    return "Welcome to the Image Processing Service!"

@app.route('/process', methods=['POST'])
def process_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part", "response_code": 400}), 400

    if 'api_key' not in request.form:
        return jsonify({"error": "No api_key provided", "response_code": 400}), 400

    file = request.files['file']

    customFilename = request.form['Myfilename']
    api_key = request.form['api_key']

    if file:
        # Save the received file with original name and extension
        if customFilename == '':
            filename = secure_filename(file.filename)
        else:
            filename = secure_filename(customFilename)

        og_filename = secure_filename(file.filename)

        file_path = os.path.join(app.config['RECEIVED_FILES'], og_filename)
        file.save(file_path)

        # Perform background removal
        input_data = open(file_path, 'rb').read()
        output_data = remove(input_data)

        # Save the processed file
        processed_filename = filename.split('.')[0] + '.png'
        output_path = os.path.join(app.config['PROCESSED_FILES'], processed_filename)
        with open(output_path, 'wb') as f:
            f.write(output_data)

        # Generate URL for the processed file
        file_url = request.url_root + app.config['PROCESSED_FILES'] + '/' + processed_filename

        return jsonify({"url": file_url, "filename": processed_filename, "status": "success", "response_code": 200})

# Ensure this script is run as the main program and not as a module
if __name__ == '__main__':
    app.run(debug=True)
