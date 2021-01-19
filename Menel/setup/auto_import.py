import importlib
import pkgutil
from types import ModuleType
from typing import Iterable


# Inspired by https://github.com/python-discord/bot/blob/master/bot/utils/extensions.py

def unqualify(name: str) -> str:
    return name.rsplit('.', maxsplit=1)[-1]


def modules_to_str(modules: Iterable[ModuleType]):
    return ', '.join(unqualify(m.__name__) for m in modules)


def auto_import(package, *args):
    modules = set()
    skipped = set()

    for module in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
        if unqualify(module.name).startswith('_'):
            continue  # skip the file if it starts with an _

        if module.ispkg:
            continue  # skip folders

        module = importlib.import_module(module.name)
        if hasattr(module, 'setup'):
            module.setup(*args)
            modules.add(module)
        else:
            skipped.add(module)

    print(f'Imported {modules_to_str(modules)}')
    if skipped:  # this shouldn't be true
        print(f'Skipped {modules_to_str(skipped)}')

    return modules