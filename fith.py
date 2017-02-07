import re
from fithtypes import FithObj, Stack
from fithprimitives import primitives

class UndefinedWordError:
    pass

funcnames = {}
varname = {}

# Decorator to maintain interpreter state between parsestack calls
def static(**kwargs):
    def decorated(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorated

def parse_normal(stack, code, parsestack):
    global funcnames
    global varnames
    word = code[0]
    if re.match(r"[0-9]*\.[0-9]*(e[0-9]+)?$", word) and not re.match(r"\.(e[0-9]+)?$", word):
        stack.push(FithObj(float(word)))
    elif re.match(r"[0-9]+(e[0-9]+)?$", word):
        stack.push(FithObj(int(word)))
    elif word.startswith("'"):
        stack.push(FithObj(word[1:]))
    elif word == '{':
        parsestack.push(parse_function)
        stack.push(FithObj(list))
    elif word in primitives:
        stack, code, parsestack, funcnames, varnames = primitives[word](stack, code, parsestack, funcnames, varnames)
    elif word in funcnames:
        code = funcnames[word].pyval + code
    elif word in varnames:
        stack.push(varnames[word])
    else:
        raise UndefinedWordError(word)
    return stack, code, parsestack

@static(nest_count=0)
def parse_function(stack, code, parsestack):
    word = code[0]
    if word == '{':
        parse_function.nest_count += 1
    elif word == '}':
        parse_function.nest_count -= 1
        if parse_function.nest_count == -1:
            parse_function.nest_count = 0
            parsestack.pop()
    else:
        stack.peek().pyval.append(FithObj(word))
    return stack, code, parsestack

def run(code, stack_=None):
    stack = stack_ or Stack()
    for i in range(len(code)):
        stack, code[i:], parsestack = parsestack.peek()(stack, code[i:], parsestack)
