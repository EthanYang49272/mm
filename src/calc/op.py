from fractions import Fraction
import logging

from .node import Node

class Operator(Node):
    """
    Abstract base class for all operator nodes in the expression tree.

    An operator node combines a left and right child ``Node`` using some
    arithmetic operation.  Concrete operator classes must define
    ``precedence``, ``weight``, and implement ``compute()``.

    Attributes:
        bonus (int): Flat difficulty bonus added to this node's score
            (default ``0``).
        weight (int): Multiplier applied to the sum of child scores when
            computing this node's score via
            ``(left.score() + right.score()) * weight + bonus``.
        left (Node): The left-hand child node.
        right (Node): The right-hand child node.

    Parameters:
        left (Node): The left operand node.
        right (Node): The right operand node.
    """
    bonus = 0
    weight: int
    left: Node
    right: Node

    def __init__(self, left: Node, right: Node):
        self.left = left
        self.right = right

    def score(self):
        return (self.left.score() + self.right.score()) * self.weight + self.bonus

class BinaryOperator(Operator):
    """
    A concrete base class for binary (two-operand) operators.

    Extends ``Operator`` with a string ``symbol`` and a ``__str__`` method
    that renders the expression as an infix string, automatically inserting
    parentheses around child nodes whose precedence is lower than this
    operator's.

    Attributes:
        symbol (str): The infix symbol used to display this operator
            (e.g. ``"+"``, ``"-"``, ``"*"``, ``"/"``).
    """
    symbol: str
    def compute(self, left_operand: Fraction, right_operand: Fraction) -> Fraction:
        raise NotImplementedError

    def get_value(self) -> Fraction:
        left = self.left.get_value()
        right = self.right.get_value()
        logging.info(f"Binary get_value, left {left}, right {right}")
        return self.compute(left, right)

    def __str__(self) -> str:
        left_str = str(self.left)
        if self.left.precedence < self.precedence:
            left_str = f"({left_str})"
        right_str = str(self.right)
        if self.right.precedence < self.precedence:
            right_str = f"({right_str})"
        return f"{left_str} {self.symbol} {right_str}"

class Add(BinaryOperator):
    """
    Binary operator node that computes addition (``left + right``).

    Attributes:
        precedence (int): ``1`` — same level as subtraction.
        symbol (str): ``"+"``
        weight (int): ``1`` — addition is the least complex binary operation.
    """
    precedence = 1
    symbol = "+"
    weight = 1
    def compute(self, left_operand: Fraction, right_operand: Fraction):
        return left_operand + right_operand
    
class Subtract(BinaryOperator):
    """
    Binary operator node that computes subtraction (``left - right``).

    Attributes:
        precedence (int): ``1`` — same level as addition.
        symbol (str): ``"-"``
        weight (int): ``1`` — subtraction shares the same complexity as
            addition.
    """
    precedence = 1
    symbol = "-"
    weight = 1
    def compute(self, left_operand: Fraction, right_operand: Fraction):
        return left_operand - right_operand

class Multiply(BinaryOperator):
    """
    Binary operator node that computes multiplication (``left * right``).

    Attributes:
        precedence (int): ``2`` — higher than addition and subtraction.
        symbol (str): ``"*"``
        weight (int): ``2`` — multiplication is considered more complex than
            addition or subtraction.
    """
    precedence = 2
    symbol = "*"
    weight = 2
    def compute(self, left_operand: Fraction, right_operand: Fraction):
        return left_operand * right_operand

class Divide(BinaryOperator):
    """
    Binary operator node that computes division (``left / right``).

    Attributes:
        precedence (int): ``2`` — same level as multiplication.
        symbol (str): ``"/"``
        weight (int): ``2`` — division shares the same complexity as
            multiplication.
    """
    precedence = 2
    symbol = "/"
    weight = 2
    def compute(self, left_operand: Fraction, right_operand: Fraction):
        return left_operand / right_operand

class Power(BinaryOperator):
    """
    Binary operator node that computes exponentiation (``left ** right``).

    Attributes:
        precedence (int): ``3`` — highest precedence among the defined
            operators.
        symbol (str): ``"^"``
        weight (int): ``2`` — exponentiation is treated as equally complex as
            multiplication and division.
    """
    precedence = 3
    symbol = "^"
    weight = 2
    def compute(self, left_operand: Fraction, right_operand: Fraction):
        return Fraction(left_operand ** right_operand)
    
#! How to display Log???
class Log(BinaryOperator):
    """
    Binary operator node intended to represent a logarithm.

    .. warning::
        This class is not yet fully implemented.  The ``symbol`` and
        ``compute()`` method are temporary placeholders copied from ``Power``
        and do not correctly represent logarithm display or computation.

    Attributes:
        precedence (int): ``3`` — placeholder, same as ``Power``.
        symbol (str): ``"^"`` — placeholder, not a valid logarithm symbol.
        weight (int): ``2`` — placeholder complexity weight.
    """
    precedence = 3
    symbol = "^"
    weight = 2
    def compute(self, left_operand: Fraction, right_operand: Fraction):
        return Fraction(left_operand ** right_operand)

# fa0 = Add(Integer(1), Integer(2))
# fa0 = Power(Add(Integer(1), Integer(2)), Multiply(Add(Integer(1), Integer(1)), Integer(2)))
# print(fa0.get_value())
# print(fa0.display())