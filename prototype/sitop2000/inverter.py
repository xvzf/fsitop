from . import inverter_debug_communicator
from . import inverter_communicator
from . import Packet, PacketBuildException


class Inverter(object):

    # Based on reverse Engineering

    data = {
        "master": None,
        "slave_left": None,
        "slave_right": None
    }

    def __init__(self, port=None, dumpfile="./dumpfile.txt"):
        if not port:
            self.debugmode = True
        
        else:
            self.debugmode = False
    
    def get_voltages_current(self):
        pass

    def update_realtime_data(self):
        pass
