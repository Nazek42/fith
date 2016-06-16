import sys
from functools import partial

class FithVar:
    def __init__(self, value):
        self._value = value
    def __call__(self, stack):
        stack.push(self._value)

class Stack:
    def __init__(self):
        self._list = []
        self._locals = {}

    def peek(self):
        return self._list[-1]

    def pop(self):
        try:
            return self._list.pop()
        except IndexError:
            print("Error: trying to pop empty stack")
            sys.exit()

    def push(self, item):
        self._list.append(item)

    def setvar(self, name, value):
        self._locals[name] = value

    def getvar(self, name):
        return self._locals[name]

    def __len__(self):
        return len(self._list)

class FithList(Stack):
    def __repr__(self):
        return ' '.join(['['] + [str(item) for item in self._list] + [']'])
    def __getitem__(self, index):
        return self._list[index]

class Metastack(Stack):
    @property
    def is_live(self):
        return not isinstance(self.peek(), (FithFunc, NamedFunc))

    def cons(self):
        self._list[-2].push(self.pop())

    def compile(self):
        func = self.pop()
        self.peek().setvar(func.name, func)

    def getvar(self, name):
        for stack in self._list:
            try:
                return stack.getvar(name)
            except KeyError:
                pass
        try:
            return super().getvar(name)
        except KeyError:
            print("Error: unrecognized word {name}".format(name=name))
            sys.exit()

    def pop_from_top(self):
        return self._list[-1].pop()
    def push_to_top(self, item):
        self._list[-1].push(item)

class FithFunc(Stack):
    pass

class NamedFunc(Stack):
    def __init__(self, name, params, returns):
        super().__init__()
        self.params = params
        self.returns = returns
        self.arity = len(params)
        self.returncount = len(returns)
        self.name = name

class FithBool(int):
    def __repr__(self):
        return "#t" if self else "#f"
    def pyify(self):
        return bool(self)
    def __call__(self, stack):
        stack.push(self)

class FithNull:
    def __repr__(self):
        return "#null"
    def pyify(self):
        return None
    def __call__(self, stack):
        stack.push(self)
