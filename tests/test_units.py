import unittest
from collections import deque
from src.base import NFH
from src.run_manager import RunManager

class TestNFHValidationUnit(unittest.TestCase):
    def test_valid_init(self):
        NFH({'q0'}, {'q0'}, {'q0'}, 1, {('q0', ('a',), 'q0')}, ['E'], {'a'})

    def test_invalid_states_disjoint(self):
        with self.assertRaises(AssertionError):
            NFH({'q0'}, {'q1'}, {'q0'}, 1, set(), ['E'], {'a'})

    def test_invalid_accepting_disjoint(self):
        with self.assertRaises(AssertionError):
            NFH({'q0'}, {'q0'}, {'q1'}, 1, set(), ['E'], {'a'})

    def test_invalid_k_zero(self):
        with self.assertRaises(AssertionError):
            NFH({'q0'}, {'q0'}, {'q0'}, 0, set(), ['E'], {'a'})

    def test_invalid_k_negative(self):
        with self.assertRaises(AssertionError):
            NFH({'q0'}, {'q0'}, {'q0'}, -5, set(), ['E'], {'a'})

    def test_invalid_alpha_length_short(self):
        with self.assertRaises(AssertionError):
            NFH({'q0'}, {'q0'}, {'q0'}, 2, set(), ['E'], {'a'})

    def test_invalid_alpha_length_long(self):
        with self.assertRaises(AssertionError):
            NFH({'q0'}, {'q0'}, {'q0'}, 1, set(), ['E', 'E'], {'a'})

    def test_alpha_invalid_type_int(self):
         with self.assertRaises(AssertionError):
            NFH({'q0'}, {'q0'}, {'q0'}, 1, set(), [1], {'a'})

    def test_alpha_invalid_content(self):
        with self.assertRaises(AssertionError):
            NFH({'q0'}, {'q0'}, {'q0'}, 1, set(), ['Z'], {'a'})

    def test_empty_states(self):
        with self.assertRaises(AssertionError):
            NFH(set(), set(), set(), 1, set(), ['E'], {'a'})

    def test_initial_states_must_be_subset(self):
        with self.assertRaises(AssertionError):
            NFH({'q0'}, {'q1'}, {'q0'}, 1, set(), ['E'], {'a'})

    def test_accepting_states_must_be_subset(self):
        with self.assertRaises(AssertionError):
             NFH({'q0'}, {'q0'}, {'q2'}, 1, set(), ['E'], {'a'})

    def test_alphabet_empty(self):
        nfh = NFH({'q0'}, {'q0'}, {'q0'}, 1, set(), ['E'], set())
        self.assertIsInstance(nfh, NFH)

    def test_mix_types_in_states(self):
        pass

    def test_delta_not_set(self):
        delta = [('q0', ('a',), 'q0')]
        nfh = NFH({'q0'}, {'q0'}, {'q0'}, 1, delta, ['E'], {'a'})
        self.assertEqual(len(nfh.delta), 1)


class TestRunManagerInitUnit(unittest.TestCase):
    def setUp(self):
        self.nfh = NFH({'q0'}, {'q0'}, {'q0'}, 2, set(), ['E', 'E'], {'a', 'b'})

    def test_init_assignment_list(self):
        rm = RunManager(self.nfh, ['a', 'b'])
        # New RunManager stores assignment as tuple of strings/deques, we just check generic init success
        self.assertIsNotNone(rm.assignment)

    def test_init_assignment_len_short(self):
        with self.assertRaises(AssertionError):
            RunManager(self.nfh, ['a'])

    def test_init_assignment_len_long(self):
        with self.assertRaises(AssertionError):
            RunManager(self.nfh, ['a', 'b', 'c'])

    def test_init_invalid_start_state(self):
        with self.assertRaises(AssertionError):
            RunManager(self.nfh, ['a', 'b'], initial_state='z99')

    def test_init_defaults(self):
        rm = RunManager(self.nfh, ['a', 'b'])
        self.assertEqual(rm.timeout, 60)
        self.assertTrue(rm.enable_timeout)

    def test_init_custom_timeout(self):
        rm = RunManager(self.nfh, ['a', 'b'], timeout=10, enable_timeout=False)
        self.assertEqual(rm.timeout, 10)
        self.assertFalse(rm.enable_timeout)

    def test_init_negative_timeout(self):
        rm = RunManager(self.nfh, ['a', 'b'], timeout=-1)
        self.assertEqual(rm.timeout, -1)

    def test_init_zero_timeout(self):
        rm = RunManager(self.nfh, ['a', 'b'], timeout=0)
        self.assertEqual(rm.timeout, 0)
    
    def test_init_custom_initial_valid(self):
        rm = RunManager(self.nfh, ['a', 'b'], initial_state='q0')
        self.assertEqual(rm.initial_state, 'q0')


