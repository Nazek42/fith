import sys
import functools
import fithtypes # FithList, FithVar, FithFunc, NamedFunc, FithBool, FithNull

def Fith_add(stack):
    b = stack.pop()
    a = stack.pop()
    stack.push(a + b)

def Fith_sub(stack):
    b = stack.pop()
    a = stack.pop()
    stack.push(a - b)

def Fith_mul(stack):
    b = stack.pop()
    a = stack.pop()
    stack.push(a * b)

def Fith_div(stack):
    b = stack.pop()
    a = stack.pop()
    stack.push(a / b)

def Fith_mod(stack):
    b = stack.pop()
    a = stack.pop()
    stack.push(a % b)

def Fith_print(stack):
    print(stack.pop())

def Fith_dump_stack(stack):
    print(stack._list)

def Fith_len(stack):
    stack.push(len(stack.pop()))

def Fith_cmp(stack):
    b = stack.pop()
    a = stack.pop()
    if a < b:
        stack.push(-1)
    elif a > b:
        stack.push(1)
    else:
        stack.push(0)

def Fith_not(stack):
    stack.push(not stack.pop())

def Fith_get(stack):
    i = stack.pop()
    L = stack.pop()
    stack.push(L[i])

def Fith_append(stack):
    item = stack.pop()
    stack.peek()._list.append(item)

def Fith_prepend(stack):
    item = stack.pop()
    stack.peek()._list.insert(0, item)

def Fith_slice(stack):
    sl = [i if isinstance(i, int) else None for i in stack.pop()]
    L = stack.peek()._list
    L[:] = [L[i] for i in range(*slice(*sl).indices(len(L)))]

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
    a = stack.peek()
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

def Fith_open_list(metastack, _=None):
    metastack.push(fithtypes.FithList())

def Fith_close_list(metastack, _=None):
    metastack.cons()

Fith_primitives = {
    '+': Fith_add,
    '-': Fith_sub,
    '*': Fith_mul,
    '/': Fith_div,
    '%': Fith_mod,
    '.': Fith_print,
    '.s': Fith_dump_stack,
    'len': Fith_len,
    'cmp': Fith_cmp,
    'not': Fith_not,
    '@': Fith_get,
    'append': Fith_append,
    'prepend': Fith_prepend,
    'slice': Fith_slice,
    'dup': Fith_dup,
    'drop': Fith_drop,
    'swap': Fith_swap,
    'over': Fith_over,
    'rot': Fith_rot,
    #'-rot': Fith_invrot,
    #'nip': Fith_nip,
    #'tuck': Fith_tuck,
    'transform': Fith_transform,
    '#t':fithtypes.FithBool(True),
    '#f':fithtypes.FithBool(False),
    '#null': fithtypes.FithNull,
}

Fith_metawords = {
    ':': Fith_open_def,
    '{': Fith_open_lambda,
    '[': Fith_open_list,
    "'": Fith_quote,
    '->': Fith_set_var,
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
