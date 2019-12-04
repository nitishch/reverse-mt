import unittest
import random


def invert1(y, shift):
    # Given y = x ^ (x >> shift), return x. y is a seq of bits
    x = y[:]
    for index in range(shift, len(y)):
        x[index] ^= x[index - shift]
    return x


def invert2(y, shift, b):
    # Given y = x ^ ((x << shift) & b), return x. y and b are
    # sequences of bits
    x = y[:]
    for i in range(shift + 1, len(y) + 1):
        x[-i] ^= x[shift - i] if b[-i] else 0
    return x


def detemper(z):
    # z is an int. return value is an int.

    # Convert integer to list of bits
    z = list(map(int, list("{:032b}".format(z))))
    l = 18
    u = 11
    s = 7
    t = 15
    b = list(map(int, bin(0x9D2C5680)[2:]))
    c = list(map(int, bin(0xEFC60000)[2:]))

    z = invert1(z, l)
    z = invert2(z, t, c)
    z = invert2(z, s, b)
    z = invert1(z, u)
    return int("".join(list(map(str, z))), 2)


def predict_next(old_values):
    """Given 624 past outputs of the RNG, return the next output"""
    assert len(old_values) == 624

    old_values = list(map(detemper, old_values))

    # Create a new RNG
    ro = random.Random()
    ro.setstate((3, tuple(old_values + [624]), None))
    # Since INDEX is set to 624, ro will use the state to calculate
    # the next random number
    return ro.getrandbits(32)


class Test(unittest.TestCase):
    def noinvert1(self, n, shift):
        """ Return n ^ (n >> shift)"""
        binary = self.int_to_binary(n)
        return list(map(lambda x, y: x ^ y, binary, [0] * shift + binary[:-shift]))

    def noinvert2(self, n, shift, b):
        """Return n ^ ((n << shift) & b)"""
        binary = self.int_to_binary(n)
        shifted = binary[shift:] + [0] * shift
        binaryb = self.int_to_binary(b)
        return list(
            map(lambda x, y: x ^ y, binary, map(lambda x, y: x & y, shifted, binaryb))
        )

    def int_to_binary(self, n):
        return list(map(int, list("{:032b}".format(n))))

    def binary_to_int(self, l):
        return int("".join(map(str, l)), 2)

    def test_invert1(self):
        self.assertEqual(self.binary_to_int(invert1(self.noinvert1(456, 3), 3)), 456)
        self.assertEqual(self.binary_to_int(invert1(self.noinvert1(456, 13), 13)), 456)

    def test_invert2(self):
        self.assertEqual(
            self.binary_to_int(
                invert2(
                    self.noinvert2(456, 13, 0x738292), 13, self.int_to_binary(0x738292)
                )
            ),
            456,
        )

    def test_prediction(self):
        ro = random.Random()

        # After a few calls to random
        for _ in range(ro.randint(0, 1000)):
            ro.random()

        output = [ro.getrandbits(32) for _ in range(624)]
        left = predict_next(output)
        right = ro.getrandbits(32)
        self.assertEqual(left, right)


unittest.main(exit=False)
