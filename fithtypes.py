class EmptyStackError:
    pass

class Stack:
    def __init__(self, start=None):
        self._list = start or []

    def peek(self):
        return self._list[-1]

    def pop(self):
        try:
            return self._list.pop()
        except IndexError:
            raise EmptyStackError

    def push(self, item):
        self._list.append(item)

    def __len__(self):
        return len(self._list)

class ListMarker:
    pass

class FithObj:
    def __init__(self, pyval):
        if isinstance(init, type):
            self.pyval = init()
            self.ftype = typeconv[str(init)]
        else:
            self.pyval = init
            self.ftype = typeconv[str(type(init))]

typeconv = {
    str(int): 'int',
    str(float): 'float',
    str(str): 'string',
    str(list): 'list',
    str(dict): 'hash',
    str(None): 'null',
    str(ListMarker): '[',
}
