"""Parser."""
from sys import stdin


def tokenize(s):
    r"""
    Tokenize a string.

    >>> tokenize("(quote (+ 1 2) + (1 (1)))")
    ['(', 'quote', '(', '+', 1, 2, ')', '+', '(', 1, '(', 1, ')', ')', ')']
    """
    return list(map(lambda s: int(s) if s.isnumeric() else s, filter(
        bool, s.replace('(', '( ').replace(')', ' )').split())))


def parse(tokens):
    """
    Parse a token stream.

    >>> parse(['(', '(', '+', 1, 2, ')', '+', '(', 1, '(', 1, ')', ')', ')'])
    (('+', 1, 2), '+', (1, (1,)))
    """
    def _list():
        tokens.pop(0)
        while tokens[0] != ')':
            yield parse(tokens)
        tokens.pop(0)
    return tuple(_list()) if tokens[0] == '(' else tokens.pop(0)


def compile(sexp, indent=0):
    """Compile s expressions to Python expressions."""
    tabs = '\t' * indent
    if isinstance(sexp, (tuple, list)):
        car, *cdr = sexp
        if car == 'def':
            name, args, *body, last = cdr
            yield tabs + car + ' ' + name + '(' + ' '.join(args) + '):\n'
            for block in body:
                yield from compile(block, indent=indent+1)
                yield '\n'
            yield tabs + '\treturn '
            yield from compile(last, indent=indent+1)
            yield '\n'
        elif car == 'defmacro':
            name, args, body = cdr
            defmacro(name, args, body)
        elif car == 'if':
            cond, if_, else_ = cdr
            yield from compile(if_)
            yield ' if '
            yield from compile(cond)
            yield ' else '
            yield from compile(else_)
        else:
            yield str(car) + '('
            if cdr:
                *prn, last = cdr
                for block in prn:
                    yield from compile(block, indent=indent+1)
                    yield ', '
                yield from compile(last, indent=indent+1)
            yield ')'
    else:
        yield str(sexp)

if __name__ == "__main__":
    print('from env import *')
    for expression in parse(tokenize('(' + stdin.read() + ')')):
        print(''.join(compile(expression)))