class TestExecutionUnit(unittest.TestCase):
    def test_simple_path_k1(self):
        nfh = NFH({'q0', 'q1'}, {'q0'}, {'q1'}, 1, {('q0', ('a',), 'q1')}, ['E'], {'a'})
        rm = RunManager(nfh, ['a'])
        self.assertTrue(rm.run())

    def test_simple_path_k1_fail(self):
        nfh = NFH({'q0', 'q1'}, {'q0'}, {'q1'}, 1, {('q0', ('b',), 'q1')}, ['E'], {'a', 'b'})
        rm = RunManager(nfh, ['a'])
        self.assertFalse(rm.run())

    def test_deadlock_start(self):
        nfh = NFH({'q0'}, {'q0'}, {'q0'}, 1, set(), ['E'], {'a'})
        rm = RunManager(nfh, ['a']) 
        self.assertFalse(rm.run())

    def test_deadlock_middle(self):
        nfh = NFH({'q0', 'q1', 'q2'}, {'q0'}, {'q2'}, 1, {('q0', ('a',), 'q1')}, ['E'], {'a'})
        rm = RunManager(nfh, ['ab'])
        self.assertFalse(rm.run())

    def test_cycle_success(self):
        # q0 -a-> q0 -b-> q1
        delta = {('q0', ('a',), 'q0'), ('q0', ('b',), 'q1')}
        nfh = NFH({'q0', 'q1'}, {'q0'}, {'q1'}, 1, delta, ['E'], {'a', 'b'})
        rm = RunManager(nfh, ['aaab'])
        self.assertTrue(rm.run())

    def test_cycle_fail(self):
        # q0 -a-> q0
        delta = {('q0', ('a',), 'q0')}
        nfh = NFH({'q0', 'q1'}, {'q0'}, {'q1'}, 1, delta, ['E'], {'a'})
        rm = RunManager(nfh, ['aaaa'])
        self.assertFalse(rm.run())

    def test_branch_simple(self):
        # q0 -a-> q1 (fail), q0 -a-> q2 (acc)
        delta = {('q0', ('a',), 'q1'), ('q0', ('a',), 'q2')}
        nfh = NFH({'q0', 'q1', 'q2'}, {'q0'}, {'q2'}, 1, delta, ['E'], {'a'})
        rm = RunManager(nfh, ['a'])
        self.assertTrue(rm.run())

    def test_branch_all_fail(self):
        delta = {('q0', ('a',), 'q1'), ('q0', ('a',), 'q2')}
        nfh = NFH({'q0', 'q1', 'q2', 'q3'}, {'q0'}, {'q3'}, 1, delta, ['E'], {'a'})
        rm = RunManager(nfh, ['a'])
        self.assertFalse(rm.run())

    def test_k3_sync_success(self):
        delta = {('q0', ('a', 'b', 'c'), 'q1')}
        nfh = NFH({'q0', 'q1'}, {'q0'}, {'q1'}, 3, delta, ['E']*3, {'a', 'b', 'c'})
        rm = RunManager(nfh, ['a', 'b', 'c'])
        self.assertTrue(rm.run())

    def test_k3_partial_fail(self):
        delta = {('q0', ('a', 'b', 'c'), 'q1')}
        nfh = NFH({'q0', 'q1'}, {'q0'}, {'q1'}, 3, delta, ['E']*3, {'a', 'b', 'c'})
        rm = RunManager(nfh, ['a', 'b', 'x'])
        self.assertFalse(rm.run())

    def test_deep_path(self):
        # Chain 20 states
        N = 20
        delta = {(f'q{i}', ('a',), f'q{i+1}') for i in range(N)}
        states = {f'q{i}' for i in range(N+1)}
        nfh = NFH(states, {'q0'}, {f'q{N}'}, 1, delta, ['E'], {'a'})
        rm = RunManager(nfh, ['a'*N])
        self.assertTrue(rm.run())

    def test_leftover_buffer_rejects(self):
        nfh = NFH({'q0', 'q1'}, {'q0'}, {'q1'}, 1, {('q0', ('a',), 'q1')}, ['E'], {'a'})
        rm = RunManager(nfh, ['aa'])
        self.assertFalse(rm.run())

    def test_buffer_consumption_check(self):
        # q0 -a-> q1 -b-> q2. In 'ba' -> fail match
        delta = {('q0', ('a',), 'q1'), ('q1', ('b',), 'q2')}
        nfh = NFH({'q0', 'q1', 'q2'}, {'q0'}, {'q2'}, 1, delta, ['E'], {'a', 'b'})
        rm = RunManager(nfh, ['ba'])
        self.assertFalse(rm.run())

    def test_empty_input_success(self):
        nfh = NFH({'q0'}, {'q0'}, {'q0'}, 1, set(), ['E'], {})
        rm = RunManager(nfh, [''])
        # q0 is accepting, input is empty. Should accept directly.
        self.assertTrue(rm.run())

    def test_empty_input_fail(self):
        nfh = NFH({'q0', 'q1'}, {'q0'}, {'q1'}, 1, set(), ['E'], {})
        rm = RunManager(nfh, [''])
        # q0 is not accepting. No moves.
        self.assertFalse(rm.run())

    def test_chained_epsilon(self):
        # q0 -#-> q1 -#-> q2 (acc)
        delta = {('q0', ('#',), 'q1'), ('q1', ('#',), 'q2')}
        nfh = NFH({'q0', 'q1', 'q2'}, {'q0'}, {'q2'}, 1, delta, ['E'], {'a'})
        rm = RunManager(nfh, [''])
        self.assertTrue(rm.run())

    def test_epsilon_mixed_chain(self):
        # q0 -#-> q1 -a-> q2 (acc)
        delta = {('q0', ('#',), 'q1'), ('q1', ('a',), 'q2')}
        nfh = NFH({'q0', 'q1', 'q2'}, {'q0'}, {'q2'}, 1, delta, ['E'], {'a'})
        rm = RunManager(nfh, ['a'])
        self.assertTrue(rm.run())

    def test_backtracking_correctness(self):
        # q0 -a-> q1 (dead)
        # q0 -a-> q2 -b-> q3 (acc)
        delta = {('q0', ('a',), 'q1'), ('q0', ('a',), 'q2'), ('q2', ('b',), 'q3')}
        nfh = NFH({'q0', 'q1', 'q2', 'q3'}, {'q0'}, {'q3'}, 1, delta, ['E'], {'a', 'b'})
        rm = RunManager(nfh, ['ab'])
        self.assertTrue(rm.run())
        if rm.run_history:
             self.assertEqual(rm.run_history[-1][2], 'q3')

    def test_stack_depth_limit_implicit(self):
        # Standard python recursion limit is 1000. 200 should be fine.
        N = 200
        delta = {(f'q{i}', ('a',), f'q{i+1}') for i in range(N)}
        states = {f'q{i}' for i in range(N+1)}
        nfh = NFH(states, {'q0'}, {f'q{N}'}, 1, delta, ['E'], {'a'})
        rm = RunManager(nfh, ['a'*N])
        self.assertTrue(rm.run())

    def test_complex_branching_tree(self):
        # q0 -> q1, q2
        # q1 -> q3, q4
        # q2 -> q5, q6 (acc)
        delta = {
            ('q0', ('a',), 'q1'), ('q0', ('a',), 'q2'),
            ('q1', ('a',), 'q3'), ('q1', ('a',), 'q4'),
            ('q2', ('a',), 'q5'), ('q2', ('a',), 'q6')
        }
        states = {'q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6'}
        nfh = NFH(states, {'q0'}, {'q6'}, 1, delta, ['E'], {'a'})
        rm = RunManager(nfh, ['aa'])
        self.assertTrue(rm.run())
        if rm.run_history:
             self.assertEqual(rm.run_history[-1][2], 'q6')

    def test_cycle_with_exit(self):
        # q0 -a-> q0, q0 -b-> q1 (acc)
        delta = {('q0', ('a',), 'q0'), ('q0', ('b',), 'q1')}
        nfh = NFH({'q0', 'q1'}, {'q0'}, {'q1'}, 1, delta, ['E'], {'a', 'b'})
        rm = RunManager(nfh, ['aaaab'])
        self.assertTrue(rm.run())


