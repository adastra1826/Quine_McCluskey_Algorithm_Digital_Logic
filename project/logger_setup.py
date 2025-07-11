from logging import *
from global_constants import *

VERBOSE = 5

LEVEL_DEFAULTS = {
    VERBOSE: WHITE,
    DEBUG: WHITE,
    INFO: GREEN,
    WARNING: YELLOW,
    ERROR: BG_RED + WHITE
}


def make_colored_method(level_no):
    def fn(self, msg, *args, color=None, **kwargs):
        if not self.isEnabledFor(level_no):
            return
        color = color or LEVEL_DEFAULTS.get(level_no, RESET)
        extra = kwargs.setdefault("extra", {})
        extra["color"] = color
        kwargs.setdefault("stacklevel", 2)
        self.log(level_no, msg, *args, **kwargs)
    return fn


class ColorFormatter(Formatter):
    def format(self, record):
        color = getattr(record, "color", RESET)
        record.msg = f"{color}{record.getMessage()}{RESET}"
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

getLogger("quine_mccluskey").setLevel(VERBOSE)
getLogger("sanitize_qm_input").setLevel(WARNING)
getLogger("generate_prime_implicants").setLevel(DEBUG)
getLogger("generate_missing_rows").setLevel(DEBUG)
getLogger("parse_sum_of_products_input").setLevel(VERBOSE)