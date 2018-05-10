# -*- coding: utf-8 -*-

import time
import datetime
from tkMessageBox import *
import Adafruit_ADS1x15
import Adafruit_BMP.BMP085 as BMP085
import dht11
import requests
import RPi.GPIO as GPIO

import csv
##presure sensor initialize
sensor = BMP085.BMP085()
#humidity and temperature sensor
instance = dht11.DHT11(pin=18)

relesOut=[22,32,36]
##relesOut=[25,12,16]
encodIn=[29,31,33]
##encodIn=[5,6,13]
btnIn=[7,12,13,15,16]
##btnIn=[4,18,27,22,23]

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(relesOut, GPIO.OUT)
GPIO.setup(encodIn, GPIO.IN)
GPIO.setup(btnIn, GPIO.IN)

def analog_diff_Read(GAIN=1):
    try:
        adc = Adafruit_ADS1x15.ADS1115()
        g = GAIN
        value = adc.read_adc_difference(0, gain=g)
        return value
    
    except IOError as e:
        showerror(title='Lectura análoga',
                  message = 'Verifique la conexión\nDel módulo de entradas análogas', font=('Verdana', 15))

def analogRead(GAIN=1):
    try:
        adc = Adafruit_ADS1x15.ADS1115()
        g = GAIN
        adc.start_adc(0, gain=g)
        value = adc.get_last_result()
        return value
    
    except IOError as e:
        showerror(title='Lectura análoga',
                  message = 'Verifique la conexión\nDel módulo de entradas análogas', font=('Verdana', 15))

def stopRead():
    adc.stop_adc()
    showwarning(title='Lectura análoga detenida')

def leerEncoder(pin=29):
    d=GPIO.input(pin) #lee estado de encoder
    #time.sleep(0.001)
    return d

def motorON(relAct, relDes):
    #time.sleep(0.1)
    GPIO.output(relDes, 0)
    #time.sleep(0.1)
    GPIO.output(relAct, 1)
    pass

def motorOFF():
   # time.sleep(0.1)
    #GPIO.output(22, 0)
    GPIO.output(25, 0)
   # time.sleep(0.1)
##    GPIO.output(32, 0)
    GPIO.output(12, 0)
   # time.sleep(0.1)
##    GPIO.output(36, 0)
    GPIO.output(16, 0)
    pass

def presion():
    
    t=sensor.read_temperature()
    p=sensor.read_pressure()
    a=sensor.read_altitude()
    sl=sensor.read_sealevel_pressure(a)
    return t,p,a,sl

def humedad():
    medida=instance.read()
    if medida.is_valid():
        dth_t=medida.temperature
        dth_h=medida.humidity
        return dth_t, dth_h
    else:
        return None,None
#def escribir():
 #   fecha = datetime.datetime.now()
  #  fecha1 = fecha.year()
   # with open('')