class TestTimeoutUnit(unittest.TestCase):
    def test_timeout_triggered(self):
        # Infinite loop
        delta = {('q0', ('#',), 'q0')}
        nfh = NFH({'q0', 'q1'}, {'q0'}, {'q1'}, 1, delta, ['E'], {'a'}) 
        rm = RunManager(nfh, [''], timeout=0.05)
        # Should return False eventually
        self.assertFalse(rm.run())

    def test_disabled_timeout_success(self):
        # Very short timeout param but disabled -> should run longer if needed
        # We need a long enough run that would fail if timeout was 1e-8
        N = 500
        delta = {(f'q{i}', ('a',), f'q{i+1}') for i in range(N)}
        states = {f'q{i}' for i in range(N+1)}
        nfh = NFH(states, {'q0'}, {f'q{N}'}, 1, delta, ['E'], {'a'})
        
        # Actually checking time is flaky. Just ensure it succeeds.
        rm = RunManager(nfh, ['a'*N], timeout=0.00000001, enable_timeout=False)
        self.assertTrue(rm.run())

    def test_negative_timeout_immediate_stop(self):
        # If timeout is checked at start of recursion
        delta = {('q0', ('a',), 'q1')}
        nfh = NFH({'q0', 'q1'}, {'q0'}, {'q1'}, 1, delta, ['E'], {'a'})
        rm = RunManager(nfh, ['a'], timeout=-1.0)
        self.assertFalse(rm.run())


