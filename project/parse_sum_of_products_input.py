from logging import *
from global_constants import *

import re
import heapq
from typing import Optional
from pprint import pformat

logger = getLogger(__name__)

def parse_sop_input(
        mintermInputString: str,
        dontCareInputString: Optional[str] = None,
        inputCount: int = None
        ) -> list[list[any]]:
    
    logger.verbose(f"SoP minterm string:\n{mintermInputString}")
    logger.verbose(f"SoP don't care string:\n{dontCareInputString}")

    sanitizedDontCareInput: list[str] = None
    
    # Remove duplicates, any value other than a digit, split by comma, sort ascending, cast final list values as integers
    sanitizedMintermInput: list[int] = cast_str_list_as_int(sorted(list(filter(None, list(set(re.split(",", re.sub("[^0-9-]", ",", mintermInputString))))))))   
    if dontCareInputString:
        sanitizedDontCareInput: list[str] = cast_str_list_as_int(sorted(list(filter(None, list(set(re.split(",", re.sub("[^0-9-]", ",", dontCareInputString))))))))

    logger.verbose(f"Sanitized minterm string:\n{sanitizedMintermInput}")
    logger.verbose(f"Sanitized don't care string:\n{sanitizedDontCareInput}")

    if not sanitizedMintermInput:
        raise SyntaxError(f"Invalid minterm specification. Values must be integers separated by commas with no spaces or quotes.\n{USAGE_TEXT}")
    elif dontCareInputString and not sanitizedDontCareInput:
        raise SyntaxError(f"Invalid don't care specification. Values must be integers separated by commas with no spaces or quotes.\n{USAGE_TEXT}")
    
    finalMintermSpecification: list[list[any]] = []
    for minterm in sanitizedMintermInput:
            finalMintermSpecification.append([minterm, 1])

    finalDontCareSpecification: list[list[any]] = []
    combinedFinalSpecification: list[list[any]] = []
    if sanitizedDontCareInput:
        for DCMinterm in sanitizedDontCareInput:
            if DCMinterm in sanitizedMintermInput:
                raise SyntaxError(f"Cannot specify the same term as a minterm and a don't care.\n{USAGE_TEXT}")
            
            finalDontCareSpecification.append([DCMinterm, "x"])
            combinedFinalSpecification = list(heapq.merge(finalMintermSpecification, finalDontCareSpecification))
    else:
        combinedFinalSpecification = finalMintermSpecification

    logger.verbose(f"Final minterm list:\n{pformat(finalMintermSpecification)}")
    logger.verbose(f"Final don't care list:\n{pformat(finalDontCareSpecification)}")
    logger.verbose(f"Final combined list:\n{pformat(combinedFinalSpecification)}")

    bitCount: int = None
    if not inputCount:
        highestInputValue: int = combinedFinalSpecification[-1][0]
        binaryRepresentation = bin(highestInputValue)[2:]
        bitCount = len(binaryRepresentation)
    else:
        bitCount = inputCount
    
    finalMintermTable: list[list[any]] = []
    for mintermSpecification in combinedFinalSpecification:
        bitValue = generate_binary_representation_as_list(mintermSpecification[0], bitCount)
        finalMintermTable.append(bitValue + [mintermSpecification[1]])

    logger.verbose(f"Final reconstructed minterm table:\n{finalMintermTable}")
    
    return finalMintermTable


def generate_binary_representation_as_list(
        number: int,
        bitCount: int
    ) -> list[int]:

    maxValue: int = int("".join(["1" for b in range(bitCount)]), 2) + 1
    if number > maxValue:
        raise ValueError(f"Minterm index '{number}' is larger than max number of inputs specified '{maxValue}'.")

    binaryString: str = bin(number)[2:].zfill(bitCount)
    binaryList: list[int] = [int(b) for b in binaryString]

    return binaryList


def cast_str_list_as_int(
        stringListInput: Optional[list[any]] = None
    ) -> list[int]:

    if not stringListInput:
        raise ValueError(f"Empty list passed to int cast function.")

    intCastValues: list[int] = []

    for value in stringListInput:
        try:
            value = int(value)
        except:
            logger.warning(f"Value '{value}' from list '{pformat(stringListInput)}' cannot be cast as int. This message should never appear.")
            continue

        if value < 0:
            raise SyntaxError(f"Cannot specify negative minterms: '{value}'.")
        
        intCastValues.append(value)

    return intCastValues