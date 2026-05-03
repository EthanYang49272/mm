from fractions import Fraction
import sys

from .node import Node

class Terminal(Node):
    """
    Abstract base class for leaf nodes in the expression tree.

    Terminal nodes represent numeric values (integers, decimals, etc.) that
    serve as the operands of operator nodes.  They have no children.

    Attributes:
        value (Fraction): The numeric value of this terminal, stored as a
            ``fractions.Fraction`` for exact arithmetic.
        precedence (int): Set to ``sys.maxsize`` so that a terminal is never
            wrapped in parentheses when an operator builds its display string.
    """
    value: Fraction
    precedence = sys.maxsize

    def get_value(self) -> Fraction:
        """returns the calculated value in Fraction form"""
        return self.value

    def score(self) -> int:
        """how much score will be rewarded to the user based on weight and bonus"""
        return self.bonus

class Integer(Terminal):
    """
    A terminal node that holds a whole-number (integer) value.

    The integer is stored internally as ``Fraction(int_value, 1)`` so that it
    participates in exact fraction arithmetic with other nodes.

    Attributes:
        bonus (int): Difficulty bonus of ``1``, reflecting the low complexity
            of an integer operand.
        value (Fraction): ``Fraction(int_value, 1)`` — the integer expressed
            as a fraction with denominator 1.

    Parameters:
        int_value (int): The integer value to store in this node.

    Example::

        str(Integer(7))  # "7"
        Integer(7).result()   # Fraction(7, 1)
    """
    bonus = 1
    def __init__(self, int_value: int):
        self.value = Fraction(int_value, 1)

    def __str__(self) -> str:
        """returns the display format by casting str() onto the numerator part of Integer(Terminal)"""
        return str(self.value.numerator)


class Decimal(Terminal):
    """
    A terminal node that holds a decimal value with up to two decimal places.

    The value is stored as ``Fraction(integer_part * 100 + decimal_part, 100)``
    for exact arithmetic.  ``decimal_part`` must be in the range ``[0, 99]``.

    Attributes:
        bonus (int): Difficulty bonus of ``2``, reflecting the higher complexity
            of a decimal operand compared to an integer.
        value (Fraction): The decimal expressed as a fraction with denominator
            100.
        integer_part (int): The whole-number component of the decimal value.
        decimal_part (int): The fractional component expressed in hundredths
            (e.g. ``4`` → ``.04``, ``40`` → ``.4``).

    Parameters:
        integer_part (int): The whole-number component of the decimal.
        decimal_part (int): The sub-decimal component in hundredths.

    Example::

        str(Decimal(9, 40))  # "9.4"
        str(Decimal(9, 4))   # "9.04"
        Decimal(9, 40).value()   # Fraction(940, 100)
    """
    bonus = 2
    integer_part: int
    decimal_part: int

    def __init__(self, integer_part: int, decimal_part: int):
        sign = 1 if integer_part >= 0 else -1
        self.value = Fraction(integer_part * 100 + sign * decimal_part, 100)
        self.integer_part = integer_part
        self.decimal_part = decimal_part
    
    #! Display 9.40 as 9.4
    def __str__(self) -> str:
        if self.decimal_part % 10 == 0:
            return f"{self.integer_part}.{self.decimal_part//10:d}"
        else:
            return f"{self.integer_part}.{self.decimal_part:02d}"
