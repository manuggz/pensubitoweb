import os

from googleapiclient.http import MediaFileUpload
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from misvoti.settings import BASE_DIR
# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
#SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'
from planeador.gdrive_namespaces import ID_DRIVE_CARPETA_MIS_VOTI


def main():
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()

    drive = GoogleDrive(gauth)
    # Create GoogleDriveFile instance with title 'Hello.txt'.
    file1 = drive.CreateFile({'title': 'Nuevo Plan3', 'parents':[
        {
            "kind": "drive#parentReference",
            'id':ID_DRIVE_CARPETA_MIS_VOTI
        }
    ]})
    file1.Upload()  # Upload the file.

    print('title: %s, id: %s' % (file1['title'], file1['id']))
    # title: Hello.txt, id: {{FILE_ID}}


if __name__ == '__main__':
    print  BASE_DIR
    main()
