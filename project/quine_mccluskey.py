#!/usr/bin/env python3
"""
MODULE DATA
"""

import os
import math
import sys
import getopt
from pprint import pformat, pprint
from logging import *
from typing import Any, List, Dict, Optional
from collections import defaultdict
import logger_setup as _
from sanitize_qm_input import sanitize_input

logger = getLogger(__name__)

# Define global constants
OPTIONS: str = "yh"
LONG_OPTIONS: List[str] = ["yes", "help"]
ALLOWED_EXTENSIONS: List[str] = [".txt", ".md", ".tsv", ".csv"]
USAGE_TEXT: str = "[USAGE]"

BLACK   = "\033[30m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"
WHITE   = "\033[37m"
BRIGHT_RED = "\033[91m"

BG_YELLOW = "\033[43m"
BG_BLUE   = "\033[44m"

RESET = "\033[0m"


logger.info(f"{CYAN}----------------------------------------------------------------------------------------------------------------------------------\n----------------------------------------------------------------------------------------------------------------------------------\n----------------------------------------------------------------------------------------------------------------------------------{RESET}")


def parse_options() -> None:
    argumentList: List[str] = sys.argv[1:]
    try:
        options, arguments = getopt.getopt(argumentList, OPTIONS, LONG_OPTIONS)
    except getopt.GetoptError as e:
        print(str(e))
        sys.exit(1)
    
    parsed: Dict[str, bool] = {
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

    argumentCount: int = len(arguments)
    if argumentCount == 0:
        raise SyntaxError(f"No input file specified. {USAGE_TEXT}")
    elif argumentCount > 2:
        raise SyntaxError(f"Too many arguments passed. {USAGE_TEXT}")

    inputFilePath: str = arguments[0]
    _, fileExtension = os.path.splitext(inputFilePath)
    if fileExtension.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Filetype {fileExtension} not supported, must be one of: {ALLOWED_EXTENSIONS}")
    inputData: List[List[Any]] = sanitize_input(inputFilePath)

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


    logger.verbose(f"Final input data:\n{pformat(inputData)}")

    mintermTableIndex: List[List[int]]
    mintermTable: List[List[any]] 
    mintermTableIndex, mintermTable = generate_minterm_table_index(inputData)

    print(mintermTable)

    combinedMintermTableAndIndex: List[List[List[Any]]] = [[] for _ in mintermTableIndex]

    #for idx in range(len(mintermTableIndex)):
        #for idy in mintermTableIndex[idx]:
            #mintermTable[idx].append(inputData[idy])

    for idx, itemX in enumerate(mintermTableIndex):
        for idy, itemY in enumerate(itemX):
            combinedTerm: List[Any] = [itemY] + mintermTable[idx][idy]
            combinedMintermTableAndIndex[idx].append(combinedTerm)

    logger.verbose(f"{RESET}Combined table:\n{pformat(combinedMintermTableAndIndex)}{RESET}")

    primeImplicants: List[List[Any]] = recursive_generate_prime_implicants(combinedMintermTableAndIndex)

    logger.debug(f"Final list of all prime implicants:\n{primeImplicants}")

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

    return mintermTableIndex, mintermTable


def recursive_generate_prime_implicants(
        combinedMintermTableAndIndex: List[List[List[Any]]],
        recursionLevel: int = 1
    ) -> tuple[Optional[List[List[Any]]], Optional[List[List[Any]]]]:

    tableLength: int = len(combinedMintermTableAndIndex)
    #disregardedBitCount = int(math.pow(recursionLevel, 2))
    binaryValue: str = ""
    for idx in range(recursionLevel):
        binaryValue += "1" if idx == 0 else "0"
    binaryValue = int(binaryValue, 2)
    disregardedBitCount = binaryValue

    logger.debug(f"{RED}Recursion level: {recursionLevel}")
    logger.debug(f"Disregarde bit count: {disregardedBitCount}")
    logger.debug(f"Combined minterm table:\n{pformat(combinedMintermTableAndIndex)}")
    logger.debug(f"Minterm table length: {tableLength}{RESET}")

    if tableLength <= 1:

        logger.verbose(f"{GREEN}Minterm table length ({tableLength}) is insufficient for combining terms, returning it:\n{combinedMintermTableAndIndex}\n{RESET}")

        return (combinedMintermTableAndIndex)
    
    primeImplicants: List[List[Any]] = [[]]

    newTerms: int = 0
    i: int = 0
    while True:

        logger.verbose(f"i: {i}")

        groupOne: List[Any] = combinedMintermTableAndIndex[i]
        groupTwo: List[Any] = combinedMintermTableAndIndex[i + 1]


        logger.verbose(f"Group one: {groupOne}\nGroup two: {groupTwo}")

        for tOneIndex, termOne in enumerate(groupOne):
            for tTwoIndex, termTwo in enumerate(groupTwo):


                mintermOne: List[any] = termOne[disregardedBitCount:-1]
                mintermTwo: List[any]  = termTwo[disregardedBitCount:-1]
                termOneMIndex: List[int] = termOne[:disregardedBitCount]
                termTwoMIndex: List[int] = termTwo[:disregardedBitCount]
                combinedTermIndex: List[int] = termOneMIndex + termTwoMIndex
                termOneOperand: any = termOne[-1]
                termTwoOperand: any = termTwo[-1]
                mintermOperand: List[any] = ["x"] if termOneOperand != 1 and termTwoOperand != 1 else [1]

                logger.verbose(f"""T1 index: {tOneIndex}
Term one: {termOne}
-> minified: {mintermOne}
Term one ms: {termOneMIndex}
T2 index: {tTwoIndex}
Term two: {termTwo}
-> minified: {mintermTwo}
Term two ms: {termTwoMIndex}
Combined ms: {combinedTermIndex}
Final operand: {mintermOperand}""")

                newTerm: List[Any] = mintermOne.copy()

                logger.verbose(f"New term copy: {newTerm}")

                differingBit: bool = False
                for y in range(len(newTerm)):
                    if mintermOne[y] != mintermTwo[y]:
                        if differingBit or mintermOne[y] == "-" or mintermTwo[y] == "-":
                            newTerm = None  # type: ignore
                        elif newTerm:
                            logger.verbose(f"Newterm about to be modified: {newTerm}")
                            newTerm[y] = "-"
                            differingBit = True
                        else: break
                if newTerm:

                    combinedNewTerm: List[any] = combinedTermIndex + newTerm + mintermOperand
                    logger.verbose(f"New term:\n{newTerm}\nCombined new term: {combinedNewTerm}")

                    try:

                        logger.verbose(f"{CYAN}Try to append `{newTerm}` to:\n{pformat(primeImplicants[i])}{RESET}")

                        primeImplicants[i].append(combinedNewTerm)
                    except:
                        logger.verbose(f"{RED}EXCEPTION{RESET}")
                        primeImplicants.append([])
                        primeImplicants[i].append(combinedNewTerm)
                    
                    newTerms += 1

                    logger.verbose(f"Current prime implicants:\n{pformat(primeImplicants)}")
            
        i += 1
        if i == tableLength - 1:
            break
    

    if newTerms != 0:
        if len(primeImplicants) <= 1:

            logger.verbose(f"{GREEN}Prime implicants (returning this):\n{primeImplicants}{RESET}")

            return primeImplicants
        else:

            logger.verbose(f"{YELLOW}Going deeper with these prime implicants:\n{primeImplicants}{RESET}")

            return recursive_generate_prime_implicants(primeImplicants, recursionLevel + 1)
    else:
        logger.verbose(f"{GREEN}Reached the end of the function with these prime implicants, returning them:\n{primeImplicants}{RESET}")
        return primeImplicants
    
    #return recursive_generate_prime_implicants(primeImplicants, primeImplicantTableIndex, recursionLevel + 1)


if __name__ == "__main__":
    """
    try:
        parse_options()
    except Exception as e:
        print(f"\033[91mError: {e}\033[0m")
    """
    parse_options()