from PyCRC.CRC16Kermit import CRC16Kermit
from xcomfort.convert import Convert

class Crc:
    @staticmethod
    def calc(data):
        return CRC16Kermit().calculate(data)

    @staticmethod
    def generate(data):
        crcData = bytes(data[3:-3])
        crc = Crc.calc(crcData)
        data[-3:-1] = Convert.intToBytes(crc)
        return data
