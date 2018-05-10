# -*- coding: utf-8 -*-
import time
import serial


def transmite(elong=1, fuerz=1):
    
    ser = serial.Serial(port = '/dev/ttyS0', baudrate=9600)
    inicio = 'i'
    fin = 'f'
    elonga = str(elong)
    fuerza = str(fuerz)
    trasmi =inicio+' '+elonga+' '+fuerza+' '+fin+'\n'        
    ser.write(trasmi)
    #print trasmi

def parar():
    ser = serial.Serial(port = '/dev/ttyS0', baudrate=9600)
    trasmi ='t'+' '+'0.0 '+' '+'0.0'+' '+'f'
    ser.write(trasmi)
    
    ser.close()
    
    #print trasmi

#except:
 #   return 'Problemas con la comunicación serial'


#if __name__ == '__main__':
#    trasmite(1,5)

