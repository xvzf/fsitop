from . import inverter_debug_communicator
from . import inverter_communicator
from . import Packet, PacketBuildException


class Inverter(object):

    def __init__(self, port=None, dumpfile="./dumpfile.txt"):
        if not port:
            self.debugmode = True
        
        else:
            self.debugmode = False
    

    def update_realtime_data(self):
        pass
