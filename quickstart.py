from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient import errors, discovery
from apiclient.http import MediaIoBaseDownload
from apiclient.http import MediaFileUpload
import io
import os
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/drive'
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = discovery.build('drive', 'v3', http=creds.authorize(Http()))

def main(parentID):
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    query = parentID + " in parents"
    # Call the Drive v3 API
    results = service.files().list(
        q=query, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    print(type(items))
    
    if not items:
        print('No files found.')
    else:
        fn = '%s.csv' % os.path.splitext(items[0]['name'].replace(' ', '_'))[0]
        print('Files:')
        for item in items:
            print(item)
            print(u'{0} ({1})'.format(item['name'], item['id']))

def download():
    query = "'1uxzassBMq-cmccik0D0b5JBZCtODSQ-L'" + " in parents"
    files = service.files().list(
        q=query, fields="nextPageToken, files(id, name)").execute().get('files', [])
    print(files)

    for file in files:
        data = service.files().get_media(fileId=file['id'])
        fh = io.FileIO(file['name'], 'wb')
        downloader = MediaIoBaseDownload(fh, data)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))

def delete():
    query = "'1uxzassBMq-cmccik0D0b5JBZCtODSQ-L'" + " in parents"
    files = service.files().list(
        q=query, fields="nextPageToken, files(id, name)").execute().get('files', [])

    for file in files:
        print(file)
        data = service.files().delete(fileId=file['id']).execute()
        print('Deleted')

def create_folder():
    body = {
        'name': 'Staging',
        'mimeType': 'application/vnd.google-apps.folder'
    }

    body['parents'] = ['1uxzassBMq-cmccik0D0b5JBZCtODSQ-L']
    query = "'1uxzassBMq-cmccik0D0b5JBZCtODSQ-L'" + " in parents"
    files = service.files().list(
        q=query, fields="nextPageToken, files(id, name)").execute().get('files', [])

    if files == []:
        root_folder = service.files().create(body=body).execute()
        print('Folder ID: %s' % root_folder.get('id'))
    else:
        for file in files:
            if file['name'] == body['name']:
                print('Folder exists')
            else:
                root_folder = service.files().create(body=body).execute()
                print('Folder ID: %s' % file.get('id'))
       
def move_file(): #move from excide folder to archive folder
    folder_id = '1Zh6hNNwIuQ7Sdu-9FrIHAORvyAN7YW6b'
    query = "'1uxzassBMq-cmccik0D0b5JBZCtODSQ-L'" + " in parents"
    files = service.files().list(
        q=query, fields="nextPageToken, files(id, name)").execute().get('files', [])
    
    for file in files:
        
        # Retrieve the existing parents to remove
        file1 = service.files().get(fileId=file['id'],
                                         fields='parents').execute()
        print(file1)
        file_mimeType = service.files().get(fileId=file['id']).execute()
        if file_mimeType['mimeType'] != 'application/vnd.google-apps.folder':
            previous_parents = ",".join(file1.get('parents'))
            # Move the file to the new folder
            file = service.files().update(fileId=file['id'],
                                                addParents=folder_id,
                                                removeParents=previous_parents,
                                                fields='id, parents').execute()
            print('Moved to archive folder')
        else:
            print('This is a folder, unable to transfer')

def upload_file():
    folder_id = '1Zh6hNNwIuQ7Sdu-9FrIHAORvyAN7YW6b'
    file_metadata = {
    'name': 'New Text Document.txt',
    'parents': [folder_id]
    }
    media = MediaFileUpload('New Text Document.txt',
                            mimetype='text/plain',
                            resumable=True)
    file = service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
    print('File ID: %s' % file.get('id'))


if __name__ == '__main__':
    query = "'1Zh6hNNwIuQ7Sdu-9FrIHAORvyAN7YW6b'" + " in parents"
    results = service.files().list(
        q=query, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    p = Paginator(items, 2)
    print(p.page(8))
    print(p.page_range)
    print(p.object_list)
    page1 = p.page(1)
    print("Page number is",page1.number)
    print(page1.has_previous())
    p.num_pages
    # print(page1.previous_page_number())
    # main("'1Zh6hNNwIuQ7Sdu-9FrIHAORvyAN7YW6b'")
    #download('1jbWCtY7DN2lhpfrg8tM5OzCIebRC9kXp')
    #download()
    #delete()
    #create_folder()
    # move_file()
    # upload_file()
    # print('Success')
    #print_files_in_folder(service, '0B5oDOAmJFcoVd2xlSjNOWnVETFU')