#!/usr/bin/env python3
"""
MODULE DATA
"""

import os
import math
import sys
import getopt
import re

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
            print("Overwrite output file if it exists")
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

    print(outputData)


def resolve_input_file_path(inputFilePath):
    inputFilePath = os.path.expanduser(inputFilePath)
    resolvedPath = os.path.abspath(inputFilePath)
    file = os.path.basename(resolvedPath)
    if not os.path.isfile(resolvedPath):
        raise FileNotFoundError(f"File not found: {resolvedPath}")    
    return file


def sanitize_input(inputFilePath):

    file = resolve_input_file_path(inputFilePath)

    sanitizedInput = []

    with open(file, "r") as f:
        for line in f:
            cleanLine = re.split(r"[,\t ]", line.strip())
            sanitizedInput.append(cleanLine)

    if len(sanitizedInput) == 0:
        raise ValueError(f"Input file contains no content.")
    elif len(sanitizedInput) == 1:
        raise ValueError(f"Input file does not contain a valid truth table. Each row must be separated by a new line.")
    
    # Remove header label row if it exists
    if sanitizedInput[0][0] not in {0, 1, "x"}:
        sanitizedInput.pop(0)

    # Remove row labels if they exist (assuming that if the first column is not 01x, all rows are labeled)
    if sanitizedInput[0][0] not in {0, 1, "x"}:
        for row in sanitizedInput:
            row.pop(0)

    rowLength = len(sanitizedInput[0])
    for row in sanitizedInput:
        if len(row) != rowLength:
            raise ValueError("Table is not complete.")    

    return sanitizedInput


def set_output_file_path(outputFilePath, outputFileExtension, overwriteFile):
    
    file = None

    if outputFilePath is None:
        file = "qm_truth_table" + outputFileExtension
        outputFilePath = file

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
    return inputData

if __name__ == "__main__":
    """
    try:
        parse_options()
    except Exception as e:
        print(f"\033[91mError: {e}\033[0m")
    """
    parse_options()