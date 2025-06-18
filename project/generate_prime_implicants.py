
from typing import Any, List, Optional
from pprint import pformat
from logging import *

logger = getLogger(__name__)

BLACK   = "\033[30m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"
WHITE   = "\033[37m"
BRIGHT_RED = "\033[91m"

BG_YELLOW = "\033[43m"
BG_BLUE   = "\033[44m"

RESET = "\033[0m"

def recursive_generate_prime_implicants(
        combinedMintermTableAndIndex: List[List[List[Any]]],
        mintermLength: int,
        recursionLevel: int = 0
    ) -> tuple[Optional[List[List[Any]]], Optional[List[List[Any]]]]:

    tableLength: int = len(combinedMintermTableAndIndex)
    binaryValue: str = ""
    for idx in range(recursionLevel + 1):
        binaryValue += "1" if idx == 0 else "0"
    binaryValue = int(binaryValue, 2)
    disregardedBitCount = binaryValue

    logger.debug(f"{RED}Recursion level: {recursionLevel}")
    logger.debug(f"Disregarded bit count: {disregardedBitCount}")
    logger.debug(f"Combined minterm table:\n{pformat(combinedMintermTableAndIndex)}")
    logger.debug(f"Minterm table length: {tableLength}{RESET}")

    if tableLength <= 1:

        logger.verbose(f"{GREEN}Minterm table length ({tableLength}) is insufficient for combining terms, returning it:\n{combinedMintermTableAndIndex}\n{RESET}")

        return (combinedMintermTableAndIndex)
    
    primeImplicants: List[List[Any]] = [[]]
    usedImplicants: List[Any] = []

    newTerms: int = 0
    i: int = 0
    while True:

        logger.verbose(f"i: {i}")

        groupOne: List[Any] = combinedMintermTableAndIndex[i]
        groupTwo: List[Any] = combinedMintermTableAndIndex[i + 1]


        logger.verbose(f"Group one: {groupOne}\nGroup two: {groupTwo}")

        for tOneIndex, termOne in enumerate(groupOne):
            for tTwoIndex, termTwo in enumerate(groupTwo):


                mintermOne: List[any] = termOne[disregardedBitCount:-1]
                mintermTwo: List[any]  = termTwo[disregardedBitCount:-1]
                termOneMIndex: List[int] = termOne[:disregardedBitCount]
                termTwoMIndex: List[int] = termTwo[:disregardedBitCount]
                combinedTermIndex: List[int] = termOneMIndex + termTwoMIndex
                termOneOperand: any = termOne[-1]
                termTwoOperand: any = termTwo[-1]
                mintermOperand: List[any] = ["x"] if termOneOperand != 1 and termTwoOperand != 1 else [1]

                logger.verbose(f"""T1 index: {tOneIndex}
Term one: {termOne}
T2 index: {tTwoIndex}
Term two: {termTwo}
""")

                newTerm: Optional[List[Any]] = mintermOne.copy()

                logger.verbose(f"New term copy: {newTerm}")

                # Iterate through each pair of terms, creating a combined version with - (if valid to do so)
                differingBit: bool = False
                for y in range(len(newTerm)):
                    if mintermOne[y] != mintermTwo[y]:
                        if differingBit or mintermOne[y] == "-" or mintermTwo[y] == "-":
                            newTerm = None
                        elif newTerm:
                            #logger.verbose(f"Newterm about to be modified: {newTerm}")
                            newTerm[y] = "-"
                            differingBit = True
                        else: break

                if newTerm:                    

                    usedImplicants.append(termOne)
                    usedImplicants.append(termTwo)

                    combinedNewTerm: List[any] = combinedTermIndex + newTerm + mintermOperand
                    logger.verbose(f"New term:\n{newTerm}\nCombined new term:\n{combinedNewTerm}")

                    try:

                        #logger.verbose(f"{CYAN}Try to append `{newTerm}` to:\n{pformat(primeImplicants[i])}{RESET}")

                        primeImplicants[i].append(combinedNewTerm)
                    except:
                        logger.verbose(f"{RED}EXCEPTION{RESET}")
                        primeImplicants.append([])
                        primeImplicants[i].append(combinedNewTerm)
                    
                    newTerms += 1

                    #logger.verbose(f"Current prime implicants:\n{pformat(primeImplicants)}")
            
        i += 1
        if i == tableLength - 1:
            # Prevent index error. At this point all possible group combinations will have been checked
            break

    if len(primeImplicants) == 1:

        uniquePrimeImplicants = remove_duplicate_minterms(primeImplicants[0], mintermLength)

        uniqueUsedImplicants: List[Any] = []
        for term in usedImplicants:
            if term not in uniqueUsedImplicants:
                uniqueUsedImplicants.append(term)

        logger.verbose(f"Used implicants:\n{pformat(uniqueUsedImplicants)}")

        originalImplicants: List[Any] = []
        for group in combinedMintermTableAndIndex:
            for term in group:
                originalImplicants.append(term)

        logger.verbose(f"Original implicants:\n{pformat(originalImplicants)}")

        unusedImplicants: List[Any] = []
        for term in originalImplicants:
            if term not in uniqueUsedImplicants:
                unusedImplicants.append(term)

        logger.verbose(f"Unused implicants:\n{pformat(unusedImplicants)}")

        uniqueUnusedImplicants = remove_duplicate_minterms(unusedImplicants, mintermLength)

        logger.verbose(f"Unique unused implicants:\n{pformat(uniqueUnusedImplicants, width=100)}")

        returnList = uniquePrimeImplicants.copy()
        if len(uniqueUnusedImplicants) > 0:
            returnList.insert(0, uniqueUnusedImplicants)

        logger.verbose(f"{GREEN}Prime implicants (returning this):\n{returnList}{RESET}")

        return returnList
    elif len(primeImplicants) > 1:

        logger.verbose(f"{YELLOW}Going deeper with these prime implicants:\n{primeImplicants}{RESET}")

        return recursive_generate_prime_implicants(primeImplicants, mintermLength, recursionLevel + 1)
    else:
        logger.verbose(f"{RED}Reached the end of the function with nothing. This probably shouldn't happen?{RESET}")
        return [None]
    

def remove_duplicate_minterms(
        primeImplicantList: List[Any] = None,
        mintermLength: int = None
) -> List[List[Any]]:
    
    if not primeImplicantList:
        return []
    
    innerSlice: int = len(primeImplicantList[0]) - mintermLength - 1
    
    minterms: List[Any] = []
    for term in primeImplicantList:
        minterms.append(term[innerSlice:-1])

    logger.verbose(f"Prime implicant minterms only:\n{pformat(minterms)}")

    uniquePrimeImplicants: List[Any] = []
    uniqueMinterms: List[Any] = []
    for idx, minterm in enumerate(minterms):
        if minterm not in uniqueMinterms:
            uniquePrimeImplicants.append(primeImplicantList[idx])
            uniqueMinterms.append(minterm)

    logger.verbose(f"Unique minterms:\n{pformat(uniqueMinterms)}")
    logger.verbose(f"Unique prime implicants:\n{pformat(uniquePrimeImplicants)}")

    return uniquePrimeImplicants