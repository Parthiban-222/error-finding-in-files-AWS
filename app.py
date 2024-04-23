from flask import Flask, request, send_file
import boto3
import os

app = Flask(__name__)

# AWS S3 credentials
AWS_ACCESS_KEY = 'your_access_key'
AWS_SECRET_KEY = 'secret Access key'
S3_BUCKET_NAME='Bucket Name'

# Function to upload file to S3
def upload_to_s3(file_name):
    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )
    s3.upload_file(file_name, S3_BUCKET_NAME, file_name)

# Function to download file from S3
def download_from_s3(file_name):
    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )
    s3.download_file(S3_BUCKET_NAME, file_name, file_name)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_files = request.files.getlist('file[]')
        error_lines = []
        # Ensure the 'uploads' directory exists
        os.makedirs('uploads', exist_ok=True)
        for file in uploaded_files:
            file_name = file.filename
            # Save the uploaded file locally
            file_path = os.path.join('uploads', file_name)
            file.save(file_path)
            # Open the file and find lines containing 'Error' or 'error'
            with open(file_path, 'r') as f:
                lines = f.readlines()
                error_lines.extend([line.strip() for line in lines if 'Error' in line or 'error' in line])
        
        # Create a new file with error lines
        new_file_path = 'error_lines.txt'
        with open(new_file_path, 'w') as f:
            f.write('\n'.join(error_lines))
        
        # Upload the new file to S3
        upload_to_s3(new_file_path)
        
        # Provide download link
        return f'<a href="/download/{new_file_path}">Download Error Lines</a>'
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file[] multiple>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/download/<path:file_name>')
def download(file_name):
    # Download the file from S3
    download_from_s3(file_name)
    return send_file(file_name, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
