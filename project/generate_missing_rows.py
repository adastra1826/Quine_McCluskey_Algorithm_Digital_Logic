from logging import *

logger = getLogger(__name__)

def generate_missing_rows(
        incompleteData: list[list[any]],
        maxRows: int,
        dontCare: bool = True
        ):
    
    """
    Given `incomplete_data` (each row ending in a bit we don't care about here),
    which is already sorted by its integer value, fill in any missing binary rows up to `max_rows`.
    Returns a full list of rows, with newly created rows appended with "x".n 
    """
    
    completeData = []
    termLength = len(incompleteData[0]) - 1
    determinant: any = "x" if dontCare else 0

    incompleteDataRowIndex = 0
    for rowIndex in range(maxRows):

        incompleteDataRow = incompleteData[incompleteDataRowIndex]
        dataBits = incompleteDataRow[:-1]
        bitString = "".join(map(str, dataBits))

        binaryValue = int(bitString, 2)

        if binaryValue != rowIndex:

            bits = bin(rowIndex)[2:].zfill(termLength)
            missingRow = [int(b) for b in bits] + [determinant]
            completeData.append(missingRow)

            logger.debug(f"Missing row at index {incompleteDataRowIndex}: {missingRow}")
            
        else:
            incompleteDataRowIndex += 1
            completeData.append(incompleteDataRow)
    
    return completeData