import logging
from sys import stderr

from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text

LOG_FORMAT = "%(message)s"


# uses the new markup API/param in Handler
# https://github.com/willmcgugan/rich/issues/171
HANDLERS = [
    RichHandler(
        console=Console(file=stderr), markup=True, show_level=False, show_path=False
    )
]
logging.basicConfig(
    datefmt="[%X]", format=LOG_FORMAT, handlers=HANDLERS, level="DEBUG",
)


class MyLogger(object):
    def __init__(self, loglib="rich", **kwargs):
        self.logg = logging.getLogger(loglib)

    def get_level(self):
        return self.logg.level

    def setLevel(self, level):
        #  TODO: figure out why `self.logg.setLevel(level)` doesn't do what I want
        logging.getLogger().setLevel(level)

    class Decorators(object):
        @classmethod
        def _fmt(cls, decorated):
            def wrap(cls, *args, **kwargs):
                if len(args) == 1:
                    msg = args[0]
                else:
                    msg = " ".join(str(a) for a in args)

                if kwargs.get("label"):
                    label = "[purple on yellow]" + kwargs.pop("label") + "[/]"
                    msg = f"{label}: {msg}"
                decorated(cls, msg, **kwargs)

            return wrap

    @Decorators._fmt
    def debug(self, *args, **kwargs):
        self.logg.debug(*args, **kwargs)

    @Decorators._fmt
    def info(self, *args, **kwargs):
        self.logg.info(*args, **kwargs)

    @Decorators._fmt
    def warning(self, *args, **kwargs):
        self.logg.warning(*args, **kwargs)

    @Decorators._fmt
    def error(self, *args, **kwargs):
        self.logg.error(*args, **kwargs)

    @Decorators._fmt
    def critical(self, *args, **kwargs):
        self.logg.critical(*args, **kwargs)


mylogger = MyLogger()
