import smbus
from time import sleep

class K16V5:
    
    REG_OUT_A = 0x02
    REG_OUT_B = 0x03
    REG_CONF_A = 0x06
    REG_CONF_B = 0x07

    def __init__(self, i2c_port, i2c_address):
        self.__i2c_bus = i2c_port
        self.__i2c_addr = i2c_address
        self.__bus = smbus.SMBus(i2c_port)
        
        # Shadow registers
        self.__state_A = 0x00
        self.__state_B = 0x00

        self.__check()
        self.__setup()

    def __check(self):
        try:
            self.__bus.read_byte_data(self.__i2c_addr, self.REG_OUT_A)
        except IOError:
            raise IOError(f"XL9535 Board not found at I2C address {self.__i2c_addr:#x}")

    def __setup(self):
        # Define all ports as output (0x00)
        self.__bus.write_byte_data(self.__i2c_addr, self.REG_CONF_A, 0x00)
        self.__bus.write_byte_data(self.__i2c_addr, self.REG_CONF_B, 0x00)
        self.reset()

    def reset(self):
        # Clear the relays
        self.__state_A = 0x00
        self.__state_B = 0x00
        self.__bus.write_byte_data(self.__i2c_addr, self.REG_OUT_A, self.__state_A)
        self.__bus.write_byte_data(self.__i2c_addr, self.REG_OUT_B, self.__state_B)

    def relay(self, section, relay_num, enable: bool = True):
        if section not in ["A", "B"]:
            raise ValueError("Invalid section! Select A or B section according with your board.")
        
        if not 0 <= relay_num <= 7:
            raise ValueError("Relay number must be between 0 and 7.")

        # Selects the register and current memory state
        reg_address = self.REG_OUT_A if section == "A" else self.REG_OUT_B
        current_state = self.__state_A if section == "A" else self.__state_B

        # Bitwise operations
        if enable:
            new_state = current_state | (1 << relay_num)
        else:
            new_state = current_state & ~(1 << relay_num)

        # Writes back to relay board on I2C bus and update the state
        if new_state != current_state:
            self.__bus.write_byte_data(self.__i2c_addr, reg_address, new_state)
            if section == "A":
                self.__state_A = new_state
            else:
                self.__state_B = new_state

    def send_pulse(self, section, relay_num):
        self.relay(section, relay_num, enable=True)
        sleep(1)
        self.relay(section, relay_num, enable=False)
