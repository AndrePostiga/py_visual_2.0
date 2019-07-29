from snapshoter.keyclipwriter import KeyClipWriter
from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2
import RPi.GPIO as gpio

from uploader.upload import upload
from helpers.configHelper import configHelper


LED_AZUL = 8
LED_VERDE = 10
LED_VERMELHO = 12
LED_AMARELO = 16 #sem função por enquanto

BTN_GRAVAR = 22
BTN_EVENTO = 24
BTN_PROX = 26

gpio.setmode(gpio.BOARD)   #Configura o modo de definição de pinos como BOARD (contagem de pinos da placa)
gpio.setwarnings(False)    #Desativa os avisos 
gpio.setup(LED_AZUL, gpio.OUT)   #define pino 18 como saida
gpio.setup(LED_VERDE, gpio.OUT)   
gpio.setup(LED_VERMELHO, gpio.OUT)   
gpio.setup(LED_AMARELO, gpio.OUT)   
gpio.setup(BTN_GRAVAR, gpio.IN, pull_up_down = gpio.PUD_UP)   #define pino como entrada pull up
gpio.setup(BTN_EVENTO, gpio.IN, pull_up_down = gpio.PUD_UP)   
gpio.setup(BTN_PROX, gpio.IN, pull_up_down = gpio.PUD_UP)   


#eventos e interrupções
gpio.add_event_detect(BTN_PROX, gpio.FALLING, bouncetime=400)
gpio.add_event_detect(BTN_GRAVAR, gpio.FALLING, bouncetime=400)
gpio.add_event_detect(BTN_EVENTO, gpio.FALLING, bouncetime=400)

#apaga todos os leds
gpio.output(LED_AZUL, 0)
gpio.output(LED_AMARELO, 0)
gpio.output(LED_VERDE, 0)
gpio.output(LED_VERMELHO, 0)


parametros = configHelper()

while True:

    gpio.output(LED_AZUL, 1)  #acende led azul, aguardando comandos    
    if gpio.event_detected(BTN_PROX): #se o botão prox config for apertado

        parametros.proxConfig()
        gpio.output(LED_AZUL, 0)
        print("[INFO] Trocando configuração, configuração {} selecionada".format(parametros.configNumber))
        print(parametros.currentConfig)
    elif gpio.event_detected(BTN_GRAVAR):       

        gpio.output(LED_VERMELHO, 1)

        print("[INFO] Esquentando a câmera")
        vs = VideoStream(parametros.currentConfig['camera']).start() 
        #vs = VideoStream(usePiCamera= parametros.currentConfig['camera'] > 0).start()  for webcam
        time.sleep(2.0)

        kcw = KeyClipWriter(parametros.currentConfig['buffer'])
        consecFrames = 0 #conta o numero de frames que não contém um evento de interesse

        while True:
            frame = vs.read()
            frame = imutils.resize(frame, width = parametros.currentConfig['resolucao_w'])
            updateConsecFrames = True

            #cv2.imshow("Frame", frame) 
            key = cv2.waitKey(1) & 0xFF

            if gpio.event_detected(BTN_GRAVAR):
                gpio.output(LED_VERMELHO, 0)
                break
            elif gpio.event_detected(BTN_EVENTO):
                gpio.output(LED_VERDE, 1)
                print("Botão Pressionado...efetuando a gravação, aguarde alguns segundos\n")
                consecFrames=0

                if not kcw.recording:
                    timestamp = datetime.datetime.now()
                    p = "{}/{}.avi".format('output', timestamp.strftime("%d-%m-%Y-%H:%M:%S"))
                    kcw.start(p, cv2.VideoWriter_fourcc(*parametros.currentConfig['codec']), parametros.currentConfig['fps'])
                
                
            if updateConsecFrames:
                consecFrames += 1

            kcw.update(frame)

            if kcw.recording and consecFrames == parametros.currentConfig['buffer']:
                kcw.finish()
                gpio.output(LED_VERDE, 0)

        if kcw.recording:
            kcw.finish()
            gpio.output(LED_VERDE, 0)

        cv2.destroyAllWindows()
        vs.stop()
        gpio.output(LED_VERMELHO, 0)
        
        #upa os arquivos ao final da gravação
        up = upload()
        if up.internet():
            up.uparVideos('../output')
        else:
            print("[INFO] O computador não possui internet neste momento, o arquivo será salvo no disco")