#!/usr/bin/env python3
"""
MODULE DATA
"""

import os
import math
import sys
import getopt
import re
from pprint import pformat, pprint
from logging import *
import logger_setup
from sanitize_qm_input import sanitize_file_input

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
    inputData = sanitize_file_input(inputFilePath)

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


def quine_mccluskey(inputData: list[list[any]]):

    mintermTableIndex = generate_minterm_table_index(inputData)

    mintermTable = [[] for _ in mintermTableIndex]

    for i in range(len(mintermTableIndex)):
        for y in mintermTableIndex[i]:
            mintermTable[i].append(inputData[y[0]][:-1])

    logger.debug(f"Minterm table:\n{pformat(mintermTable)}")

    primeImplicants = recursive_generate_prime_implicants(mintermTable, mintermTableIndex)

    logger.debug(f"Prime implicants:\n{primeImplicants}")

    return inputData


def generate_minterm_table_index(inputData):
    mintermLength = len(inputData[0])
    mintermTableIndex = [[] for _ in range(mintermLength)]

    for i, row in enumerate(inputData):
        outputBit = row[mintermLength - 1]
        if outputBit in {1, "x"}:
            numOnes = 0
            for bit in row[:len(row) - 1]:
                if bit == 1: numOnes += 1
            requiredBit = True if outputBit == 1 else False
            mintermTableIndex[numOnes].append([i, requiredBit]) # or 

    logger.debug(f"Minterm table index:\n{pformat(mintermTableIndex)}")

    return mintermTableIndex


def recursive_generate_prime_implicants(mintermTable, mintermTableIndex, recursionLevel = 0):

    logger.debug(f"Recursion level: {recursionLevel}")
    logger.debug(f"Minterm table:\n{pformat(mintermTable)}")
    logger.debug(f"Minterm table index:\n{pformat(mintermTableIndex)}")

    tableLength = len(mintermTable)
    if tableLength <= 1:
        return mintermTable
    
    primeImplicants = [[] for _ in range(tableLength)]
    primeImplicantTableIndex = [[] for _ in range(tableLength)]

    
    
    i = 0
    while True:

        groupOne = mintermTable[i]
        groupTwo = mintermTable[i + 1]
        newTerms = 0

        logger.verbose(f"i: {i}\nGroup one: {groupOne}\nGroup two: {groupTwo}")

        for tOneIndex, termOne in enumerate(groupOne):
            for tTwoIndex, termTwo in enumerate(groupTwo):

                logger.verbose(f"T1 index: {tOneIndex}\nTerm one: {termOne}\nT2 index: {tTwoIndex}\nTerm two: {termTwo}")

                newTerm = termOne.copy()
                differingBit = False
                for y in range(len(termOne)):
                    if termOne[y] != termTwo[y]:
                        if differingBit or termOne[y] == "-" or termTwo[y] == "-":
                            newTerm = None
                        else:
                            newTerm[y] = "-"
                            differingBit = True
                if newTerm:
                    logger.verbose(f"New term:\n{newTerm}")
                    primeImplicants[i].append(newTerm)
                    primeImplicantTableIndex[i].append( [mintermTableIndex[i][tOneIndex], mintermTableIndex[i][tTwoIndex]] )
                    newTerms += 1

                    logger.verbose(f"Current prime implicants:\n{pformat(primeImplicants)}")
                    logger.verbose(f"Current prime implicant table index:\n{pformat(primeImplicantTableIndex)}")
        
        if newTerms > 1:
            pass
            #primeImplicants.append(recursive_generate_prime_implicants(primeImplicants, primeImplicantTableIndex, recursionLevel + 1))
                        


        i += 1
        if i == tableLength:
            break


if __name__ == "__main__":
    """
    try:
        parse_options()
    except Exception as e:
        print(f"\033[91mError: {e}\033[0m")
    """
    parse_options()
