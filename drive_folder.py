from __future__ import print_function

import io
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

import start


class DriveFolder:
    def __init__(self, service, id):
        self.service = service
        self.id = id

    def list(self):
        try:
            page_token = None
            while True:
                response = self.service.files().list(q="'{}' in parents and trashed=false".format(self.id),
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

    def upload(self, path, filename=None, mimetype='image/jpeg'):
        if filename is None:
            filename = os.path.basename(path)
        file_metadata = {
            'name': filename,
            "parents": [self.id]
        }
        media = MediaFileUpload(path, mimetype=mimetype)
        file = self.service.files().create(body=file_metadata,
                                           media_body=media,
                                           fields='id').execute()
        print('File ID: %s' % file.get('id'))

    def download(self, file_id, local_path):
        request = self.service.files().get_media(fileId=file_id)
        # fh = io.BytesIO()
        with open(local_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print("Download %d%%." % int(status.progress() * 100))


if __name__ == '__main__':
    service = start.start('drive', 'v3')
    drive_folder = DriveFolder(service, 'folder-id')
    for file_dict in drive_folder.list():
        print(file_dict)
