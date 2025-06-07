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


def resolve_input_file_path(inputFilePath):
    inputFilePath = os.path.expanduser(inputFilePath)
    resolvedPath = os.path.abspath(inputFilePath)
    if not os.path.isfile(resolvedPath):
        raise FileNotFoundError(f"File not found: {resolvedPath}")    
    return resolvedPath


def sanitize_input(inputFilePath):

    file = resolve_input_file_path(inputFilePath)
    
    # Open source file, stream its contents while casting int strings to int type
    sanitizedInput = []
    with open(file, "r") as f:
        for line in f:
            splitData = re.split(r"[,\t ]", line.strip())
            integerCastedData = []
            for item in splitData:
                try:
                    integerValue = int(item)
                    integerCastedData.append(integerValue)
                except ValueError:
                    integerCastedData.append(item)
            sanitizedInput.append(integerCastedData)
        
    logger.info(f"Starting data:\n{pformat(sanitizedInput)}")

    numRows = len(sanitizedInput)

    if numRows == 0:
        raise ValueError(f"Input file contains no content.")
    elif numRows == 1:
        raise ValueError(f"Input file contains only one line. Each row must be separated by a new line.")

    # Remove header label row if it exists
    if sanitizedInput[0][0] not in {0, 1, "x"}:
        logger.info(f"Remove header row. Data at [1, 1] `{sanitizedInput[0][0]}` is not 0, 1, or x")
        sanitizedInput.pop(0)
        numRows -= 1

    # Remove row labels if they exist (assuming that if the first column is not 01x, all rows are labeled)
    if sanitizedInput[0][0] not in {0, 1, "x"}:
        logger.info(f"Remove first column. Data at [1, 1] `{sanitizedInput[0][0]}` is not 0, 1, or x")
        for row in sanitizedInput:
            row.pop(0)

    # Check row length and set maxRows after possibly removing header/label rows
    rowLength = len(sanitizedInput[0])
    maxRows = int(math.pow(rowLength - 1, 2))

    if rowLength >= 6:
        raise ValueError(f"DEBUG: Too many input rows.")
    
    if numRows > maxRows:
        raise ValueError(f"Input table contains {numRows} rows. Maximum number of rows for this table is {maxRows}. Remove duplicate or conflicting rows.")

    # Make sure all rows are same length and cells contain valid input
    for i, row in enumerate(sanitizedInput):
        if len(row) != rowLength:
            raise ValueError(f"Input table is malformed. Row {i + 1} is not the same length as row 1.")
        for y, cell in enumerate(row):
            if cell not in {0, 1, "x"}:
                raise ValueError(f"Table data in row {i + 1}, cell {y + 1} is invalid. `{cell}` is not 0, 1, or x")
            elif cell == "x" and y != rowLength - 1:
                raise ValueError(f"Table data in row {i + 1}, cell {y + 1} is invalid. `x` may only exist in last column.")
            
    sortedInput = recursive_binary_partition_sort(sanitizedInput)

    logger.debug(f"Sorted input data:\n{pformat(sortedInput)}")
    
    # Generate missing rows (as "don't care" minterms)
    if numRows < maxRows:
        sortedInput = generate_missing_rows(sortedInput, maxRows)

    logger.debug(f"Final list:\n{pformat(sortedInput)}")
    return sortedInput


def generate_missing_rows(incompleteData, maxRows):
    """
    Given `incomplete_data` (each row ending in a bit we don't care about here),
    which is already sorted by its integer value, fill in any missing binary rows up to `max_rows`.
    Returns a full list of rows, with newly created rows appended with "x".n 
    """
    
    completeData = []
    termLength = len(incompleteData[0]) - 1
    incompleteDataRowIndex = 0

    for rowIndex in range(maxRows):

        incompleteDataRow = incompleteData[incompleteDataRowIndex]
        dataBits = incompleteDataRow[:-1]
        bitString = "".join(map(str, dataBits))

        binaryValue = int(bitString, 2)

        if binaryValue != rowIndex:

            bits = bin(rowIndex)[2:].zfill(termLength)
            missingRow = [int(b) for b in bits] + ["x"]
            completeData.append(missingRow)

            logger.debug(f"Missing row at index {incompleteDataRowIndex}: {missingRow}")
            
        else:
            incompleteDataRowIndex += 1
            completeData.append(incompleteDataRow)
    
    return completeData


def recursive_binary_partition_sort(rows, col = 0):
    logger.verbose(f"Rows to sort by column {col}:\n{pformat(rows)}")

    if rows == []:
        logger.verbose(f"Missing row.")
        return []

    termMax = len(rows[0]) - 1
    sortedList = sorted(rows, key=lambda x: x[col])

    logger.verbose(f"Sorted rows:\n{pformat(sortedList)}")

    if col >= termMax or len(rows) <= 1:
        return sortedList
    
    zeroSubSplitList, oneSubSplitList = binary_split_nested_list(sortedList, col)

    zeroSubSortedList = recursive_binary_partition_sort(zeroSubSplitList, col + 1)
    oneSubSortedList = recursive_binary_partition_sort(oneSubSplitList, col + 1)
    return zeroSubSortedList + oneSubSortedList


def binary_split_nested_list(nestedList, index):
    zeroSubList = []
    oneSubList = []
    for i in nestedList:
        if i[index] == 0:
            zeroSubList.append(i)
        else:
            oneSubList.append(i)
    return zeroSubList, oneSubList


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

    #mintermTable = generate_minterm_table(inputData)




    return inputData

def generate_minterm_table(inputData):
    mintermLength = len(inputData[0]) - 1
    mintermTable = [[] for _ in range(mintermLength)]
    print(mintermLength, mintermTable)


if __name__ == "__main__":
    """
    try:
        parse_options()
    except Exception as e:
        print(f"\033[91mError: {e}\033[0m")
    """
    parse_options()