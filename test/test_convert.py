import unittest
from xcomfort.convert import Convert

class TestConvert(unittest.TestCase):
    def test_bytesToInt(self):
        data = bytearray(b'\xc5\xc4\x55\x00')
        ints = Convert.bytesToInt(data)
        self.assertEqual(5620933, ints)

    def test_bytesToDecimal(self):
        data = bytearray(b'\xd5')
        ints = Convert.bytesToDecimal(data)
        self.assertEqual(21.3, ints)
