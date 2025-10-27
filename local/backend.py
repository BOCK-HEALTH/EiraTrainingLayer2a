from flask import Flask, request, jsonify, send_from_directory
import boto3
import os
from werkzeug.utils import secure_filename
import threading

app = Flask(__name__)

# Simple token for API security
API_TOKEN = os.getenv('EIRA_API_TOKEN', 'changeme')

# Dataset config
DATASETS = {
    'audio': {
        'main_bucket': 'eira1-general-datasets',
        'sub_bucket': 'eira1-audio-datasets',
        'prefix': 'audio/'
    },
    'video': {
        'main_bucket': 'eira1-general-datasets',
        'sub_bucket': 'eira1-video-datasets',
        'prefix': 'video/'
    },
    'images-transcripts': {
        'main_bucket': 'eira1-general-datasets',
        'sub_bucket': 'eira1-seg.images-seg.transcripts-datasets',
        'prefixes': ['pairs_of_img_aud_trans/']  # Will filter for chunked_images and chunked_transcripts
    }
}

# Helper: check token
# Commented out for internal use - uncomment if you need API security
# @app.before_request
# def check_token():
#     if request.endpoint and request.endpoint.startswith('fetch_'):
#         token = request.headers.get('Authorization')
#         if token != f"Bearer {API_TOKEN}":
#             return jsonify({'error': 'Unauthorized'}), 401

# Helper: copy objects from main to sub bucket

def copy_dataset(dataset_key):
    config = DATASETS.get(dataset_key)
    if not config:
        return {'error': 'Invalid dataset'}, 400
    s3 = boto3.resource('s3')
    src_bucket = s3.Bucket(config['main_bucket'])
    dest_bucket = s3.Bucket(config['sub_bucket'])
    copied = []
    
    # Handle special case for images-transcripts dataset
    if dataset_key == 'images-transcripts':
        # Get all objects under pairs/ prefix
        for obj in src_bucket.objects.filter(Prefix='pairs/'):
            src_key = obj.key
            # Only copy if path contains chunked_images or chunked_transcripts
            if '/chunked_images/' in src_key or '/chunked_transcripts/' in src_key:
                copy_source = {'Bucket': config['main_bucket'], 'Key': src_key}
                # Remove 'pairs/' prefix from destination key
                dest_key = src_key.replace('pairs/', '', 1)
                dest_bucket.Object(dest_key).copy(copy_source)
                copied.append(dest_key)
    elif dataset_key in ['audio', 'video']:
        # Remove prefix for audio and video datasets
        prefix = config['prefix']
        for obj in src_bucket.objects.filter(Prefix=prefix):
            src_key = obj.key
            copy_source = {'Bucket': config['main_bucket'], 'Key': src_key}
            # Remove the prefix from destination key (e.g., 'audio/' or 'video/')
            dest_key = src_key.replace(prefix, '', 1)
            dest_bucket.Object(dest_key).copy(copy_source)
            copied.append(dest_key)
    else:
        # Standard copy for other datasets (keep original structure)
        for obj in src_bucket.objects.filter(Prefix=config['prefix']):
            src_key = obj.key
            copy_source = {'Bucket': config['main_bucket'], 'Key': src_key}
            dest_bucket.Object(src_key).copy(copy_source)
            copied.append(src_key)
    
    return {'status': 'success', 'copied': copied}

# API endpoints
@app.route('/fetch/<dataset>', methods=['POST'])
def fetch_dataset(dataset):
    result = copy_dataset(dataset)
    print(f"[LOG] Fetched dataset: {dataset}, result: {result}")
    # Always include sub_bucket and copied files/count for frontend
    if isinstance(result, dict) and result.get('status') == 'success':
        feedback = {
            'status': 'success',
            'copied': result.get('copied', []),
            'sub_bucket': DATASETS[dataset]['sub_bucket'],
        }
        return jsonify(feedback)
    return jsonify(result)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/style.css')
def serve_css():
    return send_from_directory('.', 'style.css')

@app.route('/app.js')
def serve_js():
    return send_from_directory('.', 'app.js')

UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload-txt', methods=['POST'])
def upload_txt():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not file.filename.endswith('.txt'):
        return jsonify({'error': 'Only .txt files allowed'}), 400
    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(save_path)
    # Start processing in a background thread
    def process():
        from aws import process_links_from_file
        process_links_from_file(save_path)
    threading.Thread(target=process).start()
    return jsonify({'status': 'success', 'message': f'File {filename} uploaded. Processing started.'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)