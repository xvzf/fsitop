from binascii import hexlify, unhexlify
import struct
import re
import unittest
from enum import Enum


class PacketParseException(Exception):
    """
    Exception during packet parsing
    """
    pass


class PacketBuildException(Exception):
    """
    Exception during packet building
    """
    pass


class PacketType(Enum):
    """
    Defines whether the packet was a response or request
    """
    REQUEST = "$"
    RESPONSE = "&"


class Packet(object):
    """
    Utility class for SITOP Solar 2000 packets
    """

    # Should be correct
    # TYPE;TO;FROM;CMD;8DATA*CHECKSUM
    pattern_sitop_2000 = b'([\\$\\&])([0-9]{2});([0-9]{2});([0-9A-F]{2});(.{8})\\*([0-9A-F]{2})\r\n'


    def __init__(self, toparse:None, tobuild=None) -> None:
        """
        Helps parsing and building packets for the SITOP Solar 2000 solar inverter
        :param toparse: Bytestream which should be parsed
        :param tobuild: Dict for which a packet should be created
        ! ONLY USE ONE OF THE KEYWORD PARAMETERS
        """
        # Compile regex pattern
        self.regex = re.compile(self.pattern_sitop_2000)
        
        # Check input
        if toparse and tobuild:
            raise PacketParseException("Cannot parse and build packet with the same instance")

        if toparse:
            self.parsed = True
            self.built = False
            self.parse(toparse)
        
        if tobuild and not tobuild.keys() is ["type", "to", "from", "cmd", "data"]:
            raise PacketBuildException("Invalid input dict")
        else:
            # @TODO
            self.parsed = False
            self.built = True
            pass
        

    def parse(self, bytestring: bytes) -> None:
        """
        Parses a packet received from a SITOP Solar 2000 series
        :param bytestring: Raw input bytes from serial interface
        """

        def parse_two_hex(bytestring: bytes):
            """
            :param bytestring: 2-digit hex encoded byte
            :return: decoded byte
            """
            return struct.unpack("B", unhexlify(bytestring.decode("ASCII")))[0]

        # Check against regex
        matcher = self.regex.match(bytestring)

        # Check if regex was successfull
        if not matcher:
            raise PacketParseException("Malformed bytestring")
        
        # Fill in dict
        self.pdict = {}
        self.pdict["type"]     = matcher.group(1)
        self.pdict["to"]       = parse_two_hex(matcher.group(2))
        self.pdict["from"]     = parse_two_hex(matcher.group(3))
        self.pdict["cmd"]      = parse_two_hex(matcher.group(4))
        self.pdict["data"]     = [i for i in matcher.group(5)]
        self.pdict["checksum"] = parse_two_hex(matcher.group(6))

        if self.pdict["checksum"] != self.checksum(self.pdict):
            raise PacketParseException("Checksum missmatch")
        
        # Just store the original input
        self.bytestring = bytestring
    

    @staticmethod
    def checksum(pdict: dict) -> int:
        """
        Calculates the checksum for a generated or parsed packet
        
        - Naive algorithm: Add everything apart from data and modulo by 256
                           then xor through every data(payload) byte

        :param pdict: Packet for which the checksum should be generated
        :return checksum byte
        """
        checksum = 0

        for key in ["to", "from", "cmd"]:
            checksum = (checksum + pdict[key]) % 0xff

        for b in pdict["data"]:
            checksum ^= b
        
        return checksum


    def get_dict(self) -> dict:
        """
        :return: Internal dict structure of the packet
        """
        return self.pdict


    def get_cmd_id(self) -> int:
        """
        :return: Command ID
        """
        return self.pdict["cmd"]
    

    def get_data(self) -> list:
        """
        :return: 8 data bytes
        """
        return self.pdict["data"]

    
    def get_from_to(self) -> tuple:
        """
        :return: Tuple in form (from, to)
        """
        return (self.pdict["from"], self.pdict["to"])
    

    def get_type(self) -> PacketType:
        """
        :return: Packet Type (PacketType Enum)
        """
        if self.pdict["type"] == "&":
            return PacketType.RESPONSE
        else:
            return PacketType.REQUEST
    

    def get_bytestream(self) -> bytes:
        """
        :return: Returns the parsed bytestream
        """
        return self.bytestring




###############################################
#                   Unittest                  #
###############################################

class packet_unittest(unittest.TestCase):
    
    test_bytestring = b"$01;00;4B;00000000*4C\r\n"

    def test_parse_without_error(self):
        p = Packet(self.test_bytestring)
        self.assertIsNotNone(p.get_dict())
    
    def test_parse_correct_dict(self):
        p = Packet(self.test_bytestring)

        self.assertDictEqual(p.get_dict(), {
         'checksum': 76, 
         'from': 0, 
         'data': [48, 48, 48, 48, 48, 48, 48, 48], 
         'to': 1, 
         'type': b'$', 
         'cmd': 75 })

    def test_parsed_bytestring(self):
        p = Packet(self.test_bytestring)
        self.assertEqual(self.test_bytestring, p.get_bytestream())


if __name__ == "__main__":
    unittest.main()