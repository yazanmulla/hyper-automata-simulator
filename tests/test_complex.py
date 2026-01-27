import unittest
from src.base import NFH, Hyperword
from src.run_manager import RunManager
from src.simulator import checkMembership

class TestComplexScenarios(unittest.TestCase):

    def test_pattern_matching_deep_nondeterminism(self):
        """
        Scenario: Detect if word contains substring "aba".
        Regex: (a|b)* aba (a|b)*
        States: 
            q0: wait/loop
            q1: saw 'a', hope for 'b'
            q2: saw 'ab', hope for 'a'
            q3: saw 'aba', accept/loop
        """
        states = {'q0', 'q1', 'q2', 'q3'}
        alphabet = {'a', 'b'}
        initial_states = {'q0'}
        accepting_states = {'q3'}
        k = 1
        
        # Transitions
        delta = {
            # q0 loops on anything
            ('q0', ('a',), 'q0'), ('q0', ('b',), 'q0'),
            
            # Start pattern 'a'
            ('q0', ('a',), 'q1'),
            
            # q1: needs 'b'
            ('q1', ('b',), 'q2'),
            
            # q2: needs 'a'
            ('q2', ('a',), 'q3'),
            
            # q3: loop on anything (accepting state)
            ('q3', ('a',), 'q3'), ('q3', ('b',), 'q3')
            # Removed infinite padding loop ('q3', ('#',), 'q3')
        }
        
        alpha = ['E']
        nfh = NFH(states, initial_states, accepting_states, k, delta, alpha, alphabet)
        
        # Test 1: MATCH "bbababb" (contains aba in middle)
        # Nondeterminism: at index 2 ('a'), can stay q0 or go q1.
        # Path: q0(b)->q0(b)->q1(a)->q2(b)->q3(a)->q3(b)->q3(b) --> ACCEPT
        result, _ = checkMembership(nfh, Hyperword({'bbababb'}))
        self.assertTrue(result)
        
        # Test 2: NO MATCH "aabbb" (no aba)
        result, _ = checkMembership(nfh, Hyperword({'aabbb'}))
        self.assertFalse(result)
        
        # Test 3: Overlapping "ababa" (matches)
        result, _ = checkMembership(nfh, Hyperword({'ababa'}))
        self.assertTrue(result)

    def test_concatenation_k3(self):
        """
        Scenario: Check relation R(x,y,z) <=> z = xy.
        k = 3.
        Phase 1 (Reading x): 
          If x has char 'c', z must match 'c'. y stays idle.
          If x ends (sees '#'), switch to Phase 2.
        Phase 2 (Reading y):
          If y has char 'c', z must match 'c'. x is empty '#'.
          If y ends (sees '#') AND z sees '#', Accept.
        """
        states = {'q_x', 'q_y', 'q_acc', 'q_rej'}
        alphabet = {'a', 'b', '#'}
        initial_states = {'q_x'}
        accepting_states = {'q_acc'}
        k = 3
        
        delta = set()
        
        # Phase 1: Match x and z. y is idle (must be buffered? No, we just read from x and z, y doesn't move).
        # Wait, if we don't consume y, we just read '#' (if asynchronous/peeking) OR we must effectively 'pause' y?
        # In this simulator, if we define transition with # for y, it consumes only if y is empty? 
        # Ah, the logic in valid_transitions enforces: if symbol is '#', buffer MUST be empty.
        # If the buffer is NOT empty, we cannot read '#'.
        # Solution: To "pause" a non-empty buffer, we simply don't include it in the consumption?
        # But our NFH definition requires reading k-tuple symbols every step.
        # If we specify '#', the code asserts input is empty.
        # So... strict synchronous reading of k inputs implies we consume ALL streams.
        # We cannot "pause" a stream in standard NFH unless we use a "Skip" symbol that exists in the alphabet but means "No-Op".
        # OR: We use the Asynchronous definition where we can read epsilon from some tracks?
        # Our simulator `RunManager` consumes a symbol if it is NOT '#'.
        # If we put '#' in the transition symbol vector for track 2, does it consume?
        # `move`: `if sym != '#': buffer.popleft()`.
        # So YES! We can put '#' in the transition to NOT CONSUME from that track, 
        # BUT `valid_transitions` enforces `if symbol == '#': if buffer: valid = False`.
        # THIS IS THE CATCH.
        # The code currently running (after I reverted) allows async moves:
        # Code: `current_char = buffer[0] if buffer else '#'` and `if symbol != '#'` check.
        # So if I set symbol='#', and buffer has 'a', then `# != #` is false? No.
        # `symbol='#'`. `current_char='a'`.
        # `symbol != '#'` is False. So the condition `if symbol != '#' and ...` is skipped? 
        # Wait, let's re-read valid_transitions logic carefully.
        
        """
        current_char = buffer[0] if buffer else '#'
        if symbol != '#' and symbol != current_char:
             valid = False
        """
        # If symbol is '#': The IF body is skipped. Valid remains True.
        # So we CAN take a transition with '#' even if buffer has 'a'.
        # And `move` says: `if sym != '#': popleft()`.
        # So if symbol is '#', we DO NOT pop.
        # This confirms we can implement "Pause" by using '#'.
        
        # Phase 1: x -> z. y Paused (#).
        for char in ['a', 'b']:
            # (char, #, char) -> q_x
            delta.add(('q_x', (char, '#', char), 'q_x'))
            
        # Switch phase: x is empty (#), y starts.
        # We need to detect "x finished".
        # Transition: (#, #, #) -> q_y? No, we still need to process y.
        # If x is empty, we must start reading y.
        # Transition from q_x to q_y reading first char of y?
        # OR transition on (#, #, #) is only for empty strings.
        # We can move q_x -> q_y by reading nothing? Epsilon transition?
        # Simulator doesn't support explicit Epsilon in state transition, only in input reading.
        # But we can read (x='#', y='a', z='a') and move to q_y.
        
        for char in ['a', 'b']:
            delta.add(('q_x', ('#', char, char), 'q_y'))
            
        # Phase 2: y -> z. x Empty (#).
        for char in ['a', 'b']:
            delta.add(('q_y', ('#', char, char), 'q_y'))
            
        # Finish: All empty
        delta.add(('q_y', ('#', '#', '#'), 'q_acc'))
        
        # Test cases
        alpha = ['E', 'E', 'E'] # Check exists x,y,z
        nfh = NFH(states, initial_states, accepting_states, k, delta, alpha, alphabet)
        
        # True: "a" + "b" = "ab"
        # x='a' (len 1), y='b' (len 1), z='ab' (len 2).
        # Step 1 (q_x): Read (a, #, a). x->empty, z->'b'. y still 'b'. State q_x.
        # Step 2 (q_x -> q_y): Read (#, b, b). x empty, y->empty, z->empty. State q_y.
        # Step 3 (q_y -> q_acc): Read (#, #, #). Accept.
        
        assignment = ['a', 'b', 'ab']
        manager = RunManager(nfh, assignment)
        self.assertTrue(manager.run())
        
        # False: "a" + "b" != "ba"
        # Step 1: Read (a, #, b)? Mismatch (a!=b). Reject.
        assignment_bad = ['a', 'b', 'ba']
        manager_bad = RunManager(nfh, assignment_bad)
        self.assertFalse(manager_bad.run())

    def test_graph_property_self_loop(self):
        """
        Scenario: Graph encoded as words. 
        Edge (u,v) exists if NFH accepts (u,v).
        Property: Every node x has a self-loop (x,x).
        Forall x in S, (x,x) in R.
        
        Relation R: "First letter matches". (u[0] == v[0]).
        S = {a, ab, b, ba}
        (a,a) OK. (a,ab) OK. (ab,ab) OK.
        (b,b) OK. (ba,ba) OK.
        """
        states = {'q0', 'q_ok', 'q_bad', 'q_acc'}
        alphabet = {'a', 'b'}
        initial_states = {'q0'}
        accepting_states = {'q_acc'}
        k = 2
        
        delta = {
            # Start: Match first char
            ('q0', ('a', 'a'), 'q_ok'),
            ('q0', ('b', 'b'), 'q_ok'),
            
            # Mismatch first char -> bad
            ('q0', ('a', 'b'), 'q_bad'),
            ('q0', ('b', 'a'), 'q_bad'),
            
            # After ok, consume anything until empty
            ('q_ok', ('a', 'a'), 'q_ok'), ('q_ok', ('b', 'b'), 'q_ok'),
            ('q_ok', ('a', 'b'), 'q_ok'), ('q_ok', ('b', 'a'), 'q_ok'),
            ('q_ok', ('a', '#'), 'q_ok'), ('q_ok', ('#', 'a'), 'q_ok'),
            ('q_ok', ('b', '#'), 'q_ok'), ('q_ok', ('#', 'b'), 'q_ok'),
            
            ('q_ok', ('#', '#'), 'q_acc')
        }
        
        alpha = ['A']
        
        # Automaton: Starts with 'a'
        k=1
        delta_k1 = {
             ('q0', ('a',), 'q_ok'),
             ('q_ok', ('a',), 'q_ok'), ('q_ok', ('b',), 'q_ok'), ('q_ok', ('#',), 'q_acc')
        }
        nfh_a = NFH(states, initial_states, accepting_states, k, delta_k1, ['A'], alphabet)
        
        # S = {a, ab}. All start with a. -> True
        result, _ = checkMembership(nfh_a, Hyperword({'a', 'ab'}))
        self.assertTrue(result)
        
        # S = {a, b}. b fails. -> False
        result, _ = checkMembership(nfh_a, Hyperword({'a', 'b'}))
        self.assertFalse(result)

    def test_single_maximum_length_word(self):
        '''
        Scenario: this NFH should accept hyperwords that have a single word of maximum length.
        Examples: S = {a, ab, b, ba} -> False. S = {a, ab, b, ba, baa} -> True.

        The property: There exists a word, x1, such that, for any word x2 in S:
        if x1 != x2, then x1 is longer than x2.
        '''
        
        states = {'q0', 'q_eq', 'q_read', 'q_acc'}
        initial_states = {'q0'}
        accepting_states = {'q_acc', 'q_eq'}
        k = 2
        alphabet = {'a', 'b'}
        delta = {
            ('q0', ('a', 'a'), 'q_eq'),
            ('q0', ('b', 'b'), 'q_eq'),
            ('q_eq', ('a', 'a'), 'q_eq'),
            ('q_eq', ('b', 'b'), 'q_eq'),
            # q_eq will only count as accepting if x1, x2 are the same word

            ('q0', ('a', 'a'), 'q_read'),
            ('q0', ('b', 'b'), 'q_read'),
            ('q0', ('a', 'b'), 'q_read'),
            ('q0', ('b', 'a'), 'q_read'),


            ('q_read', ('a', 'a'), 'q_read'),
            ('q_read', ('b', 'b'), 'q_read'),
            ('q_read', ('a', 'b'), 'q_read'),
            ('q_read', ('b', 'a'), 'q_read'),


            ('q_read', ('a', '#'), 'q_acc'),
            ('q_read', ('b', '#'), 'q_acc'),

            ('q_acc', ('a', '#'), 'q_acc'),
            ('q_acc', ('b', '#'), 'q_acc'),
        }

        alpha = ['E', 'A']
        nfh = NFH(states, initial_states, accepting_states, k, delta, alpha, alphabet)

        # S = {a, ab, b, ba} -> False
        result, _ = checkMembership(nfh, Hyperword({'a', 'ab', 'b', 'ba'}))
        self.assertFalse(result)

        # S = {a, ab, b, ba, baa} -> True
        result, _ = checkMembership(nfh, Hyperword({'a', 'ab', 'b', 'ba', 'baa'}))
        self.assertTrue(result)
        
        # S = {a, ab, b, ba, baa, baaa} -> True
        result, _ = checkMembership(nfh, Hyperword({'a', 'ab', 'b', 'ba', 'baa', 'baaa'}))
        self.assertTrue(result)

        words = {
            s
            for n in range(0, 11)
            for i in range(2**n)
            for s in [format(i, f"0{n}b").replace("0", "a").replace("1", "b")]
        } | {"a" * 11}
        assert len(words) == 2047
        result, _ = checkMembership(nfh, Hyperword(words))
        self.assertTrue(result)

        words = {
            s
            for n in range(0, 11)
            for i in range(2**n)
            for s in [format(i, f"0{n}b").replace("0", "a").replace("1", "b")]
        }
        assert len(words) == 2046
        result, _ = checkMembership(nfh, Hyperword(words))
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
