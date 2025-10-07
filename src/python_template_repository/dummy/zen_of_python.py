import contextlib
import io


def get_zen_of_python() -> str:
    """Return The Zen of Python.
    See https://www.python.org/dev/peps/pep-0020/
    """
    zen = io.StringIO()
    with contextlib.redirect_stdout(zen):
        import this  # Flake8 # noqa
    return zen.getvalue()
