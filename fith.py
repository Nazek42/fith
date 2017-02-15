import sys
import re
import itertools
import json
import os.path
from primitives import (Fith_primitives, Fith_metawords, metaword,
                        Fith_close_def, Fith_close_lambda, Fith_close_list)
import fithtypes # Stack, Metastack, FithFunc, NamedFunc, FithList
import parse

def main():
    words, strings = parse.parse(sys.stdin.read())
    metastack = fithtypes.Metastack()
    metastack.push(fithtypes.Stack())
    metastack._locals.update(Fith_primitives)
    metastack._locals.update(strings)
    keys, values = zip(*json.load(open("lib/listing.json")).items())
    values = [fithtypes.FithVar(value) for value in values]
    metastack._locals.update(zip(keys, values))
    FithExec(metastack, ["*builtins*", "load"])
    FithExec(metastack, words)

def FithExec(metastack, words):
    words = iter(words)
    try:
        lambda_counter = 0
        while True:
            stack = metastack.peek()
            word = next(words)
            #print("word:",word,"lambda_counter:",lambda_counter)
            if word == '}' and isinstance(stack, fithtypes.FithFunc):
                #print("Encountered }, lambda_counter:",lambda_counter)
                if lambda_counter > 0:
                    lambda_counter -= 1
                    stack.push(word)
                else:
                    Fith_close_lambda(metastack)
            elif word == ';' and isinstance(stack, fithtypes.NamedFunc):
                Fith_close_def(metastack)
            elif word == ']' and isinstance(stack, fithtypes.FithList):
                Fith_close_list(metastack)
            elif not metastack.is_live:
                if word == '{': lambda_counter += 1
                stack.push(word)
            else:
                #print("Live word:", word)
                try:
                    stack.push(int(word))
                    continue
                except ValueError:
                    try:
                        stack.push(float(word))
                        continue
                    except ValueError:
                        pass
                if word in Fith_metawords:
                    Fith_metawords[word](metastack, words)
                else:
                    transform = metastack.getvar(word)
                    #print("Encountered function: (",word,',',transform._list,')')
                    if isinstance(transform, (fithtypes.FithFunc, fithtypes.NamedFunc)):
                        #print("Encountered function: (",word,',',transform._list,')')
                        FithExec(metastack, transform._list)
                    else:
                        transform(stack)
    except StopIteration:
        pass
    except KeyboardInterrupt:
        print("Error: Ctrl-C pressed")
        sys.exit()

@metaword('load')
def Fith_load(metastack, _=None):
    try:
        path = os.path.abspath(metastack.pop_from_top())
    except TypeError:
        print("Error: load expected string")
        sys.exit()
    try:
        with open(path) as file:
            words, strings = parse.parse(file.read())
    except FileNotFoundError:
        print("Error: could not find file {path}".format(path=path))
        sys.exit()
    metastack._locals.update(strings)
    FithExec(metastack, words)

@metaword('~')
def Fith_run(metastack, _=None):
    func = metastack.pop_from_top()
    #print("Running function:", func._list)
    FithExec(metastack, func._list)

@metaword('if')
def Fith_if(metastack, _=None):
    stack = metastack.peek()
    func = stack.pop()
    cond = stack.pop()
    if cond:
        stack.push(func)
        Fith_run(metastack)

@metaword('branch')
def Fith_branch(metastack, _=None):
    stack = metastack.peek()
    iffalse = stack.pop()
    iftrue = stack.pop()
    cond = stack.pop()
    stack.push(iftrue if cond else iffalse)
    Fith_run(metastack)

@metaword('while')
def Fith_while(metastack, _=None):
    stack = metastack.peek()
    body = stack.pop()
    cond = stack.pop()
    stack.push(cond)
    Fith_run(metastack)
    while stack.pop():
        stack.push(body)
        Fith_run(metastack)
        stack.push(cond)
        Fith_run(metastack)

@metaword('filter')
def Fith_filter(metastack, _=None):
    stack = metastack.peek()
    func = stack.pop()
    lst = stack.peek()
    lst._list[:] = [thing for thing in lst._list if check(metastack, func, thing)]

def check(metastack, func, thing):
    stack = metastack.peek()
    stack.push(thing)
    stack.push(func)
    Fith_run(metastack)
    return metastack.peek().pop()

if __name__ == '__main__':
    main()
