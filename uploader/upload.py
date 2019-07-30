from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from uploader.autenticacao import autenticacao
import datetime
from googleapiclient.http import MediaFileUpload
import socket

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

class upload:

    def __init__(self):
        if self.internet():
            self.drive_service = autenticacao(SCOPES).getDriveService()        


    def listarArquivos(self):
        results = self.drive_service.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print(u'{0} ({1})'.format(item['name'], item['id']))


    def criarPasta(self, nomeDoVideo):
        print('Criando pasta...')
        file_metadata = {
            'name': nomeDoVideo,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        file = self.drive_service.files().create(body=file_metadata,fields='id').execute()
        return file.get('id')
    
    def uparArquivo(self, nomeArquivo, localArquivo, mimetype): 
        print('Enviando o arquivo: ', nomeArquivo)
        print('esta operação pode demorar alguns minutos, aguarde...')           
        folder_id = self.criarPasta(nomeArquivo)
        
        file_metadata = {
            'name': nomeArquivo,
            'parents': [folder_id]
        }
        media = MediaFileUpload(localArquivo + "/" + nomeArquivo,
                                mimetype= mimetype,
                                resumable=True)
        
        file = self.drive_service.files().create(body=file_metadata,
                                                media_body=media,
                                                fields='id').execute()

        if file:
            print("[INFO] O arquivo: {} foi enviado com sucesso".format(nomeArquivo))
            os.remove(localArquivo + "/" + nomeArquivo)
            print("[INFO] O arquivo foi excluído do disco\n\n\n")
            return True
        else:
            print("[INFO] O arquivo não foi enviado\n\n\n")
            return False


    def uparVideos(self, local):
        local = "./" + local
        path_size = 0
        porcentagem_concluida = 0
        for videos in os.listdir(local):            
            path_size += os.path.getsize(local + '/' + videos) /( 1024 * 1024)
        
        print("[INFO] 0% concluídos")
        for videos in os.listdir(local):
            porcentagem_concluida += ((os.path.getsize(local + '/' + videos) /( 1024 * 1024)) / path_size)*100             
            self.uparArquivo(videos, local, 'video/mp4')
            print("[INFO] {}% concluídos".format(int(porcentagem_concluida)))
            

    def internet(self,host="8.8.8.8", port=53, timeout=3):
        """
        Host: 8.8.8.8 (google-public-dns-a.google.com)
        OpenPort: 53/tcp
        Service: domain (DNS/TCP)
        """
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except:            
            return False
