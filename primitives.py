from fithtypes import FithObj

def close_list(stack, code, parsestack, funcnames, varnames):
    newlist = FithObj(list)
    while stack.peek().ftype != '[':
        newlist.pyval.append(stack.pop())
    newlist.pyval.reverse()

def bind_word(stack, code, parsestack, funcnames, varnames):
    name = stack.pop()
    func = stack.pop()
    if name.ftype != 'string':
        raise TypeError("%bind-word expected ( func string ) on stack")
    funcnames[name] = func
    return stack, code, parsestack, funcnames, varnames

def bind_var(stack, code, parsestack, funcnames, varnames):
    name = stack.pop()
    value = stack.pop()
    if name.ftype != 'string':
        raise TypeError("%bind-var expected ( obj string ) on stack")
    varnames[name] = value
    return stack, code, parsestack, funcnames, varnames

def quote_n(stack, code, parsestack, funcnames, varnames):
    n = stack.pop()
    if n.ftype != 'int':
        raise TypeError("%quote-n expected ( int ) on stack")
    for _ in range(n.pyval):
        stack.push(FithObj(code.pop(0)))
    return stack, code, parsestack, funcnames, varnames

def quote
