import sys

from copy import deepcopy

from typing import Any
from typing import Iterable
from typing import Type

from src.banking_app.models.base import Base


class KwargsParser:
    operators = {
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

    def parse_kwargs(
            self,
            *,
            module_name: str,
            model: Type[Base],
            **kwargs,
    ) -> str:
        """
        Parse passed kwargs and transform them to Where expression, example:

        ```python
        # noqa: E501
        conditions = KwargsParser().parse_kwargs(
            module_name=__name__,
            model=Client,
            sex=Sex.MALE,
            name='Some',
            age__in=[34, 21],
            weight__ge=80,
        )

        print(condition)
        >>> "(_KwargsParser_Client.sex == _KwargsParser_Sex.MALE, _KwargsParser_Client.name == 'Some', _KwargsParser_Client.age.in_((34, 21,)), _KwargsParser_Client.weight >= 80,)"

        print(globals())
        >>> {
            ...,
            '_KwargsParser_Client': <class 'src.banking_app.models.client.Client'>,
            '_KwargsParser_Sex': <enum 'Sex'>,
        }
        ```

        Use repr function, all required modules are imported into module!

        ```python
        statement = select(Client).where(*repr(condition))
        ```
        """

        if kwargs == dict():
            return '(True,)'

        model_name, kwargs = self._set_dependencies_in_modules(
            modules=[__name__, module_name],
            model=model,
            **kwargs,
        )

        conditions = list()
        for attr_name, attr_value in kwargs.items():
            expression = self._get_appropriate_expression(
                attr_name=attr_name,
                attr_value=attr_value,
                model_name=model_name,
            )
            conditions.append(expression)
        return f"({', '.join(conditions)},)"

    def _get_appropriate_expression(
            self,
            *,
            attr_name: str,
            attr_value: Any,
            model_name: str,
    ) -> str:
        attr_name__operator = attr_name.strip().split('__')
        length = len(attr_name__operator)

        expression = f'{attr_name} == {attr_value}'
        if length == 2:
            attr_name, operator = attr_name__operator
            expression = self._parse_operator(
                attr_name=attr_name,
                operator=operator,
                attr_value=attr_value,
            )

        return f'{model_name}.{expression}'

    def _parse_operator(
            self,
            *,
            attr_name: str,
            operator: str,
            attr_value: Any,
    ) -> str:
        expression = self.operators.get(operator)
        if expression is None:
            raise ValueError(
                f'Operator `{operator}` not in `{self.operators.keys()}`'
            )
        return expression.format(attr=attr_name, value=attr_value)

    def _set_dependencies_in_modules(
            self,
            *,
            modules: list[str],
            model: Type[Base],
            **kwargs,
    ) -> tuple[str, dict[str, str]]:
        """Install all required for statement execution modules."""

        prefix = f'_{type(self).__name__}'
        err = "raise ValueError(f'Module {} not found.')"
        modules = [sys.modules.get(mod, err.format(mod)) for mod in modules]

        model_type_name = f'{prefix}_{model.__name__}'
        [setattr(mod, model_type_name, model) for mod in modules]

        for key, value in deepcopy(kwargs).items():
            kwargs[key] = self._set_dependencies_for_sequences(
                value=value,
                prefix=prefix,
                modules=modules,
            )
        return model_type_name, kwargs

    def _set_dependencies_for_sequences(
            self,
            *,
            value: Any,
            prefix: str,
            modules: list[str],
    ) -> str:
        value_type = type(value)
        if value_type is type:
            value_type = value

        if value_type is str:
            return repr(value)  # Without repr: '1234' -> 1234;

        if isinstance(value, Iterable):
            value = list(value)
            for i, item in enumerate(value):
                value[i] = self._set_dependencies_for_sequences(
                    value=item,
                    prefix=prefix,
                    modules=modules,
                )
            return f'({', '.join(value)},)'

        if value_type.__module__ == object.__module__:  # If is builtins;
            return value
        else:
            attr_type_alias = f'{prefix}_{value_type.__name__}'
            [setattr(mod, attr_type_alias, value_type) for mod in modules]
            attr_type_origin = getattr(modules[0], attr_type_alias).__name__
            try:
                repr_ = repr(value).replace(attr_type_origin, attr_type_alias)
                eval(repr_)
                value = repr_
            except SyntaxError:
                str_ = str(value).replace(attr_type_origin, attr_type_alias)
                value = str_
            return value
