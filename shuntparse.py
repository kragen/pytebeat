#!/usr/bin/python
# -*- coding: utf-8 -*-
"""A shunting-yard parser to evaluate bytebeat expressions.

Parses a common subset of integer C and JS, plus >>>.

I wrote this mostly while seated on the floor of a crowded train on
the way home on Friday, after a long workday and only a few hours of
sleep the night before.  So the code is pretty messy in a lot of ways,
and somewhat incomplete.

I’m hoping I can polish this up a bit more into interactive bytebeat
performing software with live SDL waveform graphics in time for
tonight’s performance.

"""
import operator
import re
import traceback
import subprocess
import sys

try:
    from Numeric import where, arange, UInt8
except ImportError:
    from numpy import where, arange, uint8
    UInt8 = uint8

class ParseError(Exception): pass
class MissingOperator(ParseError): pass
class TrailingOperator(ParseError): pass
class ConsecutiveOperators(ParseError): pass
class UnmatchedRightParen(ParseError): pass
class UnmatchedLeftParen(ParseError): pass
class UnknownOpPrecedence(ParseError): pass # Can’t happen

def parse(tokens):
    ops = []
    last = NullToken(None, '(null)')
    out = []

    for token in tokens:
        if token.isa(BinaryMinus) and last.isa(Op):
            token = UnaryMinus(token)


        if token.isa(Leaf):
            if not last.isa(Op):
                raise MissingOperator(token)
            out.append(token)

        elif token.isa(RightParen):
            if last.isa(Op):
                raise ConsecutiveOperators(token)
            while ops and not ops[-1].isa(LeftParen):
                ops.pop().apply(out)
            if not ops:
                raise UnmatchedRightParen(token)
            ops.pop()

        else:
            assert token.isa(Op)
            if token.isa(UnaryOp) and not last.isa(Op):
                raise MissingOperator(token)
            if token.isa(BinaryOp) and last.isa(Op):
                raise ConsecutiveOperators(token)
            while ops and token.left_binds_looser_than(ops[-1]):
                ops.pop().apply(out)
            ops.append(token)


        last = token

    if last.isa(Op):
        raise TrailingOperator(last)
    
    while ops:
        ops.pop().apply(out)

    assert len(out) == 1
    return out.pop()

class Token(object):
    def __init__(self, pos, text): self.pos, self.text = pos, text
    def __repr__(self):
        return '<%s %r at %s>' % (self.__class__.__name__,
                                  self.text,
                                  self.pos)
    def __str__(self):
        return self.text
    
    def isa(self, klass):
        return isinstance(self, klass)

class Op(Token):
    def __init__(self, *args):
        Token.__init__(self, *args)
        self.precedence = precedence_of(self.text)
        self.associates_left = associates_left(self.text)

    def left_binds_looser_than(self, op):
        return (op.precedence > self.precedence or
                (op.precedence == self.precedence and self.associates_left))

# Left parens behave syntactically like operators in some important
# ways (they can be followed by unary operators or leaves, and they
# get pushed on the op stack, which causes other operators to
# interrogate their precedence).  Right parens do not.
class LeftParen(Op):
    def apply(self, out):
        # This can only happen if we’re left on the stack at the end
        # of the parse.
        raise UnmatchedLeftParen(self)

    # XXX should I just say that it associates right?
    def left_binds_looser_than(self, op):
        return False

class RightParen(Token): pass
# NullToken is a lot like a left paren too.
class NullToken(Op): pass

class UnaryOp(Op):
    def apply(self, out):
        out.append(UnaryApply(self, out.pop()))

    def left_binds_looser_than(self, _):
        return False

    def eval(self, arg):
        return unary_denotations[self.text](arg)

class UnaryMinus(UnaryOp):
    def __init__(self, binary_minus):
        self.pos = binary_minus.pos
        self.text = binary_minus.text
        self.precedence = precedence_of(UnaryMinus)

class BinaryOp(Op):
    def apply(self, out):
        right = out.pop()
        out.append(BinaryApply(self, out.pop(), right))

    def eval(self, left, right):
        return binary_denotations[self.text](left, right)

class BinaryMinus(BinaryOp): pass
class Leaf(Token):
    def rpn(self):
        return self.text
    
class Variable(Leaf):
    def eval(self, env):
        return env[self.text]
    
class Constant(Leaf):
    def eval(self, env):
        return (int(self.text, 16) if self.text.startswith('0x')
                else int(self.text))

def tokenize(string):
    for mo in re.finditer(r'\w+|&&|\|\||==|>>>|>>|<<|<=|>=|!=|[-&|^+()~!*/,%<>=]', string):
        text = mo.group(0)
        token_type = (UnaryOp if text in '~!' else
                      BinaryMinus if text == '-' else
                      LeftParen if text == '(' else
                      RightParen if text == ')' else
                      Constant if text[0].isdigit() else
                      Variable if text[0].isalpha() or text[0] in '$_' else
                      BinaryOp)
        yield token_type(mo.start(), text)
        

def precedence_of(text):
    for level, ops in enumerate(precedences):
        if text in ops:
            return level
    raise UnknownOpPrecedence(text)

