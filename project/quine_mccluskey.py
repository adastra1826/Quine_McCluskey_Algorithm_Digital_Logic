#!/usr/bin/env python3
"""
MODULE DATA
"""

import os
import math
import sys
import getopt
import re
from pprint import pformat
from logging import *
from sanitize_qm_input import sanitize_input

# Set up logger
VERBOSE = 5
addLevelName(VERBOSE, "VERBOSE")
def verbose(self, message, *args, **kwargs):
    if self.isEnabledFor(VERBOSE):
        self._log(VERBOSE, message, args, **kwargs)
Logger.verbose = verbose
basicConfig(
    level=DEBUG,
    format="%(levelname)s [%(funcName)s]: %(message)s"
)
logger = getLogger(__name__)

# Define global constants
OPTIONS = "yh"
LONG_OPTIONS = ["yes", "help"]
ALLOWED_EXTENSIONS = [".txt", ".md", ".tsv", ".csv"]
USAGE_TEXT = "[USAGE]"

def parse_options():
    
    argumentList = sys.argv[1:]
    try:
        options, arguments = getopt.getopt(argumentList, OPTIONS, LONG_OPTIONS)
    except getopt.GetoptError as e:
        print(str(e))
        sys.exit(1)
    
    parsed = {
        "overwrite": False,
        "help": False
    }

    for argument, value in options:
        if argument in ("-y", "--yes"):
            parsed["overwrite"] = True
            log(INFO, "Overwrite output file if it exists")
        elif argument in ("-h", "--help"):
            parsed["help"] = True

    if parsed["help"]:
        print(f"Sending help")
        sys.exit(0)

    argumentCount = len(arguments)
    if argumentCount == 0:
        raise SyntaxError(f"No input file specified. {USAGE_TEXT}")
    elif argumentCount > 2:
        raise SyntaxError(f"Too many arguments passed. {USAGE_TEXT}")

    inputFilePath = arguments[0]
    _, fileExtension = os.path.splitext(inputFilePath)
    if fileExtension.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Filetype {fileExtension} not supported, must be one of: {ALLOWED_EXTENSIONS}")
    inputData = sanitize_input(inputFilePath)

    outputLocation = None
    if argumentCount == 2:
        outputLocation = set_output_file_path(arguments[1], fileExtension, parsed["overwrite"])

    outputData = quine_mccluskey(inputData)


def set_output_file_path(outputFilePath, outputFileExtension, overwriteFile):
    
    file = None

    outputFilePath = os.path.expanduser(outputFilePath)
    resolvedPath = os.path.abspath(outputFilePath)
    file = os.path.basename(resolvedPath)
    fileName, fileExtension = os.path.splitext(file)

    if fileExtension.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Filetype {fileExtension} not supported, must must be one of: {ALLOWED_EXTENSIONS}")
    
    if os.path.exists(outputFilePath) and not overwriteFile:
        userInput = input(f"\033[33mWARNING: A file with the name \033[0m`{file}`\033[33m already exists at that location. Overwrite? (\033[31my\033[33m/\033[32mn\033[33m): \033[0m") + " "
        while userInput[0].lower() not in ["y", "n", "q"]:
            userInput = input("\033[33mInvalid input. Please enter \033[31my \033[33mor \033[32mn \033[33m(or \033[0mq \033[33mto stop): \033[0m") + " "
        if userInput[0].lower() == "q":
            sys.exit(0)
        elif userInput[0].lower() == "n":
            iteration = 1
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
    
    return os.path.join(os.path.dirname(resolvedPath), file)


def quine_mccluskey(inputData):

    mintermTableIndex = generate_minterm_table_index(inputData)

    return inputData

def generate_minterm_table_index(inputData):
    mintermLength = len(inputData[0])
    mintermTableIndex = [[] for _ in range(mintermLength)]

    for i, row in enumerate(inputData):
        if row[mintermLength - 1] in {1, "x"}:
            numOnes = 0
            for bit in row[:len(row) - 1]:
                if bit == 1: numOnes += 1            
            mintermTableIndex[numOnes].append(i)

    logger.debug(f"Minterm table:\n{pformat(mintermTableIndex)}")

    return mintermTableIndex




if __name__ == "__main__":
    """
    try:
        parse_options()
    except Exception as e:
        print(f"\033[91mError: {e}\033[0m")
    """
    parse_options()