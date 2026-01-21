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

def sendParameterChange(param_id: int, value:int, write=False):
    assert param_id < 15, "Invalid Parameter ID"
    assert param_id != 11, "Invalid Parameter ID"
    assert value < (1 << 32), "Value too big"
    param_id = param_id | (int(write) << 15)
    data = struct.pack(">IHH",value, param_id, 0x00)