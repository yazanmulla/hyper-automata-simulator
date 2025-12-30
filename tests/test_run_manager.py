from hyperautomata.base import NFH, RunManager
from collections import deque
import unittest

class TestRunManager(unittest.TestCase):
    def test_run_manager_steps(self):
        # Define a simple NFH
        states = {'q0', 'q1'}
        alphabet = {'a', 'b'}
        initial_states = {'q0'}
        accepting_states = {'q0'}
        k = 2
        
        # Transition: (q0, (a, b)) -> q0
        delta = {
            ('q0', ('a', 'b'), 'q0'),
            ('q0', ('b', 'a'), 'q1'), # q1 is sink/reject implicitly if not accepting or no transitions
        }
        
        quantification = ['A', 'A']
        
        nfh = NFH(states, initial_states, accepting_states, k, delta, quantification, alphabet)
        
        # Assignment: 1 -> 'a', 2 -> 'b'
        assignment = ['a', 'b']
        
        manager = RunManager(nfh, assignment)
        
        # Run should consume 'a', 'b' and reach q0 (accepting)
        result = manager.run()
        self.assertTrue(result)
        self.assertEqual(manager.current_state, 'q0') # Final state
        
        # Verify history
        self.assertEqual(len(manager.run_history), 1)
        step = manager.run_history[0]
        self.assertEqual(step[0], 'q0')
        self.assertEqual(step[1], ('a', 'b'))
        self.assertEqual(step[2], 'q0')
        
    def test_run_manager_reject(self):
        states = {'q0', 'q1'}
        alphabet = {'a', 'b'}
        initial_states = {'q0'}
        accepting_states = {'q0'}
        k = 2
        # (q0, (a, b)) -> q0. No transition for (b, a) from q0.
        delta = {
            ('q0', ('a', 'b'), 'q0'),
        }
        nfh = NFH(states, initial_states, accepting_states, k, delta, ['A', 'A'], alphabet)
        
        # Assignment: 1 -> 'b', 2 -> 'a'
        assignment = ['b', 'a']
        manager = RunManager(nfh, assignment)
        
        # Run: (b, a) mismatch with delta. Should return False
        result = manager.run()
        self.assertFalse(result)
        self.assertEqual(len(manager.run_history), 0)

    def test_run_manager_nondeterministic_branching(self):
        # Test Nondeterminism
        # q0 --(a,b)--> q1 (accepting)
        # q0 --(a,b)--> q2 (rejecting, stuck)
        
        states = {'q0', 'q1', 'q2'}
        alphabet = {'a', 'b'}
        initial_states = {'q0'}
        accepting_states = {'q1'}
        k = 2
        
        delta = {
            ('q0', ('a', 'b'), 'q1'),
            ('q0', ('a', 'b'), 'q2'),
        }
        
        nfh = NFH(states, initial_states, accepting_states, k, delta, ['E', 'E'], alphabet)
        assignment = ['a', 'b']
        
        manager = RunManager(nfh, assignment)
        
        # Should succeed because one branch leads to q1
        result = manager.run()
        self.assertTrue(result)
        
    def test_run_manager_k1(self):
        # Test k=1 simple automaton
        # q0 - (a) -> q1 (accepting)
        states = {'q0', 'q1'}
        alphabet = {'a'}
        initial_states = {'q0'}
        accepting_states = {'q1'}
        k = 1
        delta = { ('q0', ('a',), 'q1') }
        alpha = ['E']
        
        nfh = NFH(states, initial_states, accepting_states, k, delta, alpha, alphabet)
        manager = RunManager(nfh, ['a'])
        
        self.assertTrue(manager.run())
        self.assertEqual(len(manager.run_history), 1)
        self.assertEqual(manager.run_history[0][1], ('a',))

    def test_run_manager_k3_synchronous(self):
        # Test k=3
        # q0 - (a,b,c) -> q0 
        # q0 - (#,#,#) -> q1 (accepting)
        states = {'q0', 'q1'}
        alphabet = {'a', 'b', 'c'}
        initial_states = {'q0'}
        accepting_states = {'q1'}
        k = 3
        delta = { 
            ('q0', ('a', 'b', 'c'), 'q0'),
            ('q0', ('#', '#', '#'), 'q1')
        }
        alpha = ['E', 'E', 'E']
        
        nfh = NFH(states, initial_states, accepting_states, k, delta, alpha, alphabet)
        manager = RunManager(nfh, ['a', 'b', 'c'])
        
        # Step 1: consume (a,b,c) -> q0
        # Step 2: consume (#,#,#) -> q1 (buffers empty)
        # Should accept.
        
        self.assertTrue(manager.run())
        self.assertEqual(len(manager.run_history), 2)
        self.assertEqual(manager.run_history[0][2], 'q0')
        self.assertEqual(manager.run_history[1][2], 'q1')

    def test_run_manager_padding_behavior(self):
        # Input 1: "aa", Input 2: "a"
        # Transition requires (a,a) then (a,#)
        states = {'q0', 'q1', 'q2'}
        alphabet = {'a'}
        initial_states = {'q0'}
        accepting_states = {'q2'}
        k = 2
        delta = {
            ('q0', ('a', 'a'), 'q1'),
            ('q1', ('a', '#'), 'q2')
        }
        alpha = ['E', 'E']
        nfh = NFH(states, initial_states, accepting_states, k, delta, alpha, alphabet)
        
        manager = RunManager(nfh, ['aa', 'a'])
        self.assertTrue(manager.run())
        self.assertEqual(len(manager.run_history), 2)
        self.assertEqual(manager.run_history[1][1], ('a', '#'))

    def test_run_manager_deadlock(self):
        # Input available but no transition matches
        states = {'q0', 'q1'}
        alphabet = {'a'}
        initial_states = {'q0'}
        accepting_states = {'q1'}
        k = 1
        delta = set() # No transitions -> Deadlock immediately
        alpha = ['E']
        nfh = NFH(states, initial_states, accepting_states, k, delta, alpha, alphabet)
        
        manager = RunManager(nfh, ['a']) # Has a
        self.assertFalse(manager.run())
        self.assertEqual(len(manager.run_history), 0)

if __name__ == '__main__':
    unittest.main()
