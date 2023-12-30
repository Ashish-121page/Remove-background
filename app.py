from flask import Flask, request, jsonify
from rembg import remove
import os
from werkzeug.utils import secure_filename
import mysql.connector


app = Flask(__name__)

# Directory to store received files
received_files_dir = 'static/received_files'
os.makedirs(received_files_dir, exist_ok=True)
app.config['RECEIVED_FILES'] = received_files_dir

# Directory to store processed files
processed_files_dir = 'static/processed_files'
os.makedirs(processed_files_dir, exist_ok=True)
app.config['PROCESSED_FILES'] = processed_files_dir

# MySQL database connection
# db = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="",
#     database="python"
# )

@app.route('/')
def index():
    return "Welcome to the Image Processing Service!"


@app.route('/process', methods=['POST'])
def process_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part","response_code": 400}), 400

    if 'api_key' not in request.form:
        return jsonify({"error": "No api_key provided","response_code": 400}), 400

    if 'image_type' not in request.form:
        file = request.files['file']
    else:
        file = request.files['file']


    customFilename = request.form['Myfilename']
    api_key = request.form['api_key']

    # # Validate the api_key
    # cursor = db.cursor()
    # query = "SELECT * FROM api_keys WHERE api_key = %s"
    # cursor.execute(query, (api_key,))
    # result = cursor.fetchone()
    # if result is None:
    #     return jsonify({"error": "Invalid api_key","response_code": 400}), 401

    if file:
        # Save the received file with original name and extension
        if customFilename == '':
            filename = secure_filename(file.filename)
        else:
            filename = secure_filename(customFilename)

        og_filename = secure_filename(file.filename)

        file_path = os.path.join(app.config['RECEIVED_FILES'], og_filename)
        file.save(file_path)

        # Perform other tasks
        input_data = open(file_path, 'rb').read()
        output_data = remove(input_data)

        # Save the processed file with original name and extension
        # processed_filename = file.filename
        processed_filename = filename.split('.')[0] + '.png'
        output_path = os.path.join(app.config['PROCESSED_FILES'], processed_filename)
        with open(output_path, 'wb') as f:
            f.write(output_data)

        # Generate URL for the processed file
        file_url = request.url_root + app.config['PROCESSED_FILES'] + '/' + processed_filename

        # Store data in MySQL
        # cursor = db.cursor()
        # insert_query = "INSERT INTO processed_files (filename, url) VALUES (%s, %s)"
        # cursor.execute(insert_query, (processed_filename, file_url))
        # db.commit()

        return jsonify({"url": file_url, "filename": processed_filename, "status": "success","response_code": 200})
