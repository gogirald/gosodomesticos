# -*- coding: utf-8 -*-
import os
import threading
import Queue
from datetime import datetime
import math

from Tkinter import *
##import Pmw

from time import sleep
from datetime import datetime
import analog_digitalRead2 as AR
import transmit as TR

class InterfazDIS:
    def __init__(self, master, queue, endCommand):
        self.queue = queue
        
        self.flujo_aire = DoubleVar()
        self.flujo_aire.set(0.)
        self.flujo_gas = DoubleVar()
        self.flujo_gas.set(0.)
        self.potencia = DoubleVar()
        self.potencia.set(0)
        self.mensaje =StringVar()

##        self.prom=[]

        self.f0=Frame(root, relief=FLAT, bg='white')
        self.logoDIS=PhotoImage(file='DISLOGOSS.gif')
        self.l1=Label(self.f0,image=self.logoDIS,
                      bg='white', anchor=SE).grid(column=0, row=0)
        self.f0.grid(column=0, row=0)

        self.f1=Frame(root, relief=FLAT, bg='white')
        self.l2=Label(self.f1,text='PRUEBA DE POTENCIA\nGASODOMESTICOS',
                      font=('Verdana', 15, 'bold'),
                      bg='white', fg='#188184', anchor= W).grid(column=1, row=0)
        self.f1.grid(column=1, row=0)

        self.f2=Frame(root, relief=FLAT, bg='white')
        self.logoDIS=PhotoImage(file='DIS.gif')
        self.l3=Label(self.f2,image=self.logoDIS, bg='white', anchor=N).pack(side=TOP)
        self.f2.grid(column=0, row=2)

        self.f6=Frame(root, relief=FLAT, bg='white')
        self.logocor=PhotoImage(file='c_corona.gif')
        self.l4=Label(self.f6,image=self.logocor, bg='white', anchor=SW).grid(column=2, row=0)
        self.f6.grid(column=2, row=0)

##        self.f3=Frame(root, relief=FLAT, bg='white')
##        self.int1=Pmw.Counter(self.f3, labelpos=W,
##                              label_text='Origen\n[mm]:',
##                              label_font=('Verdana', 15),
##                              orient=VERTICAL,
##                              entry_width=10,
##                              entryfield_value=10,
##                              entry_font=('Verdana', 15),
##                              entry_fg='darkgreen',
##                              entry_highlightbackground='green',
##                              entryfield_validate={'validator':'integer', 'min':'0', 'max':'400'})
##        self.int1.pack(side=TOP,padx=10,pady=5)

##        self.int2=Pmw.Counter(self.f3, labelpos=W,
##                              label_text='Car.Max\n[mm]:',
##                              label_font=('Verdana', 15),
##                              orient=VERTICAL,
##                              entry_width=10,
##                              entryfield_value=407,
##                              entry_font=('Verdana', 15),
##                              entry_fg='darkgreen',
##                              entryfield_validate={'validator':'integer', 'min':'0', 'max':'407'})
##        self.int2.pack(side=TOP,padx=10,pady=15)

##        self.f3.grid(column=0, row=1)

        self.f4=Frame(root, relief=FLAT, bg='white')
        self.fila=0
        self.indicadores = ('Desplazamiento [mm]','Elongación [%]', 'Fuerza [N]' )
        for self.indicador in self.indicadores:
            Label(self.f4,text=self.indicador, font=('Verdana', 15, 'bold'),
                  bg='white', anchor=W, padx=10,pady=15, justify=LEFT,
                  relief=FLAT).grid(column=0, row=self.fila)

            self.fila+=1

        Label(self.f4,textvariable=self.flujo_aire, font=('Verdana', 20, 'bold'),
              bg='white', anchor= W, padx=10,pady=5, relief=SUNKEN,
              borderwidth=5, width=8).grid(column=1, row=0)

        self.l5=Label(self.f4,textvariable=self.flujo_gas, font=('Verdana', 20, 'bold'),
                      bg='white', anchor= W, padx=10,pady=5, relief=SUNKEN,
                      borderwidth=5, width=8).grid(column=1, row=1)

        self.l6=Label(self.f4,textvariable=self.potencia, font=('Verdana', 20, 'bold'),
                      bg='white', anchor= W, padx=10,pady=5, relief=SUNKEN,
                      borderwidth=5, width=8).grid(column=1, row=2)

        self.f4.grid(column=2, row=1)

        self.f5=Frame(root, relief=FLAT, bg='white')
                self.b4=Button(self.f5,text='APAGAR', pady=5,
                       font=('Verdana', 16, 'bold'), fg='red',width=10,
                       command=self.apagar).pack(side=RIGHT, pady=3)

        self.f5.grid(column=2, row=2)

        self.f7=Frame(root, relief=FLAT, bg='white')
        self.l7=Label(self.f7,text="Mensajes", font=('Verdana', 10, 'bold'),
                      bg='white', anchor= W, padx=10,pady=5, relief=FLAT).pack(side=TOP)
        self.text = Label(self.f7, textvariable=self.mensaje, height=11, width=30, bg='white',
                          relief = SOLID, font=('Verdana', 12, 'bold'), borderwidth=1).pack(side=TOP)
        self.f7.grid(column=1, row=2)

    def apagar(self):
