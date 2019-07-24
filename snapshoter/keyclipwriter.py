from collections import deque
from threading import Thread
from queue import Queue
import time
import cv2

#bufsize o numero máximo de frames que ficará em cache na memoria do buffer
#timeout numero de segundos para "dormir" quando estiver escrevendo videoclips ou nenhum frame para ler

class KeyClipWriter:
    def __init__(self, bufSize=64, timeout=1.0):
        self.bufSize = bufSize
        self.timeout = timeout
    
        self.frames = deque(maxlen=bufSize)
        self.Q = None
        self.writer = None
        self.thread = None
        self.recording = False

    def update(self, frame):
        #update os frames do buffer
        self.frames.appendleft(frame)

        #se estiver gravando, atualiza a fila inteira
        if self.recording:
            self.Q.put(frame)

    def start(self, outputPath, fourcc, fps):
        #indicar qndo estamos gravando, iniciar o escritor de video
        #iniciar a fila de frames que vão ser escritas no arquivo de video
        self.recording = True
        print(outputPath)
        self.writer = cv2.VideoWriter(outputPath, fourcc, fps, 
            (self.frames[0].shape[1], self.frames[0].shape[0]), True)
        self.Q = Queue()

        #iterar pelos frames na fila ligada e adicionar a fila comum
        for i in range(len(self.frames), 0, -1):
            self.Q.put(self.frames[i-1])
        
        #iniciar a thread de escrita dos frames no arquivo de video
        self.thread = Thread(target=self.write, args=())
        self.thread.daemon = True
        self.thread.start()

    def write(self):
        while True:
            #se o programa já parou de gravar
            if not self.recording:
                return
            
            if not self.Q.empty():
                #pega o proximo frame da fila e grava
                frame = self.Q.get()
                self.writer.write(frame)

            #caso contrario a fila está vazia
            else:
                time.sleep(self.timeout)
    

    def flush(self):
        #esvazia a fila, quando um video terminar nós precisamos mandar imadiatamente os frames para o arquivo
        while not self.Q.empty():
            frame = self.Q.get()
            self.writer.write(frame)

    def finish(self):
        #indica que a gravação terminou
        self.recording = False
        self.thread.join()
        self.flush()
        self.writer.release()