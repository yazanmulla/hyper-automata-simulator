import unittest
from src.parser import parse_nfh_from_text
from src.base import NFH

class TestParser(unittest.TestCase):
    def test_valid_parsing_simple(self):
        text = """
        k: 1
        alpha: E
        states: q0 q1
        initial: q0
        accepting: q1
        alphabet: a b
        delta:
        q0 a q1
        """
        nfh = parse_nfh_from_text(text)
        self.assertEqual(nfh.k, 1)
        self.assertEqual(nfh.states, {'q0', 'q1'})
        self.assertEqual(nfh.initial_states, {'q0'})
        self.assertEqual(nfh.accepting_states, {'q1'})
        self.assertEqual(nfh.alphabet, {'a', 'b'})
        self.assertEqual(len(nfh.delta), 1)
        self.assertIn(('q0', ('a',), 'q1'), nfh.delta)

    def test_valid_parsing_commas(self):
        text = """
        k: 2
        alpha: A, E
        states: q0, q1, q2
        initial: q0
        accepting: q2
        alphabet: 0, 1
        delta:
        q0, 0, 1, q1
        q1, 1, 1, q2
        """
        nfh = parse_nfh_from_text(text)
        self.assertEqual(nfh.k, 2)
        self.assertEqual(nfh.alpha, ['A', 'E'])
        self.assertEqual(str(nfh.delta), str({('q0', ('0', '1'), 'q1'), ('q1', ('1', '1'), 'q2')})) # str comparison for set ordering issue handling if any

    def test_missing_field(self):
        text = """
        k: 1
        states: q0
        """
        with self.assertRaises(ValueError):
            parse_nfh_from_text(text)

    def test_invalid_delta_format(self):
        text = """
        k: 2
        alpha: E E
        states: q0
        initial: q0
        accepting: q0
        alphabet: a
        delta:
        q0 a q0
        """ # Missing one symbol for k=2
        with self.assertRaises(ValueError):
            parse_nfh_from_text(text)

    def test_overlapping_names(self):
        text = """
        k: 1
        alpha: E
        states: a b
        initial: a
        accepting: b
        alphabet: a b
        delta:
        a a b
        b a a
        """
        nfh = parse_nfh_from_text(text)
        self.assertEqual(nfh.states, {'a', 'b'})
        self.assertIn(('a', ('a',), 'b'), nfh.delta)
        self.assertIn(('b', ('a',), 'a'), nfh.delta)

if __name__ == '__main__':
    unittest.main()
