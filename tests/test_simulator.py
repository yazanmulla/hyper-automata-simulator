import unittest
from hyperautomata.base import NFH, Hyperword
from simulator import checkMembership

class TestCheckMembership(unittest.TestCase):
    def test_exists_exists(self):
        # A: Exists x, Exists y. x = 'a', y = 'b'
        # S = {'a', 'b'}
        # q0 - (a,b) -> q1 (accepting)
        
        states = {'q0', 'q1'}
        alphabet = {'a', 'b'}
        initial_states = {'q0'}
        accepting_states = {'q1'}
        k = 2
        
        delta = {
            ('q0', ('a', 'b'), 'q1')
        }
        
        # Two exists
        alpha = ['E', 'E']
        
        nfh = NFH(states, initial_states, accepting_states, k, delta, alpha, alphabet)
        
        # Hyperword with a and b
        S = Hyperword({'a', 'b'})
        
        # Should be true: we can pick x='a', y='b'
        self.assertTrue(checkMembership(nfh, S))
        
        # Hyperword with only 'a'
        S_bad = Hyperword({'a'})
        # Cannot pick y='b'. Should be false.
        self.assertFalse(checkMembership(nfh, S_bad))

    def test_forall_forall(self):
        # A: ForAll x, ForAll y. x=y
        # Logic: Accept if input is (a,a) or (b,b) or (empty, empty) etc.
        # But let's simplify.
        # q0 - (a,a) -> q0 (accepting)
        # q0 - (b,b) -> q0 (accepting)
        # If we see (a,b) -> reject.
        
        states = {'q0'}
        alphabet = {'a', 'b'}
        initial_states = {'q0'}
        accepting_states = {'q0'}
        k = 2
        
        delta = {
            ('q0', ('a', 'a'), 'q0'),
            ('q0', ('b', 'b'), 'q0')
        }
        
        alpha = ['A', 'A']
        nfh = NFH(states, initial_states, accepting_states, k, delta, alpha, alphabet)
        
        # S = {'a'} -> Pairs: (a,a). Accepted.
        self.assertTrue(checkMembership(nfh, Hyperword({'a'})))
        
        # S = {'a', 'b'} -> Pairs: (a,a), (b,b), (a,b), (b,a).
        # (a,b) and (b,a) have no transitions -> Reject.
        # So ForAll should return False.
        self.assertFalse(checkMembership(nfh, Hyperword({'a', 'b'})))

    def test_forall_exists(self):
        # "For every x, there exists y such that ..."
        # S = {'a', 'b'}
        # Require: (a, ?) is accepted AND (b, ?) is accepted.
        # Let's say we accept (a,a) and (b,a).
        # Then for x=a, y=a works.
        # For x=b, y=a works.
        
        states = {'q0', 'q1'}
        alphabet = {'a', 'b'}
        initial_states = {'q0'}
        accepting_states = {'q1'}
        k = 2
        
        delta = {
            ('q0', ('a', 'b'), 'q1'),
            ('q0', ('b', 'a'), 'q1')
        }
        
        alpha = ['A', 'E']
        nfh = NFH(states, initial_states, accepting_states, k, delta, alpha, alphabet)
        
        S = Hyperword({'a', 'b'})
        self.assertTrue(checkMembership(nfh, S))
        
        # If we remove 'a' from the RHS options?
        # Say we only accept (a,b) and (b,b).
        # If S only has 'a', then for x='a', we need y='b' (not in S) or y='a' (rejects).
        # Wait, y must be in S.
        
        # Case: S={'a'}. Transitions: (a,b) -> Acc.
        # For x='a', we need y in S s.t. (a,y) accepts.
        # y can only be 'a'. (a,a) rejects. So False.
        self.assertFalse(checkMembership(nfh, Hyperword({'a'})))



    def test_exists_fail(self):
        # Exists x. x = 'b'. S={'a'}. Should fail.
        states = {'q0', 'q1'}
        alphabet = {'a', 'b'}
        initial_states = {'q0'}
        accepting_states = {'q1'}
        k = 1
        delta = { ('q0', ('b',), 'q1') }
        alpha = ['E']
        nfh = NFH(states, initial_states, accepting_states, k, delta, alpha, alphabet)
        
        self.assertFalse(checkMembership(nfh, Hyperword({'a'})))

    def test_empty_hyperword(self):
        # Test behavior on empty set
        states = {'q0'}
        alphabet = {'a'}
        initial_states = {'q0'}
        accepting_states = {'q0'}
        k = 1
        delta = set()
        
        # Exists over empty set -> False
        nfh_e = NFH(states, initial_states, accepting_states, k, delta, ['E'], alphabet)
        self.assertFalse(checkMembership(nfh_e, Hyperword(set())))
        
        # ForAll over empty set -> True
        nfh_a = NFH(states, initial_states, accepting_states, k, delta, ['A'], alphabet)
        self.assertTrue(checkMembership(nfh_a, Hyperword(set())))

    def test_alternation_AE_vs_EA(self):
        # Define a relation R(x,y).
        # Let S = {a, b}
        # R = {(a,a), (a,b)}. (All x have some y? Yes. x=a->a,b. x=b->None? No wait.)
        # Let's define:
        # q0 -(a,a)-> Acc
        # q0 -(a,b)-> Acc
        # q0 -(b,a)-> Acc
        # (b,b) is Reject.
        
        states = {'q0', 'q1'}
        alphabet = {'a', 'b'}
        initial_states = {'q0'}
        accepting_states = {'q1'}
        k = 2
        delta = {
            ('q0', ('a', 'a'), 'q1'),
            ('q0', ('a', 'b'), 'q1'),
            ('q0', ('b', 'a'), 'q1')
        }
        
        # Case 1: ForAll x, Exists y.
        # x=a. Needs y in {a,b}. (a,a) Acc, (a,b) Acc. OK.
        # x=b. Needs y in {a,b}. (b,a) Acc, (b,b) Rej. y=a works. OK.
        # So AE should be True.
        
        nfh_ae = NFH(states, initial_states, accepting_states, k, delta, ['A', 'E'], alphabet)
        self.assertTrue(checkMembership(nfh_ae, Hyperword({'a', 'b'})))
        
        # Case 2: Exists x, ForAll y.
        # Try x=a. For all y in {a,b}: (a,a) Acc, (a,b) Acc. OK.
        # So x=a is a witness. EA should be True.
        
        nfh_ea = NFH(states, initial_states, accepting_states, k, delta, ['E', 'A'], alphabet)
        self.assertTrue(checkMembership(nfh_ea, Hyperword({'a', 'b'})))
        
        # Modify to break EA but keep AE.
        # Remove (a,b) -> Acc.
        # New Delta: {(a,a), (b,a)}.
        # AE:
        # x=a -> y=a (a,a) OK.
        # x=b -> y=a (b,a) OK.
        # AE is True.
        
        # EA:
        # Try x=a. For y=b, (a,b) Rej. Fail.
        # Try x=b. For y=b, (b,b) Rej. Fail.
        # EA is False.
        
        delta_broken = {
            ('q0', ('a', 'a'), 'q1'),
            ('q0', ('b', 'a'), 'q1')
        }
        nfh_ae_2 = NFH(states, initial_states, accepting_states, k, delta_broken, ['A', 'E'], alphabet)
        self.assertTrue(checkMembership(nfh_ae_2, Hyperword({'a', 'b'})))
        
        nfh_ea_2 = NFH(states, initial_states, accepting_states, k, delta_broken, ['E', 'A'], alphabet)
        self.assertFalse(checkMembership(nfh_ea_2, Hyperword({'a', 'b'})))

if __name__ == '__main__':
    unittest.main()
