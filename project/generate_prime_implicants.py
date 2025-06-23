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
        fullyMinimizedMinterms: Optional[list[list[any]]] = []
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

    logger.debug(f"Recursion level: {recursionLevel}")
    logger.debug(f"Disregarded bit count: {disregardedBitCount}")
    logger.debug(f"Combined minterm table:\n{pformat(mintermTable)}")
    logger.debug(f"Groups of minterms to check: {mintermGroupCount}")

    if mintermGroupCount <= 1:
        logger.debug(f"Minterm table length ({mintermGroupCount}) is insufficient for combining terms, returning it:\n{combinedMintermTableAndIndices}\n")
        return fullyMinimizedMinterms + mintermTable
    
    newPrimeImplicants: list[list[any]] = []
    usedImplicants: list[list[any]] = []

    newTerms: int = 0
    i: int = 0
    while True:

        logger.verbose(f"i: {i}")

        groupOne: list[any] = mintermTable[i]
        groupTwo: list[any] = mintermTable[i + 1]


        logger.debug(f"Group {i}: {groupOne}\nGroup {i + 1}: {groupTwo}")

        for tOneIndex, termOne in enumerate(groupOne):
            for tTwoIndex, termTwo in enumerate(groupTwo):


                mintermOne: list[any] = termOne[disregardedBitCount:-1]
                mintermTwo: list[any]  = termTwo[disregardedBitCount:-1]
                termOneMIndex: list[int] = termOne[:disregardedBitCount]
                termTwoMIndex: list[int] = termTwo[:disregardedBitCount]
                combinedNewTermIndex: list[int] = termOneMIndex + termTwoMIndex
                termOneOperand: any = termOne[-1]
                termTwoOperand: any = termTwo[-1]
                newMintermOperand: list[any] = ["x"] if termOneOperand != 1 and termTwoOperand != 1 else [1]

                logger.verbose(f"""T1 index: {tOneIndex}
Term one: {termOne}
T2 index: {tTwoIndex}
Term two: {termTwo}
""")

                newTerm: Optional[list[any]] = mintermOne.copy()

                # Iterate through each pair of terms, creating a combined version with - (if valid to do so)
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
                    
                    newTerms += 1
                    usedImplicants.append(termOne)
                    usedImplicants.append(termTwo)

                    combinedNewTerm: list[any] = combinedNewTermIndex + newTerm + newMintermOperand

                    logger.verbose(f"New term:\n{newTerm}\nCombined new term:\n{combinedNewTerm}")

                    try:
                        logger.verbose(f"Try to append `{newTerm}` to:\n{pformat(newPrimeImplicants[i])}")
                        newPrimeImplicants[i].append(combinedNewTerm)
                    except:
                        logger.verbose(f"primeImplicants[{i}] does not exist, addind it and appending term.")
                        newPrimeImplicants.append([])
                        newPrimeImplicants[i].append(combinedNewTerm)

        i += 1
        if i == mintermGroupCount - 1:
            # Prevent index error. At this point all possible group combinations will have been checked
            break

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
    logger.verbose(f"Terms not used in this round:\n{pformat(unusedImplicants)}")

    if unusedImplicants:
        fullyMinimizedMinterms.append(unusedImplicants)

    if len(newPrimeImplicants) > 1:
        return recursive_generate_prime_implicants(newPrimeImplicants, mintermLength, recursionLevel + 1, unusedImplicants)
    else:
        return unusedImplicants + newPrimeImplicants


def generate_minterm_table_index(
        inputData: list[list[any]],
        disregardedBitCount: int
    ) -> list[list[any]]:
    
    mintermLength: int = len(inputData[0])
    mintermTable: list[list[list[int]]] = [[] for _ in range(mintermLength)]

    for i, row in enumerate(inputData):
        print(f"Row: {row}")
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
        primeImplicantList: list[any] = None,
        mintermLength: int = None
) -> list[list[any]]:
    
    if not primeImplicantList:
        return []
    
    innerSliceLength: int = len(primeImplicantList[0]) - mintermLength - 1
    
    minterms: list[any] = []
    for term in primeImplicantList:
        minterms.append(term[innerSliceLength:-1])

    logger.verbose(f"Prime implicant minterms only:\n{pformat(minterms)}")

    uniquePrimeImplicants: list[any] = []
    uniqueMinterms: list[any] = []
    for idx, minterm in enumerate(minterms):
        if minterm not in uniqueMinterms:
            uniquePrimeImplicants.append(primeImplicantList[idx])
            uniqueMinterms.append(minterm)

    logger.info(f"Unique minterms:\n{pformat(uniqueMinterms)}")
    logger.info(f"Unique prime implicants:\n{pformat(uniquePrimeImplicants)}")

    return uniquePrimeImplicants

def check_if_minterm_is_unique(
        newMinterm: list[any],
        primeImplicantList: list[list[any]],
        mintermLength: int
    ) -> bool:

    if not primeImplicantList:
        return True
    
    print(f"New minterm: {newMinterm}")
    
    innerSliceLength: int = len(primeImplicantList[0]) - mintermLength - 1

    minterms: list[any] = []
    for term in primeImplicantList:
        minterms.append(term[innerSliceLength:-1])

    print(f"List: {pformat(minterms)}\n")

    logger.verbose(f"Prime implicant minterms only:\n{pformat(minterms)}")

    if newMinterm in minterms:
        logger.error(f"TERM ALREADY EXISTS")
        return False
    
    return True