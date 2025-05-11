from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):
    def __init__(self):
        self.next_states: list[State] = []

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        function checks whether occured character is handled by current ctate
        """
        pass

    def check_next(self, next_char: str) -> State | Exception:
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        raise NotImplementedError("rejected string")


class StartState(State):
    next_states: list[State] = []

    def __init__(self):
        super().__init__()

    def check_self(self, char):
        return super().check_self(char)


class TerminationState(State):
    def __init__(self):
        super().__init__()

    def check_self(self, char: str) -> bool:
        return False


class DotState(State):
    """
    state for . character (any character accepted)
    """

    next_states: list[State] = []

    def __init__(self):
        super().__init__()

    def check_self(self, char: str) -> bool:
        return True


class AsciiState(State):
    """
    state for alphabet letters or numbers
    """

    next_states: list[State] = []
    curr_sym = ""

    def __init__(self, symbol: str) -> None:
        super().__init__()
        self.curr_sym = symbol

    def check_self(self, curr_char: str) -> bool:
        return self.curr_sym == curr_char


class StarState(State):

    next_states: list[State] = []

    def __init__(self, inner_state: State):
        super().__init__()
        self.inner_state = inner_state

    def check_self(self, char: str) -> bool:
        for state in self.next_states:
            if state.check_self(char):
                return True

        return False


class PlusState(State):
    next_states: list[State] = []

    def __init__(self, inner_state: State):
        super().__init__()
        self.inner_state = inner_state

    def check_self(self, char: str) -> bool:
        return self.inner_state.check_self(char)


class RegexFSM:
    curr_state: State = StartState()

    def __init__(self, regex_expr: str) -> None:
        self.regex_expr = regex_expr
        self.curr_state = StartState()
        self.start_state = self.curr_state

        prev_state = self.curr_state
        tmp_next_state = self.curr_state

        for char in regex_expr:
            tmp_next_state = self.__init_next_state(char, prev_state, tmp_next_state)
            prev_state.next_states.append(tmp_next_state)

    def __init_next_state(
        self, next_token: str, prev_state: State, tmp_next_state: State
    ) -> State:
        new_state = None

        match next_token:
            case next_token if next_token == ".":
                new_state = DotState()

            case next_token if next_token == "*":
                new_state = StarState(tmp_next_state)
                new_state.next_states.append(tmp_next_state)

            case next_token if next_token == "+":
                new_state = PlusState(tmp_next_state)
                new_state.next_states.append(tmp_next_state)

            case next_token if next_token.isascii():
                new_state = AsciiState(next_token)

            case _:
                raise AttributeError("Character is not supported")

        return new_state

    def check_string(self, input_str: str):
        states = []
        i = 0
        while i < len(self.regex_expr):
            c = self.regex_expr[i]
            if c == "*" and states:
                prev = states.pop()
                star = StarState(prev)
                star.next_states.append(prev)
                states.append(star)
            elif c == "+" and states:
                prev = states.pop()
                plus = PlusState(prev)
                plus.next_states.append(prev)
                states.append(plus)
            elif c == ".":
                states.append(DotState())
            else:
                states.append(AsciiState(c))
            i += 1

        for i in range(len(states) - 1):
            states[i].next_states.append(states[i + 1])

        term = TerminationState()
        if states:
            states[-1].next_states.append(term)
            self.start_state.next_states = [states[0]]
        else:
            self.start_state.next_states = [term]

        def can_match(state: State, s: str, pos: int) -> bool:
            if pos == len(s):
                return any(isinstance(n, TerminationState) or can_match(n, s, pos)
                           for n in state.next_states)

            if state.check_self(s[pos]):
                if can_match(state, s, pos + 1):
                    return True

            for next_state in state.next_states:
                if next_state.check_self(s[pos]) and can_match(next_state, s, pos + 1):
                    return True
                if isinstance(next_state, StarState) and can_match(next_state, s, pos):
                    return True

            return False

        return can_match(self.start_state, input_str, 0)


if __name__ == "__main__":
    regex_pattern = "a*4.+hi"

    regex_compiled = RegexFSM(regex_pattern)

    print(regex_compiled.check_string("aaaaaa4uhi"))  # True
    print(regex_compiled.check_string("4uhi"))  # True
    print(regex_compiled.check_string("meow"))  # False
