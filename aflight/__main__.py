import os
import sys
import traceback

import click

app_paths = ("app.py", "aflight.py")


class NoAppException(click.UsageError):
    pass


class Cli:
    def __init__(self):
        self.workdir = os.getcwd()
        self._loaded_app = None

    def main(self):
        app = self.load_app()
        app.serve()

    def load_app(self):
        if self._loaded_app:
            return self._loaded_app

        app = None
        for path in app_paths:
            import_name = prepare_import(path)
            app = locate_app(import_name, raise_if_not_found=False)

            if app:
                break

        if not app:
            raise NoAppException(
                "Could not locate an Aflight application. "
                "Use the 'app.py' file in the current directory."
            )

        self._loaded_app = app
        return app


def prepare_import(path):
    """Given a filename this will try to calculate the python path, add it
    to the search path and return the actual module name that is expected.
    """
    path = os.path.realpath(path)

    fname, ext = os.path.splitext(path)
    if ext == ".py":
        path = fname

    if os.path.basename(path) == "__init__":
        path = os.path.dirname(path)

    module_name = []

    # move up until outside package structure (no __init__.py)
    while True:
        path, name = os.path.split(path)
        module_name.append(name)

        if not os.path.exists(os.path.join(path, "__init__.py")):
            break

    if sys.path[0] != path:
        sys.path.insert(0, path)

    return ".".join(module_name[::-1])


def locate_app(module_name, raise_if_not_found=True):
    try:
        __import__(module_name)
    except ImportError:
        # Reraise the ImportError if it occurred within the imported module.
        # Determine this by checking whether the trace has a depth > 1.
        if sys.exc_info()[2].tb_next:
            raise NoAppException(
                f"While importing {module_name!r}, an ImportError was"
                f" raised:\n\n{traceback.format_exc()}"
            ) from None
        elif raise_if_not_found:
            raise NoAppException(f"Could not import {module_name!r}.") from None
        else:
            return

    module = sys.modules[module_name]

    return find_best_app(module)


def find_best_app(module):
    """Given a module instance this tries to find the best possible
    application in the module or raises an exception.
    """
    from . import Aflight

    # Search for the most common names first.
    for attr_name in ("app", "application"):
        app = getattr(module, attr_name, None)

        if isinstance(app, Aflight):
            return app

    # Otherwise find the only object that is an Aflight instance.
    matches = [v for v in module.__dict__.values() if isinstance(v, Aflight)]

    if len(matches) > 0:
        return matches[0]

    raise NoAppException(
        "Failed to find Aflight application in module"
        f" '{module.__name__}'."
    )


def main():
    cli = Cli()
    cli.main()


if __name__ == "__main__":
    main()
