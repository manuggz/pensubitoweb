from __future__ import unicode_literals

import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)

class PlaneadorConfig(AppConfig):
    name = 'planeador'

    g_drive = None

    def ready(self):
        from pydrive.auth import GoogleAuth
        from pydrive.drive import GoogleDrive

        gauth = GoogleAuth()

        try:
            gauth.LocalWebserverAuth()
            self.g_drive = GoogleDrive(gauth)
            logger.debug('GDrive conectado!')
        except:
            logger.error('Error connecting to Google Drive!')
            self.g_drive = None
