# Bash shell colors
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


OPTIONS: str = "m:d:l:yh"
LONG_OPTIONS: list[str] = ["minterms=", "dontcares=", "labels=", "yes", "help"]
ALLOWED_EXTENSIONS: list[str] = [".txt", ".md", ".tsv", ".csv"]
USAGE_TEXT: str = "[USAGE]"