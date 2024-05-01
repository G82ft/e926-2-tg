from unittest import TestCase


class Anything:
    def __eq__(self, _):
        return True


class Test(TestCase):
    def test_anything(self):
        self.assertTrue(1 == Anything())
        self.assertTrue(Anything() == 1)
