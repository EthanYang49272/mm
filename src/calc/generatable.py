from __future__ import annotations

import random
import logging
from fractions import Fraction
from collections.abc import Sequence
from typing import Protocol, TypeVar

from .node import Node
from .op import Operator, Add, Subtract, Multiply, Divide
from .terminal import Terminal, Integer, Decimal
from ..config import CONFIG

class GeneratableError(RuntimeError):
    """
    Exception raised when a ``Generatable`` node cannot be constructed within
    the supplied ``max_bonus`` budget.

    Inherits from ``RuntimeError``.  Callers should catch this exception and
    retry generation with different random choices.
    """
    pass

T = TypeVar("T")

def random_pick(array: Sequence[T]) -> T:
    return random.choice(array)

class TerminalFactory(Protocol):
    def __call__(self, max_bonus: int) -> Node: ...

class Generatable:
    """
    Abstract mixin base class for nodes that randomly generate their own
    children within a difficulty budget.

    All ``Generatable`` subclasses accept a single ``max_bonus`` parameter in
    ``__init__`` that constrains the total difficulty of the generated
    expression.  This class is not intended to be instantiated directly.

    Parameters:
        max_bonus (int): The maximum cumulative difficulty bonus allowed for
            the expression tree rooted at this node.

    Raises:
        NotImplementedError: Always — ``Generatable.__init__`` is abstract and
            must be overridden by every concrete subclass.
    """
    def __init__(self, max_bonus: int):
        raise NotImplementedError

class GeneratebleTerminal(Generatable, Terminal):
    """
    Abstract bridge class combining ``Generatable`` and ``Terminal``.

    Subclasses inherit both the random-generation interface from
    ``Generatable`` and the terminal-node behaviour from ``Terminal``.
    On construction the node's ``bonus`` is validated against ``max_bonus``
    and a ``GeneratableError`` is raised if the budget is exceeded.

    Parameters:
        max_bonus (int): The maximum difficulty bonus permitted for this
            terminal node.

    Raises:
        GeneratableError: If ``self.bonus`` exceeds ``max_bonus``.
    """
    def __init__(self, max_bonus: int):
        if(self.bonus > max_bonus):
            raise GeneratableError

class GeneratebleInteger(GeneratebleTerminal, Integer):
    """
    A randomly generated integer terminal node.

    On construction ``self.value`` is set to a random integer in the range
    ``[-99, 99]``.  Inherits ``bonus = 1`` from ``Integer``.

    Parameters:
        max_bonus (int): The maximum allowed difficulty bonus.  Must be at
            least ``1`` (the bonus of an integer); raises ``GeneratableError``
            otherwise.

    Attributes:
        value (Fraction): ``Fraction(v, 1)`` where ``v`` is a random integer
            in ``[-99, 99]``.

    Raises:
        GeneratableError: If ``max_bonus < 1``.
    """
    def __init__(self, max_bonus: int):
        super().__init__(max_bonus)
        self.value = Fraction(random.randint(CONFIG["min_int"], CONFIG["max_int"]),1)

class GeneratebleDecimal(GeneratebleTerminal, Decimal):
    """
    A randomly generated one-decimal-place decimal terminal node.

    On construction:

    * ``integer_part`` is a random integer in ``[-99, 99]``.
    * ``decimal_part`` is a random multiple of 10 in ``{0, 10, 20, …, 90}``,
      ensuring the value has exactly one decimal place.
    * ``value`` is set to ``Fraction(integer_part * 100 + decimal_part, 100)``.

    Inherits ``bonus = 2`` from ``Decimal``.

    Parameters:
        max_bonus (int): The maximum allowed difficulty bonus.  Must be at
            least ``2`` (the bonus of a decimal); raises ``GeneratableError``
            otherwise.

    Attributes:
        integer_part (int): Random integer in ``[-99, 99]``.
        decimal_part (int): Random multiple of 10 in ``[0, 90]``.
        value (Fraction): The combined decimal value as a ``Fraction``.

    Raises:
        GeneratableError: If ``max_bonus < 2``.
    """
    def __init__(self, max_bonus: int):
        super().__init__(max_bonus)
        self.integer_part = random.randint(CONFIG["min_int"], CONFIG["max_int"])
        self.decimal_part = random.randint(0, 9) * 10 # making the decimal is 1 d.p. by making sure decimal_part is a multiple of 10
        sign = 1 if self.integer_part >= 0 else -1
        self.value = Fraction(self.integer_part * 100 + sign * self.decimal_part, 100)
        logging.info(f"Generate Decimal, int: {self.integer_part}, dec: {self.decimal_part}, val: {self.value}")

class GeneratableOperator(Generatable, Operator):
    """
    Abstract bridge class combining ``Generatable`` and ``Operator``.

    Subclasses inherit both the random-generation interface from
    ``Generatable`` and the operator-node behaviour from ``Operator``.
    This class provides a no-op ``__init__``; concrete subclasses randomly
    assign ``self.left`` and ``self.right`` within the given bonus budget.

    Parameters:
        max_bonus (int): The maximum cumulative difficulty bonus allowed for
            the expression tree rooted at this operator node.
    """
    def __init__(self, max_bonus: int):
        pass

