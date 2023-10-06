from smd.red import*

master = Master("/dev/ttyUSB0", 115200)
print(master.scan())