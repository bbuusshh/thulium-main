import serial.tools.list_ports

from serial import Serial
from serial import SerialException
from PyQt5.QtWidgets import QErrorMessage


def connectArduino(response=''):
    for port in serial.tools.list_ports.comports():
        if port.description.startswith("USB-SERIAL CH340"):
            try:
                arduino = Serial(port.device, baudrate=57600, timeout=.01)
            except SerialException as e:
                error = QErrorMessage()
                error.showMessage("Can't open port %s !" % port.device + e.__str__())
                error.exec_()
                return -1
            # here one can add checking response on command arduino.write(b'*IDN?'), know is somewhy doesn't work
            return arduino
    error = QErrorMessage()
    error.showMessage("Arduino is not connected!")
    error.exec_()
    return -1

class COMPortDevice:
    """General class for com ports. """
    connected = False
    port = ''
    baudrate = 9600
    timeout = 1
    identification_names = [] # first few words that should be in the output to *IDN? command splited bu ',' to check

    # function to check based on port info if the port is correct
    def preCheck(self):
        return True

    def close(self): # closes port
        self.stream.close()
        self.connected = False

    def write_read_com(self, command):
        """tries to write command to devise and read it's response"""
        status = True
        readout = ''
        if not self.connected:
            return (False,'')
        try:
            self.stream.write(command)
            readout = self.stream.readline().decode()
        except SerialException as e:
            status = False
            print(e)
        return (status,readout) # return statuus of reading and readout

    def connect(self,idn_message=b'*IDN?\r'):
        """tries to connect port.
        idn_message - message to be sent to devise to identify it
        If connected returns 0, if not - value < 0 """
        try:
            p = Serial(self.port, self.baudrate, timeout=self.timeout)
            p.write(idn_message)
            s = p.readline()
            s = s.decode().split(',')
            print('Port answer ', s)
            # below is check for IDN command respons
            if len(s) < len(self.identification_names): # if length of identification names is smaller than expected
                p.close()
                self.stream = None
                return -1
            else:
                status = True
                for i in range(len(self.identification_names)): # checks every name
                    if s[i] != self.identification_names[i]:
                        status = False
                        break
                if status: # if there no mistakes while name comparison
                    print('\n' + 'Divese ' + str(self.identification_names) + ' connected on port ' + self.port + '\n')
                    self.connected = True
                    self.stream = p
                    return 0
                else: # if any mistake while name comparison
                    p.close()
                    return -1
        except SerialException as e:
            print(e)
            self.stream = None
            return -2

# class COMPortDeviceE(COMPortDevice):
#     """Extended version of com-port device 1) default port 2) GUI"""
#     def __init__(self,default_port=None):
#         super().__init__(self)
#         if default_port:
#             self.port = default_port

