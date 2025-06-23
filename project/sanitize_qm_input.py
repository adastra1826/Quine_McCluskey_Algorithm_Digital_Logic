import os
import re
from pprint import pformat
from logging import *
from generate_missing_rows import generate_missing_rows

logger = getLogger(__name__)


def sanitize_file_input(inputFilePath):

    file = resolve_input_file_path(inputFilePath)
    
    # Open source file, stream its contents while casting int strings to int type
    sanitizedInput: list[any] = []
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

    numRows: int = len(sanitizedInput)

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
        
    logger.debug(f"Original input:\n{pformat(sanitizedInput)}")

    sortedInput: list[list[any]] = recursive_binary_partition_sort(sanitizedInput)

    logger.debug(f"Sorted input data:\n{pformat(sortedInput)}")
    
    # Generate missing rows (as "don't care" minterms)
    if numRows < maxRows:
        logger.debug(f"Actual rows: {numRows}\nMax rows:    {maxRows}")
        sortedInput = generate_missing_rows(sortedInput, maxRows)

    # Add index value at start of each term in the table. This will be used later in the recursive minterm combination/reduction
    for idx, term in enumerate(sortedInput):
        term.insert(0, idx)

    logger.debug(f"Final list:\n{pformat(sortedInput)}")
    return sortedInput


def resolve_input_file_path(inputFilePath):
    inputFilePath = os.path.expanduser(inputFilePath)
    resolvedPath = os.path.abspath(inputFilePath)
    if not os.path.isfile(resolvedPath):
        raise FileNotFoundError(f"File not found: {resolvedPath}")    
    return resolvedPath


def recursive_binary_partition_sort(
        rows: int, 
        col: int = 0
    ) -> list[list[any]]:

    logger.verbose(f"Rows to sort by column {col}:\n{pformat(rows)}")

    if rows == []:
        logger.verbose(f"Missing row.")
        return []

    termMax: int = len(rows[0]) - 1
    sortedList: list[list[any]] = sorted(rows, key=lambda x: x[col])

    logger.verbose(f"Sorted rows:\n{pformat(sortedList)}")

    if col >= termMax or len(rows) <= 1:
        return sortedList
    
    zeroSubSplitList: list[list[any]]
    oneSubSplitList: list[list[any]]
    
    zeroSubSplitList, oneSubSplitList = binary_split_nested_list(sortedList, col)

    zeroSubSortedList: list[list[any]] = recursive_binary_partition_sort(zeroSubSplitList, col + 1)
    oneSubSortedList: list[list[any]] = recursive_binary_partition_sort(oneSubSplitList, col + 1)

    return zeroSubSortedList + oneSubSortedList


def binary_split_nested_list(
        nestedList: list[list[int]],
        index: int
    ) -> list[list[int]]:
    zeroSubList: list[int] = []
    oneSubList: list[int] = []
    for i in nestedList:
        if i[index] == 0:
            zeroSubList.append(i)
        else:
            oneSubList.append(i)
    return zeroSubList, oneSubList
