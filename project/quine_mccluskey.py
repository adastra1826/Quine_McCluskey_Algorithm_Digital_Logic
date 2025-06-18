#!/usr/bin/env python3
"""
MODULE DATA
"""

import logger_setup
import os
import sys
import getopt
from pprint import pformat, pprint
import logging
from typing import Any, List, Dict, Optional
import logger_setup as _
from sanitize_qm_input import sanitize_file_input
from generate_prime_implicants import recursive_generate_prime_implicants

logger = logging.getLogger("quine_mccluskey")

# Define global constants
OPTIONS: str = "m:d:yh"
LONG_OPTIONS: List[str] = ["minterms=", "dontcares=", "yes", "help"]
ALLOWED_EXTENSIONS: List[str] = [".txt", ".md", ".tsv", ".csv"]
USAGE_TEXT: str = "[USAGE]"


logger.info(f"----------------------------------------------------------------------------------------------------------------------------------\n----------------------------------------------------------------------------------------------------------------------------------\n----------------------------------------------------------------------------------------------------------------------------------")


def parse_options() -> None:
    argumentList: List[str] = sys.argv[1:]
    try:
        options, arguments = getopt.getopt(argumentList, OPTIONS, LONG_OPTIONS)
    except getopt.GetoptError as e:
        print(str(e))
        sys.exit(1)
    
    parsed: Dict[str, bool] = {
        "minterms": False,
        "dontcares": False,
        "overwrite": False,
        "help": False
    }

    for argument, value in options:
        if argument in ("-m", "--minterms"):
            parsed["minterms"] = True
            logger.debug(f"Minterms specified")
        elif argument in ("-d", "--dontcares"):
            parsed["dontcares"] = True
            logger.debug(f"Don't cares specified")
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
    if argumentCount == 0:
        raise SyntaxError(f"No input file specified. {USAGE_TEXT}")
    elif argumentCount > 2:
        raise SyntaxError(f"Too many arguments passed. {USAGE_TEXT}")

    inputFilePath: str = arguments[0]
    _, fileExtension = os.path.splitext(inputFilePath)
    if fileExtension.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Filetype {fileExtension} not supported, must be one of: {ALLOWED_EXTENSIONS}")
    inputData: List[List[Any]] = sanitize_file_input(inputFilePath)

    outputLocation: Optional[str] = None
    if argumentCount == 2:
        outputLocation = set_output_file_path(arguments[1], fileExtension, parsed["overwrite"])

    outputData: List[List[Any]] = quine_mccluskey(inputData)


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
        inputData: List[List[Any]]
    ) -> List[List[Any]]:


    logger.info(f"Sanitized input data:\n{pformat(inputData)}")

    mintermTableIndex: List[List[int]]
    mintermTable: List[List[any]] 
    mintermTableIndex, mintermTable = generate_minterm_table_index(inputData)
    mintermLength = len(inputData[0]) - 1

    initialCombinedMintermTableAndIndex: List[List[List[Any]]] = [[] for _ in mintermTableIndex]

    for idx, itemX in enumerate(mintermTableIndex):
        for idy, itemY in enumerate(itemX):
            combinedTerm: List[Any] = [itemY] + mintermTable[idx][idy]
            initialCombinedMintermTableAndIndex[idx].append(combinedTerm)


    combinedMintermTableAndIndex: List[List[List[Any]]] = []

    for group in initialCombinedMintermTableAndIndex:
        if len(group) != 0:
            combinedMintermTableAndIndex.append(group)

    logger.verbose(f"Combined table:\n{pformat(combinedMintermTableAndIndex)}")

    primeImplicants: List[List[Any]] = recursive_generate_prime_implicants(combinedMintermTableAndIndex, mintermLength)

    logger.info(f"Prime implicants:\n{primeImplicants}")

    return inputData


def generate_minterm_table_index(
        inputData: List[List[Any]]
    ) -> tuple[List[List[int]], List[List[any]]]:
    
    mintermLength: int = len(inputData[0])
    mintermTableIndex: List[List[int]] = [[] for _ in range(mintermLength)]
    mintermTable: List[List[int]] = [[] for _ in range(mintermLength)]

    for i, row in enumerate(inputData):
        outputBit = row[mintermLength - 1]
        if outputBit in {1, "x"}:
            numOnes: int = 0
            for bit in row[:len(row) - 1]:
                if bit == 1:
                    numOnes += 1
            mintermTableIndex[numOnes].append(i)
            mintermTable[numOnes].append(row)

    logger.debug(f"Minterm table index:\n{pformat(mintermTableIndex)}")
    logger.debug(f"Minterm table:\n{pformat(mintermTable)}")

    return mintermTableIndex, mintermTable


if __name__ == "__main__":
    """
    try:
        parse_options()
    except Exception as e:
        print(f"\033[91mError: {e}\033[0m")
    """
    parse_options()