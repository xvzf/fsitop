#!/usr/bin/env python3

from sitop2000 import Inverter
from sitop2000 import inverter_debug_communicator

if __name__ == "__main__":
    #i = Inverter()
    idc = inverter_debug_communicator("../dumps/onlinelog02.txt")
    idc.get_all_pairs()