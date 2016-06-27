import sys
import functools
import math
import operator
import fithtypes # FithList, FithVar, FithFunc, NamedFunc, FithBool, FithNull

class word:
    def __init__(self, arity):
        self.arity = arity
    def __call__(self, func):
        arity = self.arity
        @functools.wraps(func)
        def wrapper(stack):
            args = []
            for _ in range(arity):
                args.append(stack.pop())
            result = func(*args[::-1])
            if result is not None:
                stack.push(result)
        return wrapper

def Fith_dump_stack(stack):
    print(stack._list)

@word(1)
def Fith_len(L):
    return len(L._list)

@word(2)
def Fith_cmp(a, b):
    if a < b:
        return -1
    elif a > b:
        return 1
    else:
        return 0

@word(2)
def Fith_get(L, i):
    return L[i]

def Fith_set(stack):
    x = stack.pop()
    i = stack.pop()
    stack.peek()._list[i] = x

def Fith_append(stack):
    item = stack.pop()
    stack.peek()._list.append(item)

def Fith_prepend(stack):
    item = stack.pop()
    stack.peek()._list.insert(0, item)

def Fith_del(stack):
    index = stack.pop()
    stack.peek()._list.pop(index)

def Fith_slice(stack):
    sl = [i if isinstance(i, int) else None for i in stack.pop()._list]
    L = stack.peek()._list
    L[:] = [L[i] for i in range(*slice(*sl).indices(len(L)))]

@word(1)
def Fith_transpose(L):
    outlist = [fithtypes.FithList(subl) for subl in list(zip(*L._list))]
    return fithtypes.FithList(outlist)

def Fith_dump(stack):
    L = stack.pop()
    stack._list += L

def Fith_dup(stack):
    stack.push(stack.peek())

def Fith_drop(stack):
    stack.pop()

def Fith_swap(stack):
    b = stack.pop()
    a = stack.pop()
    stack.push(b)
    stack.push(a)

def Fith_over(stack):
    b = stack.pop()
    a = stack.peek()
    stack.push(b)
    stack.push(a)

def Fith_rot(stack):
    c = stack.pop()
    b = stack.pop()
    a = stack.pop()
    stack.push(b)
    stack.push(c)
    stack.push(a)

def Fith_invrot(stack):
    Fith_rot(stack)
    Fith_rot(stack)

def Fith_nip(stack):
    Fith_swap(stack)
    stack.pop()

def Fith_tuck(stack):
    Fith_swap(stack)
    Fith_over(stack)

def Fith_transform(stack):
    before, after = stack.pop().split('--')
    names = {}
    for metavar in before[::-1]:
        names[metavar] = stack.pop()
    for metavar in after:
        stack.push(names[metavar])

def Fith_line(stack):
    stack.push(input())

def Fith_read(stack):
    stack.push(sys.stdin.read())

def Fith_castgen(cast):
    def castfunc(stack):
        stack._list[-1] = cast(stack.peek())
    return castfunc

@word(1)
def Fith_cast_list(thing):
    newlist = fithtypes.FithList()
    try:
        newlist._list = list(thing)
    except TypeError:
        newlist._list = [thing]
    return newlist

def Fith_typecheckgen(T):
    @word(1)
    def typechecker(thing):
        return isinstance(thing, T)
    return typechecker

def Fith_open_def(metastack, words):
    name = next(words)
    if next(words) != '(':
        print("Error: missing stack effect in definition of \"{name}\"".format(name=name))
        sys.exit()
    params = []
    param = next(words)
    while param != '--':
        params.append(param)
        param = next(words)
    returns = []
    ret = next(words)
    while ret != ')':
        returns.append(ret)
        ret = next(words)
    metastack.push(fithtypes.NamedFunc(name, params, returns))

def Fith_close_def(metastack, _=None):
    if metastack.is_live:
        print("Error: unmatched ;")
        sys.exit()
    metastack.compile()

def Fith_open_lambda(metastack, _=None):
    metastack.push(fithtypes.FithFunc())

def Fith_close_lambda(metastack, _=None):
    if metastack.is_live:
        print("Error: unmatched }")
        sys.exit()
    metastack.cons()

def Fith_quote(metastack, words):
    metastack.peek().push(next(words))

def Fith_set_var(metastack, words):
    metastack.setvar(next(words), fithtypes.FithVar(metastack.pop_from_top()))

def Fith_register(metastack, words):
    metastack.setvar(next(words), metastack.pop_from_top())

def Fith_open_list(metastack, _=None):
    metastack.push(fithtypes.FithList())

def Fith_close_list(metastack, _=None):
    metastack.cons()

Fith_primitives = {
    '+': word(2)(operator.add),
    '-': word(2)(operator.sub),
    '*': word(2)(operator.mul),
    '/': word(2)(operator.truediv),
    '/_': word(2)(operator.floordiv),
    'abs': word(1)(abs),
    'mod': word(2)(operator.mod),
    'pow': word(2)(pow),
    'powmod': word(3)(pow),
    'floor': word(1)(math.floor),
    'ceil': word(1)(math.ceil),
    'min': word(2)(min),
    'max': word(2)(max),
    'sqrt': word(1)(math.sqrt),
    '.': word(1)(print),
    '\.': word(1)(functools.partial(print, end='')),
    '.s': Fith_dump_stack,
    'len': Fith_len,
    'cmp': Fith_cmp,
    'not': word(1)(operator.not_),
    'and': word(2)(operator.and_),
    'or': word(2)(operator.or_),
    'get': Fith_get,
    'set': Fith_set,
    'del': Fith_del,
    'append': Fith_append,
    'prepend': Fith_prepend,
    'slice': Fith_slice,
    'transpose': Fith_transpose,
    'ord': word(1)(ord),
    'chr': word(1)(chr),
    'dump': Fith_dump,
    'dup': Fith_dup,
    'drop': Fith_drop,
    'swap': Fith_swap,
    'over': Fith_over,
    'rot': Fith_rot,
    #'-rot': Fith_invrot,
    #'nip': Fith_nip,
    #'tuck': Fith_tuck,
    'transform': Fith_transform,
    'line': Fith_line,
    'read': Fith_read,
    '>int': Fith_castgen(int),
    '>float': Fith_castgen(float),
    '>str': Fith_castgen(str),
    '>list': Fith_cast_list,
    'int?': Fith_typecheckgen(int),
    'float?': Fith_typecheckgen(float),
    'str?': Fith_typecheckgen(str),
    'list?': Fith_typecheckgen(fithtypes.FithList),
    '#t':fithtypes.FithBool(True),
    '#f':fithtypes.FithBool(False),
    '_': fithtypes.FithNull(),
}

Fith_metawords = {
    ':': Fith_open_def,
    '{': Fith_open_lambda,
    '[': Fith_open_list,
    "'": Fith_quote,
    '->': Fith_set_var,
    '::': Fith_register,
}

class metaword:
    def __init__(self, name):
        self._name = name
    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(metastack, words=None):
            return func(metastack, words)
        Fith_metawords[self._name] = wrapper
        return wrapper
