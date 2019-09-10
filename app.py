from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient import errors, discovery
from django.conf import settings
settings.configure()
from django.template import Template, Context
from flask import flash
from apiclient.http import MediaFileUpload
from apiclient.http import MediaIoBaseDownload
from apiclient.http import MediaFileUpload

import datetime
import json
import io
import os
import ast
from functools import wraps

from flask import Flask
from flask import Response
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import send_from_directory
from flask import url_for

from werkzeug import secure_filename
from settings import *

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

app = Flask(__name__)

SCOPES = 'https://www.googleapis.com/auth/drive'
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
service = build('drive', 'v3', http=creds.authorize(Http()))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def list_files_in_drive():
    query = "'1Zh6hNNwIuQ7Sdu-9FrIHAORvyAN7YW6b'" + " in parents"
    # Call the Drive v3 API
    results = service.files().list(
        q=query, fields="nextPageToken, files(id, name)").execute()
    global items, files, p # To set variable items to be global (use in upload function) 
    items = results.get('files', [])
    paginator = Paginator(items, 5)
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(item)
            page = request.args.get('page', 1)
            try:
                p = paginator.page(page)
            except PageNotAnInteger:
                p = paginator.page(1)
            except EmptyPage:
                p = paginator.page(paginator.num_pages)
        files = p.object_list

@app.route('/', methods=['GET','POST'])
def start():
    list_files_in_drive()
    return render_template('index.html', items=files, p=p )

@app.route('/uploaded', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file1 = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file1.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file1 and allowed_file(file1.filename):
            # filename = secure_filename(file1.filename)
            # file_path = 'uploaded\\'
            filename = secure_filename(file1.filename)
            file1.save(filename)
            print(filename)
            folder_id = '1Zh6hNNwIuQ7Sdu-9FrIHAORvyAN7YW6b'
            file_metadata = {
            'name': file1.filename,
            'parents': [folder_id]
            }
            media = MediaFileUpload(filename,
                            resumable=True)
            print(media)
            file1 = service.files().create(body=file_metadata,
                                                media_body=media,
                                                fields='id').execute()
            print('File ID: %s' % file1.get('id'))
        list_files_in_drive()
        global upload_successful
        upload_successful = "Upload Successful!"
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for('uploaded_file', filename=filename))
    return render_template('index.html', items=files, p=p, upload_successful=upload_successful)
    # return redirect(url_for('start'))

@app.route('/deletefile', methods=['POST'])
def delete():
    file_id = request.form['id']
    data = service.files().delete(fileId=file_id).execute()
    list_files_in_drive()
    global delete_successful
    delete_successful = "Delete successful!"
    return render_template('index.html', items=files, p=p, delete_successful=delete_successful)

@app.route('/downloadfile', methods=['POST'])
def download():
    home = os.path.expanduser('~')
    download = os.path.join(home, 'Downloads')
    get_file = ast.literal_eval(request.form['id'])
    file_path = download + "\\" + get_file['name']
    data = service.files().get_media(fileId=get_file['id'])
    fh = io.FileIO(get_file['name'], 'wb')
    downloader = MediaIoBaseDownload(fh, data)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    list_files_in_drive()
    return render_template('index.html', items=files, p=p)

@app.route('/uploads/<path:filename>', methods = ['GET', 'POST'])
def uploaded_file(filename):
    # return jsonify(filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run()