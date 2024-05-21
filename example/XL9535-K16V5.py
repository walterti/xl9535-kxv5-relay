from k16v5 import K16V5
from time import sleep
#number of Raspberry PI I2C Bus
bus = 1

#default address of board is 0x20, edit it according to your settings
address = 0x20

board = K16V5(bus,address)

#enable relay A0
board.relay("A",0,True)

#make a pause
sleep(1)

#send a pulse to relay A3
board.send_pulse("A",3)

#another pause
sleep(1)

#disable relay A0
board.relay("A",0, False)
