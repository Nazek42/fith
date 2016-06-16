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
            if word == '}' and isinstance(stack, fithtypes.FithFunc):
                if lambda_counter > 0:
                    lambda_counter -= 1
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
                    if isinstance(transform, (fithtypes.FithFunc, fithtypes.NamedFunc)):
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
    FithExec(metastack, metastack.pop_from_top()._list)

@metaword('if')
def Fith_if(metastack, _=None):
    func = metastack.pop_from_top()
    cond = metastack.pop_from_top()
    if cond:
        stack.push(func)
        Fith_run(metastack)

@metaword('branch')
def Fith_branch(metastack, _=None):
    iffalse = metastack.pop_from_top()
    iftrue = metastack.pop_from_top()
    cond = metastack.pop_from_top()
    stack.push(iftrue if cond else iffalse)
    Fith_run(metastack)

@metaword('while')
def Fith_while(metastack, _=None):
    body = metastack.pop_from_top()
    cond = metastack.pop_from_top()
    while cond:
        metastack.push_to_top(body)
        Fith_run(metastack)
        cond = metastack.pop_from_top()

if __name__ == '__main__':
    main()
