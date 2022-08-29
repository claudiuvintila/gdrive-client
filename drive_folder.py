from __future__ import print_function

import io
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import errors
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

import gdrive_client.start


class DriveFolder:
    def __init__(self, service, id):
        self.service = service
        self.id = id

    def list(self, mimetype=None):
        try:
            page_token = None
            if mimetype is None:
                mimetype_filter = ''
            else:
                mimetype_filter = f"and mimeType='{mimetype}'"

            while True:
                response = self.service.files().list(q=f"'{self.id}' in parents and trashed=false {mimetype_filter}",
                                                     spaces='drive',
                                                     fields='nextPageToken, files(id, name)',
                                                     pageToken=page_token).execute()
                for file_ in response.get('files', []):
                    # Process change
                    # print('Found file: %s (%s)' % (file.get('name'), file.get('id')))
                    # print(file)
                    yield file_

                page_token = response.get('nextPageToken', None)
                if page_token is None:
                    break

        except HttpError as error:
            # TODO(developer) - Handle errors from drive API.
            print(f'An error occurred: {error}')

    def upload(self, path, filename=None, mimetype=None):
        if filename is None:
            filename = os.path.basename(path)
        file_metadata = {
            'name': filename,
            "parents": [self.id]
        }
        media = MediaFileUpload(path, mimetype=mimetype)
        file = self.service.files().create(body=file_metadata,  # 'image/jpeg'
                                           media_body=media,
                                           fields='id').execute()
        file_id = file.get('id')
        print('File ID: %s' % file_id)

        return file_id

    def download(self, file_id, local_path):
        request = self.service.files().get_media(fileId=file_id)
        # fh = io.BytesIO()
        with open(local_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print("Download %d%%." % int(status.progress() * 100))

    def create_subfolder(self, subfolder_name):
        file_metadata = {
            'name': subfolder_name,
            "parents": [self.id],
            'mimeType': 'application/vnd.google-apps.folder'
        }
        file = self.service.files().create(body=file_metadata, fields='id').execute()
        subfolder_id = file.get('id')

        print('Folder ID: %s' % subfolder_id)

        return subfolder_id

    def delete(self, file_id):
        try:
            self.service.files().delete(fileId=file_id).execute()
        except errors.HttpError as error:
            print('An error occurred: %s' % error)


if __name__ == '__main__':
    service = gdrive_client.start.start('drive', 'v3')
    drive_folder = DriveFolder(service, 'folder-id')
    for file_dict in drive_folder.list():
        print(file_dict)
