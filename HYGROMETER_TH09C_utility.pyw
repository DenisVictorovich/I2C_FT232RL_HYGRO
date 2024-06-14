# HYGROMETER_TH09C_utility.pyw

FT232RL_COM_PORT = "COM37"

import time, serial # pip install pyserial
import threading    # pip install pythreading

from tkinter                      import * # pip install tk
from I2C_base                     import * # I2C_base.py
from HYGROMETER_HOPERF_TH09C_base import * # HYGROMETER_HOPERF_TH09C_base.py

root = Tk()
root.title("HYGROMETER  HOPERF  TH09C  utility")
_H_ = Label ( root, text = "=======", font = ('Arial', 100), fg = 'blue' ) ; _H_.pack()
_T_ = Label ( root, text = "=======", font = ('Arial', 100), fg = 'red'  ) ; _T_.pack()

def SCL(c):   I2C_ser.rts = not c
def SDA(c):   I2C_ser.dtr = not c
def SDA_in(): return not I2C_ser.cts

I2C   = I2C_base(SCL, SDA, SDA_in)
TH09C = HYGROMETER_HOPERF_TH09C_base(I2C)
I2C_ser = serial.serial_for_url(FT232RL_COM_PORT, 9600, do_not_open = True)

def measure():
    try :
        I2C_ser.open()
        I2C.reset_the_bus()
        H, T = TH09C.measure()
        _H_.configure ( text = ("H = %.1f%%" % H).replace('.', ',') )
        _T_.configure ( text = ("T = %.1f°C" % T).replace('.', ',') )
        I2C_ser.close()
    except :
        _H_.configure ( text = "=======" )
        _T_.configure ( text = "=======" )

def process():
    while True:
        measure()
        time.sleep(0.050) # НЕОБХОДИМО, иначе <<подвисает>>

threading.Thread ( target = process ) . start()
root.mainloop()
