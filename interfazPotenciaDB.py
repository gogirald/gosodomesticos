# -*- coding: utf-8 -*-
import os
import threading
import Queue
from datetime import datetime
import math

from Tkinter import *

from time import sleep
from datetime import datetime
import analog_digitalRead2 as AR
import transmit as TR
import enviomongo

import requests
#import urllib
#import Adafruit_ADS1x15

class InterfazDIS:
    def __init__(self, master, queue, endCommand):
        self.queue = queue
        self.test = False
        self.flujo_aire = DoubleVar()
        self.flujo_aire.set(0.)
        self.flujo_gas = DoubleVar()
        self.flujo_gas.set(0.)
        self.potencia = DoubleVar()

        self.pcsval = DoubleVar()
        self.pcsval.set(0.)
        self.kvalue = DoubleVar()
        self.kvalue.set(0.)
        self.pnominal = DoubleVar()
        self.pnominal.set(0.)
        self.realiza = StringVar()
        self.realiza.set('')
        
        self.prom=[]

        self.f0=Frame(root, relief=FLAT, bg='white')
        self.logoDIS=PhotoImage(file='DISLOGOSS.gif')
        self.l1=Label(self.f0,image=self.logoDIS,
                      bg='white', anchor=SE).grid(column=0, row=0)
        self.f0.grid(column=0, row=0)

##        self.f1=Frame(root, relief=FLAT, bg='white')
        self.l2=Label(root,text='MEDICIÓN POTENCIA', font=('Verdana', 15, 'bold'),
                      bg='white', fg='darkcyan', anchor= W).grid(column=1, row=0)
##        self.f1.grid(column=1, row=0)

##        self.f2=Frame(root, relief=FLAT, bg='white')
        self.logoHAC=PhotoImage(file='haceb.gif')
        self.l3=Label(root,image=self.logoHAC, bg='white', anchor=N).grid(column=2, row=0)
##        self.f2.grid(column=0, row=2)
        self.pos=0
        
        self.f3=Frame(root, relief=FLAT, bg='white')
        self.entradas_gas = ('PCS [kWh/m3]','valor k',
                             'P Nominal', 'Realiza'  )
        for self.indicador in self.entradas_gas:
            Label(self.f3,text=self.indicador,
                  bg='white', anchor=W, justify=LEFT,
                  relief=FLAT).grid(column=0, row=self.pos)
            self.pos+=1
            
        self.pcs = Entry(self.f3, textvariable=self.pcsval, bg='white',width=6).grid(column=1, row=0)
        self.k = Entry(self.f3,textvariable=self.kvalue, bg='white',width=6).grid(column=1, row=1)
        self.nom = Entry(self.f3,textvariable=self.pnominal, bg='white',width=6).grid(column=1, row=2)
        self.rea = Entry(self.f3,textvariable=self.realiza, bg='white',width=6).grid(column=1, row=3)

        self.f3.grid(column=0, row=1, rowspan=3)
        

        self.f4=Frame(root, relief=FLAT, bg='white')
        self.fila=0
        self.indicadores = ('Flujo Aire [L/min]','Flujo Gas [L/min]', 'Potencia [kW]' )
        for self.indicador in self.indicadores:
            Label(self.f4,text=self.indicador,
                  bg='white', anchor=W, justify=LEFT,
                  relief=FLAT).grid(column=0, row=self.fila)

            self.fila+=1

        self.fa=Label(self.f4,textvariable=self.flujo_aire,
              bg='white', anchor= W, relief=SUNKEN,
              borderwidth=3, width=7).grid(column=1, row=0)

        self.fg=Label(self.f4,textvariable=self.flujo_gas,
                      bg='white', anchor= W, relief=SUNKEN,
                      borderwidth=3, width=7).grid(column=1, row=1)

        self.p=Label(self.f4,textvariable=self.potencia,
                      bg='white', anchor= W, relief=SUNKEN,
                      borderwidth=3, width=7).grid(column=1, row=2)
        self.f4.grid(column=1, row=1)

        self.f5=Frame(root, relief=FLAT, bg='white')
        self.b4=Button(self.f5,text='APAGAR', pady=5,
                       fg='red',width=8,
                       command=self.apagar).pack(side=RIGHT, pady=3)
        self.f5.grid(column=1, row=4)

        self.f6=Frame(root, relief=FLAT, bg='white')
        self.b5=Button(self.f6,text='PRUEBA', pady=5,
                       fg='darkcyan',width=8,
                       command=self.prueba).pack(side=RIGHT, pady=3)
        self.f6.grid(column=0, row=4)


##        self.f7=Frame(root, relief=FLAT, bg='white')
##        self.l7=Label(self.f7,text="Mensajes", font=('Verdana', 10, 'bold'),
##                      bg='white', anchor= W, padx=10,pady=5, relief=FLAT).pack(side=TOP)
##        self.text = Label(self.f7, textvariable=self.mensaje, height=11, width=30, bg='white',
##                          relief = SOLID, font=('Verdana', 12, 'bold'), borderwidth=1).pack(side=TOP)
##        self.f7.grid(column=1, row=2)

    def apagar(self):
