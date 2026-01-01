import unittest
import time
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
        self.assertEqual(rm.variables['1'], deque(['a']))
        self.assertEqual(rm.variables['2'], deque(['b']))

    def test_init_assignment_tuple_fails(self):
        with self.assertRaises(ValueError):
            RunManager(self.nfh, ('a', 'b'))

    def test_init_assignment_dict_internal(self):
        vars_dict = {'1': deque(['a']), '2': deque(['b'])}
        rm = RunManager(self.nfh, vars_dict)
        self.assertEqual(rm.variables, vars_dict)

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

    def test_init_deep_copy_verify(self):
        inp = ['a', 'b']
        rm = RunManager(self.nfh, inp)
        inp[0] = 'z' 
        self.assertEqual(rm.variables['1'][0], 'a') 

    def test_init_variables_independence(self):
        inp = ['a', 'a']
        rm = RunManager(self.nfh, inp)
        rm.variables['1'].popleft()
        self.assertEqual(len(rm.variables['2']), 1) 

    def test_init_custom_initial_valid(self):
        rm = RunManager(self.nfh, ['a', 'b'], initial_state='q0')
        self.assertEqual(rm.current_state, 'q0')

    def test_init_k1_assignment(self):
        nfh1 = NFH({'q0'}, {'q0'}, {'q0'}, 1, set(), ['E'], {'a'})
        rm = RunManager(nfh1, ['abc'])
        self.assertEqual(list(rm.variables['1']), ['a', 'b', 'c'])

    def test_empty_assignment_strings(self):
        rm = RunManager(self.nfh, ['', ''])
        self.assertEqual(len(rm.variables['1']), 0)
        self.assertEqual(len(rm.variables['2']), 0)