##        AR.motorOFF()
##        sleep(0.5)
        os.system("shutdown now -h")

    def processIncoming(self):
        """Handle all messages currently in the queue, if any."""
        while self.queue.qsize(  ):
            try:
                msg = self.queue.get(0)
                # Check contents of message and do whatever is needed. As a
                # simple test, print it (in real life, you would
                # suitably update the GUI's display in a richer fashion).
                print msg
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
        self.mult=1.
        self.vflux=0.  #analog value loadcell
        self.fflux=0.0173  #strength convertion factor of loadcell
##        self.tcelda=0.      #truncate vcelda
        self.t=0.

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
            self.gain=1
            self.anterior=self.actual
            self.gui.flujo_aire.set(AR.analog_diff_Read(self.gain))
            self.vcelda=AR.analog_diff_Read(self.gain)
            self.tcelda=math.floor(self.vcelda/500)*500
            self.t=self.tcelda*self.fcelda
            self.gui.fuerza.set(self.t-self.tar)
            self.actual=AR.leerEncoder(self.encMotor)
            self.inicio=AR.leerEncoder(self.encInit)
            self.final=AR.leerEncoder(self.encFin)
            #TR.transmite(self.gui.elong.get(), self.gui.fuerza.get())
            
            #Whether limits are reached, motor wil stop.
            if (AR.leerEncoder(self.encInit) or AR.leerEncoder(self.encFin)):
                        self.gui.mensaje.set('INICIO O FIN DE CARRERA\nALCANZADO')
                        AR.motorOFF()
                        TR.parar()
                        self.cont = 0.

            if (self.gui.mensaje.get()=="Buscando origen...")and(int(self.gui.int1.get())==int(self.gui.despl.get())):
                AR.motorOFF()
                TR.parar()
                self.cont=0
                self.gui.mensaje.set('LISTO PARA\nINICIAR PRUEBA')

            if self.gui.mensaje.get()=="ESTABLECIENDO\nPUNTO DE CERO ESFUERZO":
                self.new = datetime.now()

                if (self.new-old).seconds <=3:
                    self.gui.prom.append(self.tcelda*self.fcelda)
                   # print self.gui.prom

                elif (self.new-old).seconds >=3:
                    m=0
                    for n in self.gui.prom:
                       m+=n
                    self.tar=float(m)/float(len(self.gui.prom))
                    print self.tar
                    self.gui.mensaje.set("VALOR DE CARGA CERO\nESTABLECIDO")


            if self.anterior != self.actual:
                if (AR.leerEncoder(self.gui.separa)) and (not AR.leerEncoder(self.gui.acerca)):
                    
                    if float(self.gui.int1.get()) != 0.:
                        self.cont+=1.
                        self.gui.elong.set(float(self.gui.despl.get())/float(self.gui.int1.get())*100)

                        TR.transmite(self.gui.elong.get(), self.gui.fuerza.get())
                        msg = self.cont*self.mult
                        self.queue.put(msg)

                        if self.t < -1.:
                            AR.motorOFF()
                            TR.parar()
                            self.gui.mensaje.set('EL MATERIAL DE LA PRUEBA\nHA ALCANZADO\nSU PUNTO DE RUPTURA')
                        
                    else:
                        AR.motorOFF()
                        self.gui.mensaje.set('ASIGNE UN VALOR CORRECTO\nEN EL CAMPO ORIGEN')
               
                elif not(AR.leerEncoder(self.gui.separa)) and (AR.leerEncoder(self.gui.acerca)):
                    self.cont-=1.
                    msg = self.cont*self.mult
                    self.queue.put(msg)

            

            if not AR.leerEncoder(self.btonUp):
                self.gui.mensaje.set('SEPARACIÓN DE MORDAZAS')
                AR.motorON(self.gui.separa, self.gui.acerca)
                while not AR.leerEncoder(self.btonUp):
                    pass
                self.gui.mensaje.set('')
                AR.motorOFF()

            if not AR.leerEncoder(self.btonDown):
                self.gui.mensaje.set('ACERCAMIENTO DE MORDAZAS')
                AR.motorON(self.gui.acerca, self.gui.separa)
                while not AR.leerEncoder(self.btonDown):
                    pass
                self.gui.mensaje.set('')
                AR.motorOFF()


         #   else:
          #      AR.motorOFF()
                
                    
    def endApplication(self):
        self.running = 0
        
root=Tk()
root.title=("CAUCHOS CORONA")
root.configure(background='white')
root.attributes('-fullscreen', True)

#InterfazDIS(root)

client = ThreadedClient(root)
root.mainloop()
