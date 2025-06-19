from logging import *
from global_constants import *

logger = getLogger(__name__)

def generate_missing_rows(
        incompleteData: list[list[any]],
        maxRows: int,
        determinant: any = "x"
        ):
    
    """
    Given `incomplete_data` (each row ending in a bit we don't care about here),
    which is already sorted by its integer value, fill in any missing binary rows up to `max_rows`.
    Returns a full list of rows, with newly created rows appended with "x" (or 0 if dontCare is False)
    """
    
    completeData: list[list[any]] = []
    termLength: int = len(incompleteData[0]) - 1

    incompleteDataRowIndex: int = 0
    for rowIndex in range(maxRows):

        incompleteDataRow: list[any] = incompleteData[incompleteDataRowIndex]
        dataBits: list[int] = incompleteDataRow[:-1]
        bitString: str = "".join(map(str, dataBits))

        binaryValue: int = int(bitString, 2)

        if binaryValue != rowIndex:

            bits: str = bin(rowIndex)[2:].zfill(termLength)
            missingRow: list[any] = [int(b) for b in bits] + [determinant]
            completeData.append(missingRow)

            logger.debug(f"Missing row at index {incompleteDataRowIndex}: {missingRow}")
            
        else:
            incompleteDataRowIndex += 1
            completeData.append(incompleteDataRow)
    
    return completeData