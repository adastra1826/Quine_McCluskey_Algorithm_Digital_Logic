#!/usr/bin/env python3
"""
MODULE DATA
"""

from global_constants import *

import logger_setup
import os
import sys
import getopt
from pprint import pformat, pprint
from logging import getLogger
from typing import Optional
from sanitize_qm_input import sanitize_file_input
from generate_prime_implicants import recursive_generate_prime_implicants
from parse_sum_of_products_input import parse_sop_input

logger = getLogger("quine_mccluskey")

logger.info(f"----------------------------------------------------------------------------------------------------------------------------------\n----------------------------------------------------------------------------------------------------------------------------------\n----------------------------------------------------------------------------------------------------------------------------------", color = RED)


def parse_options() -> None:
    argumentlist: list[str] = sys.argv[1:]
    try:
        options, arguments = getopt.getopt(argumentlist, OPTIONS, LONG_OPTIONS)
    except getopt.GetoptError as e:
        print(str(e))
        sys.exit(1)
    
    parsed: dict[str, bool] = {
        "overwrite": False,
        "help": False
    }

    optionArguments: dict[str, Optional[str]] = {
        "minterms": None,
        "dontcares": None,
        "labels": None
    }

    for argument, value in options:
        if argument in ("-m", "--minterms"):
            optionArguments["minterms"] = value
            logger.debug(f"Minterms specified")
        elif argument in ("-d", "--dontcares"):
            optionArguments["dontcares"] = value
            logger.debug(f"Don't cares specified")
        elif argument in ("-l", "labels="):
            optionArguments["labels"] = value
            logger.debug(f"Labels specified")
        elif argument in ("-y", "--yes"):
            parsed["overwrite"] = True
            logger.debug(f"OVerwrite output file specified")
        elif argument in ("-h", "--help"):
            parsed["help"] = True
            logger.debug(f"Help specified")

    if parsed["help"]:
        print(f"Sending help")
        sys.exit(0)

    argumentCount: int = len(arguments)
    sanitizedInputData: Optional[list[list[any]]] = None

    if argumentCount > 2:
        raise SyntaxError(f"Too many arguments passed.\n{USAGE_TEXT}")

    if optionArguments["minterms"]:
        if argumentCount == 2:
            raise SyntaxError(f"You cannot specify both an input file and minterms.\n{USAGE_TEXT}")
        sanitizedInputData = parse_sop_input(optionArguments["minterms"], optionArguments["dontcares"])
    else:
        if argumentCount == 0:
            raise SyntaxError(f"No input file specified.\n{USAGE_TEXT}")

        inputFilePath: str = arguments[0]
        _, fileExtension = os.path.splitext(inputFilePath)
        if fileExtension.lower() not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Filetype {fileExtension} not supported, must be one of: {ALLOWED_EXTENSIONS}")
        sanitizedInputData = sanitize_file_input(inputFilePath)

    outputLocation: Optional[str] = None
    if argumentCount == 2:
        outputLocation = set_output_file_path(arguments[1], fileExtension, parsed["overwrite"])
    if sanitizedInputData:
        outputData: list[list[any]] = quine_mccluskey(sanitizedInputData)
    else:
        raise RuntimeError(f"This should never happen. Internal script error.")


def set_output_file_path(
        outputFilePath: str,
        outputFileExtension: str,
        overwriteFile: bool
    ) -> str:

    file: Optional[str] = None

    outputFilePath = os.path.expanduser(outputFilePath)
    resolvedPath = os.path.abspath(outputFilePath)
    file = os.path.basename(resolvedPath)
    fileName, fileExtension = os.path.splitext(file)

    if fileExtension.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Filetype {fileExtension} not supported, must must be one of: {ALLOWED_EXTENSIONS}")
    
    if os.path.exists(outputFilePath) and not overwriteFile:
        userInput: str = input(f"\033[33mWARNING: A file with the name \033[0m`{file}`\033[33m already exists at that location. Overwrite? (\033[31my\033[33m/\033[32mn\033[33m): \033[0m") + " "
        while userInput[0].lower() not in ["y", "n", "q"]:
            userInput = input("\033[33mInvalid input. Please enter \033[31my \033[33mor \033[32mn \033[33m(or \033[0mq \033[33mto stop): \033[0m") + " "
        if userInput[0].lower() == "q":
            sys.exit(0)
        elif userInput[0].lower() == "n":
            iteration: int = 1
            while True:
                appendText = f"_{iteration}"
                tempFile = fileName + appendText + fileExtension
                if not os.path.exists(tempFile):
                    file = tempFile
                    print(f"Output file: {file}")
                    break
                iteration += 1
                if iteration >= 999:
                    raise FileExistsError(f"Maximum number of possible file rename checks reached (999). Please choose a different name for the output file with the `-o filename.extension` flag.")
    
    return os.path.join(os.path.dirname(resolvedPath), file)  # type: ignore


def quine_mccluskey(
        completeImplicantTable: list[list[any]]
    ) -> list[list[any]]:

    logger.info(f"Sanitized input data:\n{pformat(completeImplicantTable)}")

    mintermLength = len(completeImplicantTable[0]) - 2

    primeImplicants: list[list[any]] = recursive_generate_prime_implicants(completeImplicantTable, mintermLength)

    logger.info(f"Prime implicants:\n{primeImplicants}")

    return completeImplicantTable


if __name__ == "__main__":
    """
    try:
        parse_options()
    except Exception as e:
        print(f"\033[91mError: {e}\033[0m")
    """
    parse_options()