precedences = [['(null)', '('],
               [','],
               ['='],
               ['||'],
               ['&&'],
               ['|'],
               ['^'],
               ['&'],
               ['==', '!='],
               ['<', '<=', '>', '>='],
               ['<<', '>>', '>>>'],
               ['+', '-'],
               ['*', '/', '%'],
               ['!', '~', UnaryMinus],
               ]

def associates_left(text):
    # In full JS and C, augmented assignments, ?:, and function calls
    # also associate right, but this is the only right-associative
    # operator I’m handling now.
    return text != '='


class Apply(object): pass

class BinaryApply(Apply):
    def __init__(self, op, left, right):
        self.op, self.left, self.right = op, left, right
    def __repr__(self):
        return '[[ %r %r %r ]]' % (self.left, self.op, self.right)
    def __str__(self):
        return '(%s%s%s)' % (self.left, self.op, self.right)
    def eval(self, env):
        if self.op.text == '=':
            rvalue = self.right.eval(env)
            env[self.left.text] = rvalue
            return rvalue
        else:        
            left = self.left.eval(env)
            right = self.right.eval(env)
            return self.op.eval(left, right)
    def rpn(self):
        if self.op.text == '=':
            return ' '.join([self.right.rpn(), 'constant', self.left.text])
        elif self.op.text == ',':
            return ' '.join([self.left.rpn(), '', self.right.rpn()])
        else:
            return ' '.join([self.left.rpn(), self.right.rpn(), self.op.text])

class UnaryApply(Apply):
    def __init__(self, op, operand):
        self.op, self.operand = op, operand
    def __repr__(self):
        return '[[ %r %r ]]' % (self.op, self.operand)
    def __str__(self):
        return '%s%s' % (self.op, self.operand)
    def eval(self, env):
        value = self.operand.eval(env)
        return self.op.eval(value)
    def rpn(self):
        if self.op.text == '-':
            return ' '.join(['0', self.operand.rpn(), '-'])
        else:
            return ' '.join([self.operand.rpn(), self.op.text])

# Here we introduce a dependency on Numeric, and force return values
# of booleans and comparators to be (possibly zero-dimensional)
# Numeric arrays, in order to get Boolean and logical semantics more
# or less compatible with JS.  The alternative would be to do
# isinstance tests on the values passed in to the operators to see
# what to return, and that would be unacceptable.

# The remaining incompatibility is that && and || aren’t
# short-circuiting, so different assignments might happen here than in
# JS.

binary_denotations = {
    ',': lambda a, b: b,
    '|': operator.or_,
    '^': operator.xor,
    '&': operator.and_,
    '<<': operator.lshift,
    '>>': operator.rshift,
    '+': operator.add,
    '-': operator.sub,
    # This isn't correct, but it avoids Numeric's ArithmeticError:
    # Integer overflow in multiply.
    '*': lambda a, b: (a & (2**15-1)) * (b & (2**15-1)),
    # These two have to worry about SIGFPE from division by zero.
    '/': lambda a, b: a / where(b == 0, 1, b),
    '%': lambda a, b: a % where(b == 0, 1, b),

    '&&': lambda a, b: where(a, where(b, 1, 0), 0),
    '||': lambda a, b: where(a, 1, where(b, 1, 0)),
    '==': lambda a, b: where(a == b, 1, 0),
    '!=': lambda a, b: where(a != b, 1, 0),
    '<': lambda a, b: where(a < b, 1, 0),
    '>': lambda a, b: where(a > b, 1, 0),
    '<=': lambda a, b: where(a <= b, 1, 0),
    '>=': lambda a, b: where(a >= b, 1, 0),
}

unary_denotations = {
    '~': operator.inv,
    '-': operator.neg,
    '!': lambda x: where(x, 0, 1),
}

def ps(astr):
    "Parse string, for interactive testing."
    try:
        return parse(tokenize(astr))
    except ParseError, e:
        traceback.print_exc()
        print e.__class__, repr(e.args[0])

def roundtrip(astr):
    return str(ps(astr))

def play_bytebeat(astr, out):
    t = 0
    n_samples = 256
    formula = ps(astr)
    if formula is None:
        return
    if out is not sys.stdout:
        print formula
        print formula.rpn()

    while True:
        x = formula.eval({'t': arange(t, t+n_samples)})
        out.write(x.astype(UInt8).tostring())
        t += n_samples

if __name__ == '__main__':
    if sys.argv[1] == '-o':
        if sys.argv[2] == '-':
            outfile = sys.stdout
        else:
            outfile = open(sys.argv[2], 'w')
        sys.argv[1:3] = []
    else:
        try:
            # This will no longer work even on current Linux; instead you must
            # at least popen aplay.
            outfile = open('/dev/dsp', 'w')
        except IOError:
            # Fall back to ALSA or PulseAudio if present.
            cmd = 'aplay || pacat --format=u8 --rate=8000 --channels=1'
            outfile = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE).stdin
    try:
        play_bytebeat(sys.argv[1], outfile)
    finally:
        outfile.close()
