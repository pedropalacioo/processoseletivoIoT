"""
Mock machine module for testing MicroPython code on standard Python
Provides mock implementations of Pin and other machine module components
"""


class Pin:
    """Mock Pin class for testing"""
    
    # Pin modes
    IN = 1
    OUT = 0
    
    # Pin states
    LOW = 0
    HIGH = 1
    
    def __init__(self, pin, mode=OUT, value=0):
        """Initialize a mock Pin"""
        self.pin = pin
        self.mode = mode
        self._value = value
    
    def on(self):
        """Set pin to high"""
        self._value = 1
    
    def off(self):
        """Set pin to low"""
        self._value = 0
    
    def value(self, val=None):
        """Get or set pin value"""
        if val is not None:
            self._value = val
        return self._value
    
    def __str__(self):
        return f"Pin({self.pin}, mode={self.mode}, value={self._value})"


class ADC:
    """Mock ADC (Analog-to-Digital Converter) class for testing"""
    
    ATTN_0DB = 0
    ATTN_2_5DB = 1
    ATTN_6DB = 2
    ATTN_11DB = 3
    
    def __init__(self, pin):
        """Initialize a mock ADC"""
        self.pin = pin
        self._value = 0
    
    def read(self):
        """Return a mock ADC value"""
        return self._value
    
    def atten(self, val):
        """Set attenuation (mock)"""
        pass


class I2C:
    """Mock I2C class for testing"""
    
    def __init__(self, id=0, scl=None, sda=None, freq=400000):
        """Initialize a mock I2C"""
        self.id = id
        self.scl = scl
        self.sda = sda
        self.freq = freq
    
    def scan(self):
        """Return list of I2C device addresses"""
        return []
    
    def readfrom(self, addr, nbytes):
        """Read from I2C device"""
        return bytes(nbytes)
    
    def writeto(self, addr, buf):
        """Write to I2C device"""
        return len(buf)


class UART:
    """Mock UART class for testing"""
    
    def __init__(self, id=0, baudrate=115200, tx=None, rx=None):
        """Initialize a mock UART"""
        self.id = id
        self.baudrate = baudrate
        self.tx = tx
        self.rx = rx
    
    def write(self, data):
        """Write to UART"""
        return len(data)
    
    def read(self, nbytes=None):
        """Read from UART"""
        return b''


def unique_id():
    """Return a mock unique ID"""
    return b'\x00' * 6


def reset():
    """Mock reset function"""
    pass
