import re
import itertools
import fithtypes

def parse(raw, name=''):
    raw = remove_comments(raw)
    raw = re.split(r'"(.*?)"', raw.strip())
    offset = 1 if raw[0] else 0
    if not raw[0]: raw.pop(0)
    if not raw[-1]: raw.pop()
    strings = {}
    for i in range(offset, len(raw), 2):
        placeholder = '\x02' + name + str(i)
        string = parse_escapes(raw[i])
        strings[placeholder] = fithtypes.FithVar(string)
        raw[i] = placeholder
    return itertools.chain.from_iterable(s.split() for s in raw), strings

def parse_escapes(string):
    escapes = {
        'a': '\x07',
        'b': '\x08',
        'f': '\x0C',
        'n': '\x0A',
        'r': '\x0D',
        't': '\x09',
        'v': '\x0B',
        'q': '"',
    }
    pointer = 0
    final = []
    while pointer < len(string):
        char = string[pointer]
        if char == '\\':
            try:
                esc = string[pointer + 1]
            except IndexError:
                print("Error: Incomplete backslash escape in string literal \"{string}\"".format(string=string))
                sys.exit()
            if esc in escapes:
                final.append(escapes[esc])
                pointer += 2
            elif esc == 'x':
                final.append(chr(int(string[ pointer+2 : pointer+4 ], 16)))
                pointer += 3
            elif esc == 'u':
                final.append(chr(int(string[ pointer+2 : pointer+6 ], 16)))
                pointer += 5
            elif esc == 'U':
                final.append(chr(int(string[ pointer+2 : pointer+10 ], 16)))
                pointer += 9
            else:
                final.append(esc)
                pointer += 2
        else:
            final.append(char)
            pointer += 1
    return ''.join(final)

def remove_comments(code):
    no_comments = re.sub(r"##.*$", ' ', code, flags=re.MULTILINE)
    return re.sub(r" {2,}", ' ', no_comments.replace('\n', ' '))
