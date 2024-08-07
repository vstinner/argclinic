from argclinic.utils import hash_text
import unittest


class Tests(unittest.TestCase):
    def test_hash_text(self):
        self.assertEqual(hash_text(''), 'da39a3ee5e6b4b0d')
        self.assertEqual(hash_text('abc'), 'a9993e364706816a')
        self.assertEqual(hash_text('abc\ndef'), '6a07139fd8d155df')


if __name__ == "__main__":
    unittest.main()
