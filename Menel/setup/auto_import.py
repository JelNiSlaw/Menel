import importlib
import pkgutil
from types import ModuleType
from typing import Iterable

from .. import log
from ..objects import commands


# Inspired by https://github.com/python-discord/bot/blob/master/bot/utils/extensions.py

def unqualify(name: str) -> str:
    return name.rsplit('.', maxsplit=1)[-1]


def modules_to_str(modules: Iterable[ModuleType]):
    return ', '.join(unqualify(m.__name__) for m in modules)


def add_help(module: ModuleType):
    # noinspection PyUnresolvedReferences
    commands.update({module.COMMAND.name: module.COMMAND})


def auto_import(package, *args, add_to_help: bool):
    modules = set()

    for module in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
        if unqualify(module.name).startswith('_'):
            continue  # skip the file if it starts with an _

        if module.ispkg:
            continue  # skip folders

        module = importlib.import_module(module.name)
        # noinspection PyUnresolvedReferences
        module.setup(*args)
        if add_to_help:
            add_help(module)
        modules.add(module)

    log.debug(f'Imported {modules_to_str(modules)}')

    return modules