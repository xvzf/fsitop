# Sitop Solar Inverter Protocol based on Reverse Engineering

## Interface Description

- The inverter uses a RS232 interface with 9600 BAUD.

## Communication

- The general packet construction is `TYPE;TO;FROM;CMD;DATA*CHECKSUM`
- The inverter reacts to a response only when it is awake (if the sun is shining and the panels produce enought energy)

| TYPE | TO | FROM | CMD | DATA | CHECKSUM  |
|---|---|---|---|---|---|
| ´$´ for a request ; ´&´ for a response  | ID of sender in HEX value | ID of receiver in HEX value | Command ID in HEX value | 8 data bytes NOT in HEX value | Checksum, see below |

### Checksum calculation

The checksum is calculated by adding the value of TO, FROM and CMD together and modulo it by 255 (or `0xFF` in HEX form).
After that, every data byte is xored to the checksum, here a sample python code:

    checksum = 0

    for key in ["to", "from", "cmd"]:
        checksum = (checksum + pdict[key]) % 0xff

    for b in pdict["data"]:
        checksum ^= b

    return checksum

## Available commands

- @TODO