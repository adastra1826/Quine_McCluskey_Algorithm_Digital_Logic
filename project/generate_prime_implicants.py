from typing import Optional
from pprint import pformat
from logging import *

logger = getLogger(__name__)

def recursive_generate_prime_implicants(
        combinedMintermTableAndIndex: list[list[list[any]]],
        mintermLength: int,
        recursionLevel: int = 0
    ) -> tuple[Optional[list[list[any]]], Optional[list[list[any]]]]:

    tableLength: int = len(combinedMintermTableAndIndex)
    binaryValue: str = ""
    for idx in range(recursionLevel + 1):
        binaryValue += "1" if idx == 0 else "0"
    binaryValue = int(binaryValue, 2)
    disregardedBitCount = binaryValue

    logger.debug(f"Recursion level: {recursionLevel}")
    logger.debug(f"Disregarded bit count: {disregardedBitCount}")
    logger.debug(f"Combined minterm table:\n{pformat(combinedMintermTableAndIndex)}")
    logger.debug(f"Minterm table length: {tableLength}")

    if tableLength <= 1:

        logger.verbose(f"Minterm table length ({tableLength}) is insufficient for combining terms, returning it:\n{combinedMintermTableAndIndex}\n")

        return (combinedMintermTableAndIndex)
    
    primeImplicants: list[list[any]] = [[]]
    usedImplicants: list[any] = []

    newTerms: int = 0
    i: int = 0
    while True:

        logger.verbose(f"i: {i}")

        groupOne: list[any] = combinedMintermTableAndIndex[i]
        groupTwo: list[any] = combinedMintermTableAndIndex[i + 1]


        logger.verbose(f"Group one: {groupOne}\nGroup two: {groupTwo}")

        for tOneIndex, termOne in enumerate(groupOne):
            for tTwoIndex, termTwo in enumerate(groupTwo):


                mintermOne: list[any] = termOne[disregardedBitCount:-1]
                mintermTwo: list[any]  = termTwo[disregardedBitCount:-1]
                termOneMIndex: list[int] = termOne[:disregardedBitCount]
                termTwoMIndex: list[int] = termTwo[:disregardedBitCount]
                combinedTermIndex: list[int] = termOneMIndex + termTwoMIndex
                termOneOperand: any = termOne[-1]
                termTwoOperand: any = termTwo[-1]
                mintermOperand: list[any] = ["x"] if termOneOperand != 1 and termTwoOperand != 1 else [1]

                logger.verbose(f"""T1 index: {tOneIndex}
Term one: {termOne}
T2 index: {tTwoIndex}
Term two: {termTwo}
""")

                newTerm: Optional[list[any]] = mintermOne.copy()

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

                    combinedNewTerm: list[any] = combinedTermIndex + newTerm + mintermOperand
                    logger.verbose(f"New term:\n{newTerm}\nCombined new term:\n{combinedNewTerm}")

                    try:

                        #logger.verbose(f"{CYAN}Try to append `{newTerm}` to:\n{pformat(primeImplicants[i])}{RESET}")

                        primeImplicants[i].append(combinedNewTerm)
                    except:
                        logger.verbose(f"EXCEPTION")
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

        uniqueUsedImplicants: list[any] = []
        for term in usedImplicants:
            if term not in uniqueUsedImplicants:
                uniqueUsedImplicants.append(term)

        logger.verbose(f"Used implicants:\n{pformat(uniqueUsedImplicants)}")

        originalImplicants: list[any] = []
        for group in combinedMintermTableAndIndex:
            for term in group:
                originalImplicants.append(term)

        logger.verbose(f"Original implicants:\n{pformat(originalImplicants)}")

        unusedImplicants: list[any] = []
        for term in originalImplicants:
            if term not in uniqueUsedImplicants:
                unusedImplicants.append(term)

        logger.verbose(f"Unused implicants:\n{pformat(unusedImplicants)}")

        uniqueUnusedImplicants = remove_duplicate_minterms(unusedImplicants, mintermLength)

        logger.verbose(f"Unique unused implicants:\n{pformat(uniqueUnusedImplicants, width=100)}")

        returnlist = uniquePrimeImplicants.copy()
        if len(uniqueUnusedImplicants) > 0:
            returnlist.insert(0, uniqueUnusedImplicants)

        logger.verbose(f"Prime implicants (returning this):\n{returnlist}")

        return returnlist
    elif len(primeImplicants) > 1:

        logger.verbose(f"Going deeper with these prime implicants:\n{primeImplicants}")

        return recursive_generate_prime_implicants(primeImplicants, mintermLength, recursionLevel + 1)
    else:
        logger.verbose(f"Reached the end of the function with nothing. This probably shouldn't happen?")
        return [None]
    

def remove_duplicate_minterms(
        primeImplicantlist: list[any] = None,
        mintermLength: int = None
) -> list[list[any]]:
    
    if not primeImplicantlist:
        return []
    
    innerSlice: int = len(primeImplicantlist[0]) - mintermLength - 1
    
    minterms: list[any] = []
    for term in primeImplicantlist:
        minterms.append(term[innerSlice:-1])

    logger.verbose(f"Prime implicant minterms only:\n{pformat(minterms)}")

    uniquePrimeImplicants: list[any] = []
    uniqueMinterms: list[any] = []
    for idx, minterm in enumerate(minterms):
        if minterm not in uniqueMinterms:
            uniquePrimeImplicants.append(primeImplicantlist[idx])
            uniqueMinterms.append(minterm)

    logger.verbose(f"Unique minterms:\n{pformat(uniqueMinterms)}")
    logger.verbose(f"Unique prime implicants:\n{pformat(uniquePrimeImplicants)}")

    return uniquePrimeImplicants