import struct
from canlib import canlib, Frame
from canlib.canlib import ChannelData

def setUpChannel(channel=0,
                 openFlags=canlib.Open.ACCEPT_VIRTUAL,
                 outputControl=canlib.Driver.NORMAL):
    ch = canlib.openChannel(channel, openFlags, bitrate=canlib.Bitrate.BITRATE_250K)
    print("Using channel: %s, EAN: %s" % (ChannelData(channel).channel_name,
                                          ChannelData(channel).card_upc_no))
    ch.setBusOutputControl(outputControl)
    ch.busOn()
    return ch


def tearDownChannel(ch):
    ch.busOff()
    ch.close()

def sendParameterChange(ch: canlib.Channel, param_id: int, value:int, write=False):
    if param_id < 15 and param_id != 11 and value < (1 << 32):
        param_id = param_id | (int(write) << 15)
        data = struct.pack("<IHH",value, param_id, 0x00)

        ch.write(Frame(0x106, data))
    else:
        print("Invalid Parameter ID or Value")

def requestParameterValue(ch: canlib.Channel, param_id: int):
    assert param_id < 15, "Invalid Parameter ID"
    assert param_id != 11, "Invalid Parameter ID"
    data = struct.pack("<H", param_id)

    ch.write(Frame(id_=0x107, data=data))