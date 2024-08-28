import ast
from typing import Union

from ariadne_codegen.client_generators.constants import (
    OPTIONAL,
    UNION,
    UNSET_NAME,
    UNSET_TYPE_NAME,
)
from ariadne_codegen.plugins.base import Plugin
from graphql import OperationDefinitionNode


def is_ignorable_ast_node(node: Union[ast.expr, None]) -> bool:
    return node is None or isinstance(node, ast.Name)


class RewriteUnsetTypeMethodArguments(Plugin):
    def generate_client_method(
        self,
        method_def: Union[ast.FunctionDef, ast.AsyncFunctionDef],
        operation_definition: OperationDefinitionNode,
    ) -> Union[ast.FunctionDef, ast.AsyncFunctionDef]:
        for idx, arg in enumerate(method_def.args.args):
            if isinstance(arg.annotation, ast.Subscript):
                annotation = arg.annotation
                if annotation.slice is None or not isinstance(
                    annotation.slice, ast.Tuple
                ):
                    continue
                if (
                    not isinstance(annotation.value, ast.Name)
                    or annotation.value.id != UNION
                ):
                    continue
                subscript, name = annotation.slice.elts
                if (
                    isinstance(subscript, ast.Subscript)
                    and isinstance(subscript.value, ast.Name)
                    and subscript.value.id == OPTIONAL
                    and isinstance(name, ast.Name)
                    and name.id == UNSET_TYPE_NAME
                ):
                    arg.annotation = subscript
                else:
                    continue
            elif not is_ignorable_ast_node(arg.annotation):
                raise TypeError(
                    f"Expected annotation to be of type Subscript. Got {arg.annotation}"
                )
        if method_def.args.defaults is not None:
            method_def.args.defaults = list(
                map(
                    lambda arg: (
                        ast.Name(id="None")
                        if isinstance(arg, ast.Name) and arg.id == UNSET_NAME
                        else arg
                    ),
                    method_def.args.defaults,
                )
            )
        return method_def
