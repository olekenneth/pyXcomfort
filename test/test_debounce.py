import unittest
from xcomfort.debounce import debounce

class TestDebounce(unittest.TestCase):

    def test_debounce(self):
        @debounce(1)
        def myprint(message):
            print(message)

        myprint('message 1')
        myprint('message 2')
        myprint('message 3')
        myprint('message 4')
        myprint('message 5')
        myprint('message 6')
        myprint('message 7')

    def test_debounceNow(self):
        @debounce(0)
        def myprint(message):
            print(message)

        myprint('message 1')
