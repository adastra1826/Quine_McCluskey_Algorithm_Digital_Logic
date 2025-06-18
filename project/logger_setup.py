from logging import *

BLACK: str      = "\033[30m"
RED: str        = "\033[31m"
GREEN: str      = "\033[32m"
YELLOW: str     = "\033[33m"
BLUE: str       = "\033[34m"
MAGENTA: str    = "\033[35m"
CYAN: str       = "\033[36m"
WHITE: str      = "\033[37m"
BRIGHT_RED: str = "\033[91m"

BG_YELLOW: str  = "\033[43m"
BG_BLUE: str    = "\033[44m"
BG_RED: str     = "\x1b[41m"

RESET = "\033[0m"

VERBOSE = 5

LEVEL_DEFAULTS = {
    VERBOSE: WHITE,
    DEBUG: CYAN,
    INFO: GREEN,
    WARNING: YELLOW,
    ERROR: BG_RED + WHITE
}

def make_colored_method(level_no):
    def fn(self, msg, *args, color=None, **kwargs):
        if not self.isEnabledFor(level_no):
            return
        col = color or LEVEL_DEFAULTS.get(level_no, RESET)
        extra = kwargs.setdefault("extra", {})
        extra["color"] = col
        kwargs.setdefault("stacklevel", 2)
        self.log(level_no, msg, *args, **kwargs)
    return fn


class ColorFormatter(Formatter):
    def format(self, record):
        col = getattr(record, "color", RESET)
        record.msg = f"{col}{record.getMessage()}{RESET}"
        record.args = ()
        return super().format(record)
    

addLevelName(VERBOSE, "VERBOSE")
def verbose(self, msg, *args, **kwargs):
    if self.isEnabledFor(VERBOSE):
        kwargs.setdefault("stacklevel", 2)
        self._log(VERBOSE, msg, args, **kwargs)
Logger.verbose = verbose

for name, level in [
    ("debug", DEBUG),
    ("verbose", VERBOSE),
    ("info",  INFO),
    ("warning", WARNING),
    ("error", ERROR)
    ]:
    setattr(Logger, name, make_colored_method(level))


root = getLogger()
root.setLevel(DEBUG)

for handler in list(root.handlers):
    root.removeHandler(handler)

handler = StreamHandler()
handler.setFormatter(
    ColorFormatter("%(levelname)s [%(name)s:%(funcName)s]:\n%(message)s\n")
    )

root.addHandler(handler)

getLogger("sanitize_qm_input").setLevel(WARNING)
getLogger("generate_prime_implicants").setLevel(INFO)
getLogger("quine_mccluskey").setLevel(INFO)