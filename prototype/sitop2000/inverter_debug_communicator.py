#!/usr/bin/env python3

from binascii import hexlify, unhexlify
from . import Packet, PacketParseException


class PacketNotInDumpException(Exception):
    pass

class inverter_debug_communicator(object):

    packet_pair_list = []

    def __init__(self, dumpfilename: str):
        self.filename = dumpfilename
        self.parse_dump()
    

    @staticmethod
    def create_new_pair(request, response):
        return {"request": request, "response": response}


    @staticmethod
    def extract_hex(line):
        return unhexlify("".join(line[4:6]))

    
    def parse_bytestrings_dumpfile(self):
        with open(self.filename, "r") as dump:
            request = b""
            response = b""
            request_complete = False

            for line in dump:
                if line.startswith("> "): # Incoming traffic
                    request_complete = True
                    response += inverter_debug_communicator.extract_hex(line)
                else: # Outgoing traffic
                    if request_complete:
                        # capture complete, append to list
                        request_complete = False
                        yield inverter_debug_communicator.create_new_pair(
                                request,
                                response
                            )
                        # Clear buffer
                        request = b""
                        response = b""
                        request += inverter_debug_communicator.extract_hex(line)
                    
                    else:
                        request += inverter_debug_communicator.extract_hex(line)
    

    def parse_dump(self):
        for pair in self.parse_bytestrings_dumpfile():
            # Generate a list of all received packets
            try:

                self.packet_pair_list.append(
                    inverter_debug_communicator.create_new_pair(
                        Packet(pair["request"]),
                        Packet(pair["response"])
                    )
                )

            except PacketParseException as pe:

                # Invalid packet, just drop the pair
                print(str(pe) + ":")
                print(pair)

        
    def get_all_pairs(self):
        return self.packet_pair_list


    def request(self, request: Packet):

        for req, res in self.packet_pair_list:
            if req == request:
                return res
        
        raise PacketNotInDumpException("No dump with the packet available")