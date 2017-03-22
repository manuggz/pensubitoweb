from __future__ import unicode_literals

from django.apps import AppConfig


class PlaneadorConfig(AppConfig):
    name = 'planeador'

    g_drive = None

    def ready(self):
        from pydrive.auth import GoogleAuth
        from pydrive.drive import GoogleDrive

        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()

        self.g_drive = GoogleDrive(gauth)