##        AR.motorOFF()
##        sleep(0.5)
        os.system("shutdown now -h")

    def prueba(self):
        self.test = True
     
    def processIncoming(self):
        """Handle all messages currently in the queue, if any."""
        while self.queue.qsize(  ):
            try:
                msg = self.queue.get(0)
                # Check contents of message and do whatever is needed. As a
                # simple test, print it (in real life, you would
                # suitably update the GUI's display in a richer fashion).
                print (msg)
            except Queue.Empty:
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                pass

class ThreadedClient:
    """
    Launch the main part of the GUI and the worker thread. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """
    
    def __init__(self, master):
        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI as well. We spawn a new thread for the worker (I/O).
        """
        self.presion=0.
        self.temperatura=0.
        self.temperatura2=0.
        self.humedad=0.
        self.vflujo=0.  #ADC value flow sensor
        self.fflujo=3.75e-4  #convertion factor of analog sensor
        self.potencia=0.
        self.gas=0. #gas flow value
        self.aire=0. #air flow value 
        self.BMP_Val=0.

        self.temperatura2=0.
        self.humedad=0.

        self.tar=0.     #This variable is used to stablishing zero loadcell value
        
        self.master = master

        # Create the queue
        self.queue = Queue.Queue(  )

        # Set up the GUI part
        self.gui = InterfazDIS(master, self.queue, self.endApplication)

        # Set up the thread to do asynchronous I/O
        # More threads can also be created and used, if necessary
        self.running = 1
        self.thread1 = threading.Thread(target=self.workerThread1)
        self.thread1.start(  )

        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.periodicCall(  )

    def periodicCall(self):
        """
        Check every 200 ms if there is something new in the queue.
        """
        self.gui.processIncoming(  )
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            import sys
            sys.exit(1)
        self.master.after(200, self.periodicCall)

    def workerThread1(self):
        """
        This is where we handle the asynchronous I/O. For example, it may be
        a 'select(  )'. One important thing to remember is that the thread has
        to yield control pretty regularly, by select or otherwise.
        """
        while self.running:
            # To simulate asynchronous I/O, we create a random number at
            # random intervals. Replace the following two lines with the real
            # thing.
            #origen = self.gui.init1.get()
            #carrera = self.gui.init2.get()

            sleep(0.01)
            self.gain=2/3

##            self.gui.despl.set(self.cont)
            self.vflujo=AR.analog_diff_Read(self.gain)
            self.aire=self.vflujo*self.fflujo
            self.gui.flujo_aire.set(self.aire)
            self.gas=self.aire*self.gui.kvalue.get()
            self.gui.flujo_gas.set(self.gas)
            self.BMP_Val=AR.presion()
            self.potencia=self.gui.flujo_aire.get()*0.06*self.BMP_Val[1]*15*(float(self.gui.pcsval.get()))*(float(self.gui.kvalue.get()))/(self.BMP_Val[3]*self.BMP_Val[0])
            self.gui.potencia.set(self.potencia)
##            self.inicio=AR.leerEncoder(self.encInit)
##            self.final=AR.leerEncoder(self.encFin)
            #TR.transmite(self.gui.elong.get(), self.gui.fuerza.get())
            self.temperatura2, self.humedad = AR.humedad()

            if self.gui.test:

                if self.temperatura2!= None:
                    tiem=datetime.utcnow()
                    real=self.gui.realiza.get()
                    pnom=self.gui.pnominal.get()
                    temp1=self.BMP_Val[0]
                    pres=self.BMP_Val[1]
                    temp2=self.temperatura2
                    hum=self.humedad
                    alt=self.BMP_Val[2]
                    aire=[]
                    gas=[]
                    poten=[]
                    for d in range(20):
                        bmp=AR.presion()
                        flujo=AR.analog_diff_Read(self.gain)
                        aire1=flujo*self.fflujo
                        aire.append(aire1)
                        gas.append(aire1*self.gui.kvalue.get())
                        poten.append(aire1*0.06*bmp[1]*15*(float(self.gui.pcsval.get()))*(float(self.gui.kvalue.get()))/(bmp[3]*bmp[0]))
                    datosDB = {'date':tiem,
                               'realiza':real,
                               'nominal':pnom,
                               'temperatura1':temp1,
                               'temperatura2':temp2,
                               'presion':pres,
                               'humedad':hum,
                               'altitud':alt,
                               'flujo aire':aire,
                               'flujo gas':gas,
                               'potencia':poten}
                    post_id = enviomongo.enviarMongo(datosDB)
                    self.gui.test = False
                #print post_id
                #datos='&field1='+str(self.aire)+'&field2='+str(self.gas)+'&field3='+str(self.potencia)+'&field4='+str(self.BMP_Val[1])+'&field5='+str(self.BMP_Val[0])+'&field6='+str(self.temperatura2)+'&field7='+str(self.humedad)+'&field8='+str(self.BMP_Val[2])
            #print url+datos
            #r=requests.get(url+datos)
            #print r.text
            #sleep(5)
                 
    def endApplication(self):
        self.running = 0
        
url='https://api.thingspeak.com/update?api_key=55V6GO7IAWJXP12C'
root=Tk()
root.title=("FAST TEST BRAIN")
root.configure(background='white')
root.attributes('-fullscreen', True)

#InterfazDIS(root)

client = ThreadedClient(root)
root.mainloop()
