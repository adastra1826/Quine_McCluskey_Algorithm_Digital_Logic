import logger_setup
from logging import *
from global_constants import *
from typing import Optional
from pprint import pformat

logger = getLogger(__name__)

def recursive_generate_prime_implicants(
        combinedMintermTableAndIndices: list[list[any]],
        mintermLength: int,
        recursionLevel: int = 0,
        fullyMinimizedMinterms: Optional[list[list[any]]] = None
    ) -> tuple[Optional[list[list[any]]], Optional[list[list[any]]]]:

    # Determine the number of bits at the beginning of each term that are not part of the minterm itself
    binaryValue: str = ""
    for idx in range(recursionLevel + 1):
        binaryValue += "1" if idx == 0 else "0"
    binaryValue = int(binaryValue, 2)
    disregardedBitCount = binaryValue

    mintermTable: list[list[any]]
    mintermTable = generate_minterm_table_index(combinedMintermTableAndIndices, disregardedBitCount)

    mintermGroupCount: int = 0
    for group in mintermTable:
        if group:
            mintermGroupCount += 1

    logger.debug(f"Recursion level: {recursionLevel}", color = WHITE + BG_RED)
    logger.debug(f"Disregarded bit count: {disregardedBitCount}", color = WHITE + BG_RED)
    logger.debug(f"Combined minterm table:\n{pformat(mintermTable)}", color = WHITE + BG_RED)
    logger.debug(f"Groups of minterms to check: {mintermGroupCount}", color = WHITE + BG_RED)
    logger.debug(f"Fully minimized implicants: {fullyMinimizedMinterms}", color = WHITE + BG_RED)

    if mintermGroupCount <= 1:
        logger.debug(f"Minterm table length ({mintermGroupCount}) is insufficient for combining terms, returning it:\n{combinedMintermTableAndIndices}\n")
        return fullyMinimizedMinterms + mintermTable[0]
    
    newPrimeImplicants: list[list[any]] = []
    usedImplicants: list[list[any]] = []
 
    i: int = 0
    while True:

        logger.verbose(f"i: {i}")

        groupOne: list[any] = mintermTable[i]
        groupTwo: list[any] = mintermTable[i + 1]


        logger.verbose(f"Group {i}: {groupOne}\nGroup {i + 1}: {groupTwo}")

        for termOne in groupOne:
            for termTwo in groupTwo:

                mintermOne: list[any] = termOne[disregardedBitCount:-1]
                mintermTwo: list[any]  = termTwo[disregardedBitCount:-1]
                termOneMIndex: list[int] = termOne[:disregardedBitCount]
                termTwoMIndex: list[int] = termTwo[:disregardedBitCount]
                combinedNewTermIndex: list[int] = termOneMIndex + termTwoMIndex
                termOneOperand: any = termOne[-1]
                termTwoOperand: any = termTwo[-1]
                newMintermOperand: list[any] = ["x"] if termOneOperand != 1 and termTwoOperand != 1 else [1]

                newTerm: Optional[list[any]] = mintermOne.copy()

                # Iterate through each pair of terms, creating a combined version with '-' (if valid to do so)
                differingBit: bool = False
                for y in range(len(newTerm)):
                    if mintermOne[y] != mintermTwo[y]:
                        if differingBit or mintermOne[y] == "-" or mintermTwo[y] == "-":
                            newTerm = None
                        elif newTerm:
                            newTerm[y] = "-"
                            differingBit = True
                        else: break

                if newTerm:
                    logger.verbose(f"New combined term:`{newTerm}`")
                    usedImplicants.append(termOne)
                    usedImplicants.append(termTwo)
                    combinedNewTerm: list[any] = combinedNewTermIndex + newTerm + newMintermOperand
                    newPrimeImplicants.append(combinedNewTerm)

        i += 1
        if i == mintermGroupCount - 1:
            # Prevent index error. At this point all possible group combinations will have been checked
            break

    # Remove duplicate minterms. Very important step, as the script takes far longer to run if this is omitted
    newPrimeImplicants = remove_duplicate_minterms(newPrimeImplicants, mintermLength)

    logger.debug(f"New prime implicants:\n{pformat(newPrimeImplicants)}", color = CYAN)
    logger.verbose(f"Used implicants:\n{pformat(usedImplicants)}")

    # Create unique list of all implicants that were used
    uniqueUsedImplicants: list[list[any]] = []
    for term in usedImplicants:
        if term not in uniqueUsedImplicants:
            uniqueUsedImplicants.append(term)
    logger.verbose(f"Unique used implicants:\n{pformat(uniqueUsedImplicants)}")
                
    # Flatten the nested original implicants into one list
    originalImplicants: list[list[any]] = []
    for group in mintermTable:
        for term in group:
            originalImplicants.append(term)
    logger.verbose(f"Original implicants:\n{pformat(originalImplicants)}")
    
    # Find all implicants that were not used
    unusedImplicants: list[list[any]] = []
    for term in originalImplicants:
        if term not in uniqueUsedImplicants:
            unusedImplicants.append(term)
    logger.debug(f"Terms not used in this round:\n{pformat(unusedImplicants)}")

    # Carry over previous fully minimized terms and add new ones
    newFullyMinimizedMinterms: list[list[any]] = []
    if unusedImplicants:
        logger.debug("Add unused implicants to fully minimized minterms, excluding terms that only cover don't care values.")
        for term in unusedImplicants:
            if term[-1] == 1:
                newFullyMinimizedMinterms.append(term)
    if fullyMinimizedMinterms:
        logger.debug(f"Add previous fully minimized minterms:\n{pformat(fullyMinimizedMinterms)}")
        newFullyMinimizedMinterms.append(fullyMinimizedMinterms)

    return recursive_generate_prime_implicants(newPrimeImplicants, mintermLength, recursionLevel + 1, newFullyMinimizedMinterms)


def generate_minterm_table_index(
        inputData: list[list[any]],
        disregardedBitCount: int
    ) -> list[list[any]]:
    
    mintermLength: int = len(inputData[0])
    mintermTable: list[list[list[int]]] = [[] for _ in range(mintermLength - disregardedBitCount)]

    for i, row in enumerate(inputData):
        outputBit = row[-1]
        if outputBit in {1, "x"}:
            numOnes: int = 0
            for bit in row[disregardedBitCount:-1]:
                if bit == 1:
                    numOnes += 1
            mintermTable[numOnes].append(row)

    logger.verbose(f"Minterm table:\n{pformat(mintermTable)}")

    return mintermTable
    

def remove_duplicate_minterms(
        primeImplicantList: list[list[any]] = None,
        mintermLength: int = None
) -> list[list[any]]:
    
    if not primeImplicantList:
        return []
    
    innerSliceLength: int = len(primeImplicantList[0]) - mintermLength - 1
    
    minterms: list[any] = []
    for term in primeImplicantList:
        minterms.append(term[innerSliceLength:-1])

    uniquePrimeImplicants: list[any] = []
    uniqueMinterms: list[any] = []
    for idx, minterm in enumerate(minterms):
        if minterm not in uniqueMinterms:
            uniquePrimeImplicants.append(primeImplicantList[idx])
            uniqueMinterms.append(minterm)

    logger.verbose(f"Provided minterms:\n{pformat(minterms)}")
    logger.verbose(f"Unique minterms:\n{pformat(uniqueMinterms)}")
    logger.verbose(f"Provided prime implicants:\n{pformat(primeImplicantList)}")
    logger.verbose(f"Unique prime implicants:\n{pformat(uniquePrimeImplicants)}")

    return uniquePrimeImplicants