"""Register map definitions for THZ readings (firmware 5.39).

This module provides the REGISTER_MAP dictionary containing sensor register definitions
specific to firmware version 5.39 in the format expected by RegisterMapManager.

Each block key (e.g., "pxx0A033B") maps to a list of tuples defining sensors:
    (name, offset, length, decode_type, factor)

Where:
    - name: Sensor name (string with trailing colon)
    - offset: Byte offset in the response data
    - length: Number of hex characters (2 per byte)
    - decode_type: Decoding function identifier
    - factor: Scaling factor for the value
"""

REGISTER_MAP = {
    "firmware": "539",
    # Flow and measurement sensors
    "pxx0A033B": [
        ("sFlowRate:", 8, 4, "hex2int", 1),
    ],
    "pxx0A064F": [
        ("sHumMaskingTime:", 8, 4, "hex2int", 1),
    ],
    "pxx0A0650": [
        ("sHumThreshold:", 8, 4, "hex2int", 1),
    ],
    "pxx0A069A": [
        ("sHeatingRelPower:", 8, 4, "hex2int", 1),
    ],
    "pxx0A069B": [
        ("sComprRelPower:", 8, 4, "hex2int", 1),
    ],
    "pxx0A069C": [
        ("sComprRotUnlimit:", 8, 4, "hex2int", 1),
    ],
    "pxx0A069D": [
        ("sComprRotLimit:", 8, 4, "hex2int", 1),
    ],
    "pxx0A06A4": [
        ("sOutputReduction:", 8, 4, "hex2int", 1),
    ],
    "pxx0A06A5": [
        ("sOutputIncrease:", 8, 4, "hex2int", 1),
    ],
    "pxx0A09D1": [
        ("sHumProtection:", 8, 4, "hex2int", 1),
    ],
    "pxx0A09D2": [
        ("sSetHumidityMin:", 8, 4, "hex2int", 1),
    ],
    "pxx0A09D3": [
        ("sSetHumidityMax:", 8, 4, "hex2int", 1),
    ],
    "pxx0A0648": [
        ("sCoolHCTotal:", 8, 4, "hex2int", 1),
    ],
    # Temperature sensors (dew point)
    "pxx0B0264": [
        ("sDewPointHC1:", 8, 4, "hex2int", 10),
    ],
    "pxx0C0264": [
        ("sDewPointHC2:", 8, 4, "hex2int", 10),
    ],
}
