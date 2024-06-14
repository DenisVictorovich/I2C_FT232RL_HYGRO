
import time

class HYGROMETER_HOPERF_TH09C_base:
    TH09C_DEVICE_ADDRESS = (0x86)
    def __init__(self, I2C):
        self.I2C = I2C
    # The crc7(val)function returns the CRC-7 of a 17 bits value val
    # Compute the CRC-7 of ëvalí (should only have 17 bits)
    def crc7(self, val):
        CRC7WIDTH = 7 # 7 bits CRC has polynomial of 7th order (has 8 terms)
        CRC7POLY = 0x89 # The 8 coefficients of the polynomial
        CRC7IVEC = 0x7F # Initial vector has all 7 bits high
        # Payload data
        DATA7WIDTH = 17
        DATA7MASK  = ( (1 <<  DATA7WIDTH) - 1  ) # 0b 0 1111 1111 1111 1111
        DATA7MSB   = (  1 << (DATA7WIDTH  - 1) ) # 0b 1 0000 0000 0000 0000
        # Setup polynomial
        pol = CRC7POLY;
        # Align polynomial with data
        pol = pol << (DATA7WIDTH - CRC7WIDTH - 1)
        # Loop variable (indicates which bit to test, start with highest)
        bit = DATA7MSB
        # Make room for CRC value
        val = val << CRC7WIDTH
        bit = bit << CRC7WIDTH
        pol = pol << CRC7WIDTH
        # Insert initial vector
        val |= CRC7IVEC
        # Apply division until all bits done
        while ( bit & (DATA7MASK << CRC7WIDTH) ) != 0:
            if ( bit & val ) != 0: val ^= pol
            bit >>= 1
            pol >>= 1
        return val
    def device_check(self): self.I2C.INIT(); ack = not self.I2C.wr_byte(self.TH09C_DEVICE_ADDRESS); self.I2C.TERM(); return ack
    def measure(self):
        H, T = 0.0, 0.0
        # œŒœ€“ ¿ œŒÀ”◊»“‹ ƒ¿ÕÕ€≈ — √»√–Œ-“≈–ÃŒÃ≈“–¿ Œ“ ´HOPERFª
        # »—“Œ◊Õ» : <<TH09C_Datasheet_V1.01.pdf>>
        self.I2C.INIT(); ack = not self.I2C.wr_byte(self.TH09C_DEVICE_ADDRESS); self.I2C.wr_byte(0x22); self.I2C.wr_byte(0x03); self.I2C.TERM()
        if ack:
            time.sleep(0.130) # Wait for measurements to complete
            # Read T and H (read 6 bytes starting from 0x30 in device 86)
            self.I2C.INIT(); self.I2C.wr_byte(self.TH09C_DEVICE_ADDRESS | 0); self.I2C.wr_byte(0x30)
            self.I2C.INIT(); self.I2C.wr_byte(self.TH09C_DEVICE_ADDRESS | 1)
            rbuf = {}
            for i in range(6): rbuf[i] = 0
            for i in range(6): rbuf[i] = self.I2C.rd_byte(i == 5)
            self.I2C.TERM();
            # Extract T_VAL and H_VAL (little endian), assumes 32 bits
            T_val = int(rbuf[2]) << 16 | int(rbuf[1]) << 8 | int(rbuf[0])
            H_val = int(rbuf[5]) << 16 | int(rbuf[4]) << 8 | int(rbuf[3])
            # Extract (and print) the fields
            T_data  = T_val & 0xffff
            T_valid = (T_val >> 16) & 0x1
            T_crc   = (T_val >> 17) & 0x7f
            # Check the CRC
            T_payl = T_val & 0x1ffff;
            T_crc_ok = self.crc7(T_payl) == T_crc
            # Convert to float (and print)
            TinK = float(T_data) / 64 # Temperature in Kelvin
            TinC = TinK - 273.15      # Temperature in Celsius
            TinF = TinC * 1.8 + 32.0  # Temperature in Fahrenheit
            if T_crc_ok: T = TinC
            # Extract (and print) the fields
            H_data  = H_val & 0xffff
            H_valid = (H_val >> 16) & 0x1
            H_crc   = (H_val >> 17) & 0x7f
            # Check the CRC
            H_payl = H_val & 0x1ffff
            H_crc_ok = self.crc7(H_payl) == H_crc
            # Convert to float (and print)
            if H_crc_ok: H = float(H_data) / 512
        return H, T
