from json import dumps
from json import loads

from typing import Iterable


OPERATORS = {
    'gt': '{attr} > {value}',
    'lt': '{attr} < {value}',
    'ge': '{attr} >= {value}',
    'le': '{attr} <= {value}',

    'eq': '{attr} == {value}',
    'noteq': '{attr} != {value}',
    'not_eq': '{attr} != {value}',

    'in': '{attr}.in_({value})',
    'notin': '{attr}.notin_({value})',
    'not_in': '{attr}.notin_({value})',

    'between': '{attr}.between{value}',
}


class KwargsParser:

    def parse_kwargs(self, **kwargs) -> str:
        if kwargs == dict():
            return '(True,)'
        kwargs_serialized = dict()
        for f, v in kwargs.items():
            kwargs_serialized[f] = self._value_dump(v)
        expression = self._sql_build(kwargs_serialized)
        return f'({expression},)'

    def _value_dump(self, value):
        if isinstance(value, str):
            pass
        elif type(value).__module__ != object.__module__:  # If not builtins.
            value = str(value)
        elif isinstance(value, Iterable):
            value = [self._value_dump(v) for v in value]
        return loads(dumps(value))

    def _sql_build(self, kwargs) -> str:
        expressions = list()
        for k, v in kwargs.items():
            v = repr(v) if isinstance(v, str) else v
            attr_name__operator = k.strip().split('__')
            expression = f'{k} == {v}'
            if len(attr_name__operator) == 2:
                attr_name, operator = attr_name__operator
                expression = OPERATORS.get(operator)
                if expression is None:
                    raise ValueError(f'Operator `{operator}` not in `{OPERATORS.keys()}`')
                expression = expression.format(attr=attr_name, value=v)
            expressions.append(f'self.model.{expression}')
        return ', '.join(expressions)
