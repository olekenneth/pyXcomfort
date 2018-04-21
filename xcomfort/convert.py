class Convert:
    @staticmethod
    def intToBytes(number, byteorder='big', length=None):
        return (number).to_bytes(length or round(len(str(number)) / 2), byteorder=byteorder)

    @staticmethod
    def bytesToInt(bytes, byteorder='big'):
        bytesCopy = bytes.copy()
        bytesCopy.reverse()
        return int.from_bytes(bytesCopy, byteorder=byteorder)

    @staticmethod
    def bytesToHex(bytes, byteorder='big'):
        return hex(Convert.bytesToInt(bytes, byteorder=byteorder))

    @staticmethod
    def bytesToDecimal(bytes, byteorder='big'):
        int = Convert.bytesToInt(bytes, byteorder=byteorder)
        return int / 10