class TestTransitionsUnit(unittest.TestCase):
    def setUp(self):
        # q0 --(a,b)--> q1
        # q0 --(a,a)--> q2
        # q0 --(#,b)--> q3
        # q0 --(#,#)--> q4
        # q0 --(b,#)--> q5
        delta = {
            ('q0', ('a', 'b'), 'q1'),
            ('q0', ('a', 'a'), 'q2'),
            ('q0', ('#', 'b'), 'q3'),
            ('q0', ('#', '#'), 'q4'),
            ('q0', ('b', '#'), 'q5')
        }
        self.nfh = NFH({'q0', 'q1', 'q2', 'q3', 'q4', 'q5'}, {'q0'}, {'q1'}, 2, delta, ['E', 'E'], {'a', 'b'})

    def test_match_exact(self):
        rm = RunManager(self.nfh, ['a', 'b'])
        valid = [t for t in rm.valid_transitions() if t[2] == 'q1']
        self.assertEqual(len(valid), 1)

    def test_match_partial_fail_1(self):
        rm = RunManager(self.nfh, ['a', 'c'])
        valid = [t for t in rm.valid_transitions() if t[2] == 'q1']
        self.assertEqual(len(valid), 0)

    def test_match_partial_fail_2(self):
        rm = RunManager(self.nfh, ['c', 'b'])
        valid = [t for t in rm.valid_transitions() if t[2] == 'q1']
        self.assertEqual(len(valid), 0)

    def test_match_epsilon_first(self):
        rm = RunManager(self.nfh, ['a', 'b'])
        valid = [t for t in rm.valid_transitions() if t[2] == 'q3']
        self.assertEqual(len(valid), 1)

    def test_match_epsilon_only_empty_buffer(self):
        pass

    def test_epsilon_matches_empty(self):
        rm = RunManager(self.nfh, ['', 'b'])
        valid = [t for t in rm.valid_transitions() if t[2] == 'q3']
        self.assertEqual(len(valid), 1)

    def test_double_epsilon(self):
        rm = RunManager(self.nfh, ['a', 'b'])
        valid = [t for t in rm.valid_transitions() if t[2] == 'q4']
        self.assertEqual(len(valid), 1)
        
        rm = RunManager(self.nfh, ['', ''])
        valid = [t for t in rm.valid_transitions() if t[2] == 'q4']
        self.assertEqual(len(valid), 1)

    def test_consume_logic_normal(self):
        rm = RunManager(self.nfh, ['a', 'b'])
        rm.move(('q0', ('a', 'b'), 'q1'))
        self.assertEqual(len(rm.variables['1']), 0)
        self.assertEqual(len(rm.variables['2']), 0)

    def test_consume_logic_epsilon_mixed(self):
        rm = RunManager(self.nfh, ['a', 'b'])
        rm.move(('q0', ('#', 'b'), 'q3'))
        self.assertEqual(len(rm.variables['1']), 1) # 'a' remains
        self.assertEqual(rm.variables['1'][0], 'a')
        self.assertEqual(len(rm.variables['2']), 0) # 'b' consumed

    def test_consume_logic_double_epsilon(self):
        rm = RunManager(self.nfh, ['a', 'b'])
        rm.move(('q0', ('#', '#'), 'q4'))
        self.assertEqual(len(rm.variables['1']), 1)
        self.assertEqual(len(rm.variables['2']), 1)

    def test_transition_invalid_dest(self):
        rm = RunManager(self.nfh, ['a', 'b'])
        valid = rm.valid_transitions()
        for t in valid:
            self.assertIn(t[2], {'q1', 'q2', 'q3', 'q4', 'q5'})

    def test_state_change(self):
        rm = RunManager(self.nfh, ['a', 'b'])
        rm.move(('q0', ('a', 'b'), 'q1'))
        self.assertEqual(rm.current_state, 'q1')

    def test_history_append(self):
        rm = RunManager(self.nfh, ['a', 'b'])
        rm.move(('q0', ('a', 'b'), 'q1'))
        self.assertEqual(len(rm.run_history), 1)
        self.assertEqual(rm.run_history[0], ('q0', ('a', 'b'), 'q1'))

    def test_symbol_not_in_alphabet(self):
        pass

    def test_empty_input_fails_non_epsilon(self):
        rm = RunManager(self.nfh, ['', ''])
        valid = [t for t in rm.valid_transitions() if t[2] == 'q1']
        self.assertEqual(len(valid), 0)

    def test_short_input_fails_match(self):
        rm = RunManager(self.nfh, ['a', ''])
        valid = [t for t in rm.valid_transitions() if t[2] == 'q1']
        self.assertEqual(len(valid), 0)

    def test_mixed_epsilon_2(self):
        rm = RunManager(self.nfh, ['b', 'a'])
        valid = [t for t in rm.valid_transitions() if t[2] == 'q5']
        self.assertEqual(len(valid), 1)


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

    def test_timeout_pruning_finite_wins(self):
        # Branch 1: infinite loop. Branch 2: success.
        delta = {('q0', ('#',), 'q0'), ('q0', ('a',), 'q1')}
        nfh = NFH({'q0', 'q1'}, {'q0'}, {'q1'}, 1, delta, ['E'], {'a'})
        
        rm = RunManager(nfh, ['a'], timeout=0.05)
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
        self.assertTrue(rm.run())

    def test_empty_input_fail(self):
        nfh = NFH({'q0', 'q1'}, {'q0'}, {'q1'}, 1, set(), ['E'], {})
        rm = RunManager(nfh, [''])
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
        self.assertEqual(rm.run_history[-1][2], 'q3')

    def test_stack_depth_limit_implicit(self):
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
        start = time.time()
        self.assertFalse(rm.run())
        self.assertGreater(time.time() - start, 0.05)

    def test_timeout_propagation(self):
        pass

    def test_disabled_timeout_success(self):
        # Very short timeout param but disabled -> should run longer
        N = 1000
        delta = {(f'q{i}', ('a',), f'q{i+1}') for i in range(N)}
        states = {f'q{i}' for i in range(N+1)}
        nfh = NFH(states, {'q0'}, {f'q{N}'}, 1, delta, ['E'], {'a'})
        
        rm = RunManager(nfh, ['a'*N], timeout=0.00000001, enable_timeout=False)
        self.assertTrue(rm.run())

    def test_zero_timeout_immediate_stop(self):
        delta = {('q0', ('a',), 'q1')}
        nfh = NFH({'q0', 'q1'}, {'q0'}, {'q1'}, 1, delta, ['E'], {'a'})
        rm = RunManager(nfh, ['a'], timeout=0.0) 
        pass

    def test_long_timeout_4s(self):
        delta = {('q0', ('#',), 'q0')}
        nfh = NFH({'q0', 'q1'}, {'q0'}, {'q1'}, 1, delta, ['E'], {'a'})
        rm = RunManager(nfh, [''], timeout=4.0)
        start = time.time()
        self.assertFalse(rm.run())
        self.assertGreater(time.time() - start, 4.0)

    def test_negative_timeout_immediate_stop(self):
        delta = {('q0', ('a',), 'q1')}
        nfh = NFH({'q0', 'q1'}, {'q0'}, {'q1'}, 1, delta, ['E'], {'a'})
        rm = RunManager(nfh, ['a'], timeout=-1.0)
        self.assertFalse(rm.run())


class TestAcceptanceUnit(unittest.TestCase):
    def test_accepts_empty(self):
        nfh = NFH({'q0'}, {'q0'}, {'q0'}, 1, set(), ['E'], {})
        rm = RunManager(nfh, [''])
        self.assertTrue(rm.acceptingState())

    def test_rejects_non_empty(self):
        nfh = NFH({'q0'}, {'q0'}, {'q0'}, 1, set(), ['E'], {'a'})
        rm = RunManager(nfh, ['a'])
        self.assertFalse(rm.acceptingState())

    def test_rejects_wrong_state(self):
        nfh = NFH({'q0', 'q1'}, {'q0'}, {'q1'}, 1, set(), ['E'], {})
        rm = RunManager(nfh, [''])
        self.assertFalse(rm.acceptingState())

    def test_k_multi_empty(self):
        nfh = NFH({'q0'}, {'q0'}, {'q0'}, 3, set(), ['E']*3, {})
        rm = RunManager(nfh, ['', '', ''])
        self.assertTrue(rm.acceptingState())

    def test_k_multi_mixed(self):
        nfh = NFH({'q0'}, {'q0'}, {'q0'}, 2, set(), ['E']*2, {})
        rm = RunManager(nfh, ['a', ''])
        self.assertFalse(rm.acceptingState())

    def test_k_multi_mixed_2(self):
        rm = RunManager(NFH({'q0'}, {'q0'}, {'q0'}, 2, set(), ['E']*2, {}), ['', 'b'])
        self.assertFalse(rm.acceptingState())

if __name__ == '__main__':
    unittest.main()
