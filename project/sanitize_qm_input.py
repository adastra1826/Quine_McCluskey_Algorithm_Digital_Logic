import os
import re
import math
from pprint import pformat
from logging import *

logger = getLogger(__name__)


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
    maxBinaryValue = ""
    for _ in range(rowLength - 1):
        maxBinaryValue += "1"
    maxBinaryValue = int(maxBinaryValue, 2)
    maxRows = maxBinaryValue + 1
    
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

    logger.verbose(f"Sorted input data:\n{pformat(sortedInput)}")
    
    # Generate missing rows (as "don't care" minterms)
    if numRows < maxRows:
        logger.verbose(f"Actual rows: {numRows}\nMax rows:    {maxRows}")
        sortedInput = generate_missing_rows(sortedInput, maxRows)

    logger.debug(f"Final list:\n{pformat(sortedInput)}")
    return sortedInput


def resolve_input_file_path(inputFilePath):
    inputFilePath = os.path.expanduser(inputFilePath)
    resolvedPath = os.path.abspath(inputFilePath)
    if not os.path.isfile(resolvedPath):
        raise FileNotFoundError(f"File not found: {resolvedPath}")    
    return resolvedPath


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

            logger.verbose(f"Missing row at index {incompleteDataRowIndex}: {missingRow}")
            
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
