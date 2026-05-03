from fractions import Fraction

class Node:
    """
    Abstract base class for all nodes in the arithmetic expression tree.

    Every node — both operator nodes and terminal (value) nodes — inherits
    from this class.  Subclasses must implement ``value()``, ``score()``,
    and ``__str__``.

    Attributes:
        precedence (int): Operator precedence used when deciding whether to
            wrap a child node in parentheses during display.  Higher values
            bind more tightly.
        bonus (int): Difficulty bonus associated with this node, contributing
            to the score awarded to the user.
    """

    precedence: int
    bonus: int

    def __init__(self):
        pass

    def get_value(self) -> Fraction:
        raise NotImplementedError

    def score(self) -> int:
        raise NotImplementedError
    
    def __str__(self) -> str:
        raise NotImplementedError
