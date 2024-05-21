import smbus
from time import sleep
import numpy as np

section_relay = [0x1, 0x2, 0x4, 0x8, 0x10, 0x20, 0x40, 0x80]


class K16V5:
    def __init__(self, i2c_port, i2c_address):
        self.__buf = 0;
        self.__i2c_bus = i2c_port
        self.__bus = smbus.SMBus(i2c_port)
        self.__i2c_addr = i2c_address
        self.__check()

        self.__bus.write_byte_data(self.__i2c_addr, 0x2, 0x00)
        self.__bus.write_byte_data(self.__i2c_address, 0x6, 0x00)

        self.__bus.write_byte_data(self.__i2c_addr, 0x3, 0x00)
        self.__bus.write_byte_data(self.__i2c_address, 0x7, 0x00)

    def __check(self):
        try:
            self.__bus.read_byte_data(self.__i2c_addr, 0x02)
        except IOError:
            raise IOError(f"XL9535 Board not found at I2C address {self.__i2c_addr:#x}")

    def reset(self):
        self.__bus.write_byte_data(self.__i2c_addr, 0x2, 0x00)
        self.__bus.write_byte_data(self.__i2c_addr, 0x3, 0x00)

    def relay(self, section, relay_num, enable: bool = True):
        section_address = 0
        if section != "A" and section != "B":
            raise OSError("Invalid section! Select A or B section according with your board.")
        if section == "A":
            section_address = 0x02
        else:
            section_address = 0x03
        self.__buf = self.__bus.read_byte_data(self.__i2c_addr, section_address)
        x = np.array(self.__bus.read_byte_data(self.__i2c_addr, section_address), dtype=np.uint8)
        result = np.flip(np.unpackbits(x))
        if (result[relay_num] == 1):
            if (enable):
                pass
            else:
                result[relay_num] = 0
        if (result[relay_num] == 0):
            if (enable):
                result[relay_num] = 1
            else:
                pass
        result = np.flip(result)
        result = ''.join(str(x) for x in result)
        result = int(result, base=2)
        self.__bus.write_byte_data(self.__i2c_addr, section_address, result)

    def send_pulse(self, section, relay_num):
        self.relay(section, relay_num, enable=True)
        sleep(1)
        self.relay(section, relay_num, enable=False)
