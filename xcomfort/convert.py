class Convert:
    @staticmethod
    def intToBytes(number, byteorder="big", length=None):
        return (number).to_bytes(
            length or round(len(str(number)) / 2), byteorder=byteorder
        )

    @staticmethod
    def bytesToInt(byte, byteorder="big"):
        bytesCopy = byte.copy()
        bytesCopy.reverse()
        return int.from_bytes(bytesCopy, byteorder=byteorder)

    @staticmethod
    def bytesToHex(byte, byteorder="big"):
        return hex(Convert.bytesToInt(byte, byteorder=byteorder))

    @staticmethod
    def bytesToDecimal(byte, byteorder="big"):
        integer = Convert.bytesToInt(byte, byteorder=byteorder)
        return integer / 10
