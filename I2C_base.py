
class I2C_base:
    def __init__(self, SCL, SDA, SDA_in):
        # functions pointers:
        self.SCL    = SCL
        self.SDA    = SDA
        self.SDA_in = SDA_in
    def pause(self): return # time.sleep(.0005)
    def reset_the_bus(self):
        i = 9
        self.pause()
        while i != 0:
            self.pause(); self.SCL(1)
            self.pause(); self.SCL(0)
            i -= 1
        self.pause(); self.INIT()
        self.pause(); self.TERM()
    def INIT(self):
        self.SCL(0);              self.pause()
        self.SDA(1); self.SCL(1); self.pause()
        self.SDA(0);              self.pause()
        self.SCL(0);              self.pause()
    def TERM(self):
        self.SCL(0);              self.pause()
        self.SDA(0);              self.pause()
        self.SCL(1);              self.pause()
        self.SDA(1);              self.pause()
    def wr_sda(self, x): self.SDA(x != 0); self.pause()
    def SCL_pulse(self):
        self.pause(); self.SCL(1)
        self.pause(); self.SCL(0)
        self.pause()
    def rd_bit(self):
        self.SDA(1);          self.pause()
        self.SCL(1);          self.pause()
        data = self.SDA_in(); self.pause()
        self.SCL(0);          self.pause()
        return data;
    def wr_byte(self, data):
        mask = 0x80
        while mask != 0:
            self.wr_sda(data & mask)
            self.SCL_pulse()
            mask >>= 1
        return self.rd_bit()
    def rd_byte(self, ack):
        mask = 0x80; data = 0
        while mask != 0:
            if self.rd_bit(): data |= mask
            mask >>= 1
        self.SDA(ack); self.SCL_pulse()
        return data