class GeneratableAdd(Add, GeneratableOperator):
    """
    A randomly generated addition expression node.

    On construction, random left and right child nodes are chosen from
    ``[GeneratebleInteger, GeneratebleDecimal]``.  The bonus budget is split
    randomly between the two children
    (``left_bonus + right_bonus == max_bonus``) and generation is retried
    until ``self.score() <= max_bonus``.

    Parameters:
        max_bonus (int): The maximum cumulative difficulty bonus for this
            expression.  Must be at least ``2`` to accommodate two terminal
            children.

    Attributes:
        left (Node): Randomly generated left operand (integer or decimal).
        right (Node): Randomly generated right operand (integer or decimal).

    Raises:
        GeneratableError: If ``max_bonus < 2``.
    """
    def __init__(self, max_bonus: int):
        super().__init__(max_bonus)
        if(max_bonus < 2):
            raise GeneratableError
        possible_operand: Sequence[TerminalFactory] = (
            GeneratebleInteger,
            GeneratebleDecimal,
        )
        count = 1
        while(True):
            try:
                left_bonus = random.randint(1, max_bonus)
                right_bonus = max_bonus - left_bonus
                # bonus of parent node = sum of bonus of children nodes

                self.left = random_pick(possible_operand)(left_bonus)
                self.right = random_pick(possible_operand)(right_bonus)
                if(self.score() <= max_bonus):
                    break
            except GeneratableError:
                # print("Retry Generating %d" % count)
                count += 1
                continue

class GeneratableSubtract(Subtract, GeneratableOperator):
    """
    A randomly generated subtraction expression node.

    On construction, random left and right child nodes are chosen from
    ``[GeneratebleInteger, GeneratebleDecimal]``.  The bonus budget is split
    randomly between the two children
    (``left_bonus + right_bonus == max_bonus``) and generation is retried
    until ``self.score() <= max_bonus``.

    Parameters:
        max_bonus (int): The maximum cumulative difficulty bonus for this
            expression.  Must be at least ``2`` to accommodate two terminal
            children.

    Attributes:
        left (Node): Randomly generated left operand (integer or decimal).
        right (Node): Randomly generated right operand (integer or decimal).

    Raises:
        GeneratableError: If ``max_bonus < 2``.
    """
    def __init__(self, max_bonus: int):
        super().__init__(max_bonus)
        if(max_bonus < 2):
            raise GeneratableError
        possible_operand: Sequence[TerminalFactory] = (
            GeneratebleInteger,
            GeneratebleDecimal,
        )
        count = 1
        while(True):
            try:
                left_bonus = random.randint(1, max_bonus)
                right_bonus = max_bonus - left_bonus
                self.left = random_pick(possible_operand)(left_bonus)
                self.right = random_pick(possible_operand)(right_bonus)
                if(self.score() <= max_bonus):
                    break
            except GeneratableError:
                # print("Retry Generating %d" % count)
                count += 1
                continue

class GeneratableMultiply(Multiply, GeneratableOperator):
    """
    A randomly generated multiplication expression node.

    On construction, random left and right child nodes are chosen from
    ``[GeneratebleInteger]`` only — decimals are excluded to keep
    multiplication tractable.  The bonus budget is split randomly between the
    two children and generation is retried until ``self.score() <= max_bonus``.

    Parameters:
        max_bonus (int): The maximum cumulative difficulty bonus for this
            expression.  Must be at least ``2`` to accommodate two terminal
            children.

    Attributes:
        left (Node): Randomly generated left integer operand.
        right (Node): Randomly generated right integer operand.

    Raises:
        GeneratableError: If ``max_bonus < 2``.
    """
    def __init__(self, max_bonus: int):
        super().__init__(max_bonus)
        if(max_bonus < 2):
            raise GeneratableError
        count = 1
        while(True):
            try:
                self.left = Integer(random.randint(CONFIG["min_int"], CONFIG["max_int"]))
                self.right = Integer(random.randint(0, 9))
                if(self.score() <= max_bonus):
                    break
            except GeneratableError:
                # print("Retry Generating %d" % count)
                count += 1
                continue

class GeneratableDivide(Divide, GeneratableOperator):
    """
    A randomly generated division expression node.

    On construction, random left and right child nodes are chosen from
    ``[GeneratebleInteger]`` only — decimals are excluded to keep division
    tractable.  The bonus budget is split randomly between the two children
    and generation is retried until ``self.score() <= max_bonus``.

    Parameters:
        max_bonus (int): The maximum cumulative difficulty bonus for this
            expression.  Must be at least ``2`` to accommodate two terminal
            children.

    Attributes:
        left (Node): Randomly generated left integer operand.
        right (Node): Randomly generated right integer operand.

    Raises:
        GeneratableError: If ``max_bonus < 2``.
    """
    def __init__(self, max_bonus: int):
        super().__init__(max_bonus)
        if(max_bonus < 2):
            raise GeneratableError
        possible_operand: Sequence[TerminalFactory] = (
            GeneratebleInteger,
        )
        count = 1
        while(True):
            try:
                left_bonus = random.randint(1, max_bonus)
                right_bonus = max_bonus - left_bonus
                self.left = random_pick(possible_operand)(left_bonus)
                self.right = random_pick(possible_operand)(right_bonus)
                if(self.score() <= max_bonus):
                    break
            except GeneratableError:
                # print("Retry Generating %d" % count)
                count += 1
                continue

root_operators: Sequence[TerminalFactory] = (
    GeneratableAdd,
    GeneratableSubtract,
    GeneratableMultiply,
    GeneratableDivide,
)

def generate(score: int) -> Node:
    root: Node = random_pick(root_operators)(score)
    return root

# for i in range(1):
#     e = GeneratableAdd(5)
#     print(e)
#     print(e.get_value())
#     print(e.score())

# python3 --version