'''
import imutils
from imutils.video import VideoStream

def frameResize(vs, parametros):
    frame = vs.read()
    frame = imutils.resize(frame, width = mn.parametros['resolucao_w'])
    return frame
'''
