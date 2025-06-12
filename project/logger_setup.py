from logging import *

VERBOSE = 5
addLevelName(VERBOSE, "VERBOSE")
def verbose(self, msg, *args, **kwargs):
    if self.isEnabledFor(VERBOSE):
        kwargs.setdefault("stacklevel", 2)
        self._log(VERBOSE, msg, args, **kwargs)
Logger.verbose = verbose

basicConfig(
    level = VERBOSE,
    format = "%(levelname)s [%(module)s:%(funcName)s]:\n%(message)s\n"
)

getLogger("sanitize_qm_input").setLevel(WARNING)
getLogger("quine_mccluskey").setLevel(VERBOSE)
