import unittest
from src.base import NFH, Hyperword
from src.simulator import checkMembership

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
        result, _ = checkMembership(nfh, S)
        self.assertTrue(result)
        
        # Hyperword with only 'a'
        S_bad = Hyperword({'a'})
        # Cannot pick y='b'. Should be false.
        result_bad, _ = checkMembership(nfh, S_bad)
        self.assertFalse(result_bad)

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
        result, _ = checkMembership(nfh, Hyperword({'a'}))
        self.assertTrue(result)
        
        # S = {'a', 'b'} -> Pairs: (a,a), (b,b), (a,b), (b,a).
        # (a,b) and (b,a) have no transitions -> Reject.
        # So ForAll should return False.
        result, _ = checkMembership(nfh, Hyperword({'a', 'b'}))
        self.assertFalse(result)

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
        result, _ = checkMembership(nfh, S)
        self.assertTrue(result)
        
        # If we remove 'a' from the RHS options?
        # Say we only accept (a,b) and (b,b).
        # If S only has 'a', then for x='a', we need y='b' (not in S) or y='a' (rejects).
        # Wait, y must be in S.
        
        # Case: S={'a'}. Transitions: (a,b) -> Acc.
        # For x='a', we need y in S s.t. (a,y) accepts.
        # y can only be 'a'. (a,a) rejects. So False.
        result, _ = checkMembership(nfh, Hyperword({'a'}))
        self.assertFalse(result)



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
        
        result, _ = checkMembership(nfh, Hyperword({'a'}))
        self.assertFalse(result)

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
        result_e, _ = checkMembership(nfh_e, Hyperword(set()))
        self.assertFalse(result_e)
        
        # ForAll over empty set -> True
        nfh_a = NFH(states, initial_states, accepting_states, k, delta, ['A'], alphabet)
        result_a, _ = checkMembership(nfh_a, Hyperword(set()))
        self.assertTrue(result_a)

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
        result, _ = checkMembership(nfh_ae, Hyperword({'a', 'b'}))
        self.assertTrue(result)
        
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
        result, _ = checkMembership(nfh_ae_2, Hyperword({'a', 'b'}))
        self.assertTrue(result)
        
        nfh_ea_2 = NFH(states, initial_states, accepting_states, k, delta_broken, ['E', 'A'], alphabet)
        result_2, _ = checkMembership(nfh_ea_2, Hyperword({'a', 'b'}))
        self.assertFalse(result_2)

    def test_forall_returns_multiple_runs(self):
        # A: ForAll x. x='a' or x='b'.
        # S = {'a', 'b'}
        # Should return 2 managers.
        states = {'q0', 'q1'}
        alphabet = {'a', 'b'}
        initial_states = {'q0'}
        accepting_states = {'q1'}
        k = 1
        delta = {
             ('q0', ('a',), 'q1'),
             ('q0', ('b',), 'q1')
        }
        alpha = ['A']
        nfh = NFH(states, initial_states, accepting_states, k, delta, alpha, alphabet)
        
        result, managers = checkMembership(nfh, Hyperword({'a', 'b'}))
        self.assertTrue(result)
        self.assertEqual(len(managers), 2)
        # Verify assignments
        assignments = {tuple(mgr.initial_assignment) for mgr in managers}
        self.assertIn(('a',), assignments)
        self.assertIn(('b',), assignments)

if __name__ == '__main__':
    unittest.main()