class TestAcceptanceUnit(unittest.TestCase):
    def test_accepts_empty(self):
        nfh = NFH({'q0'}, {'q0'}, {'q0'}, 1, set(), ['E'], {})
        rm = RunManager(nfh, [''])
        self.assertTrue(rm.run())

    def test_rejects_non_empty(self):
        nfh = NFH({'q0'}, {'q0'}, {'q0'}, 1, set(), ['E'], {'a'})
        rm = RunManager(nfh, ['a'])
        self.assertFalse(rm.run())

    def test_rejects_wrong_state(self):
        nfh = NFH({'q0', 'q1'}, {'q0'}, {'q1'}, 1, set(), ['E'], {})
        rm = RunManager(nfh, [''])
        self.assertFalse(rm.run())

    def test_k_multi_empty(self):
        nfh = NFH({'q0'}, {'q0'}, {'q0'}, 3, set(), ['E']*3, {})
        rm = RunManager(nfh, ['', '', ''])
        self.assertTrue(rm.run())

    def test_k_multi_mixed(self):
        nfh = NFH({'q0'}, {'q0'}, {'q0'}, 2, set(), ['E']*2, {})
        rm = RunManager(nfh, ['a', ''])
        self.assertFalse(rm.run())

    def test_k_multi_mixed_2(self):
        rm = RunManager(NFH({'q0'}, {'q0'}, {'q0'}, 2, set(), ['E']*2, {}), ['', 'b'])
        self.assertFalse(rm.run())

if __name__ == '__main__':
    unittest.main()
