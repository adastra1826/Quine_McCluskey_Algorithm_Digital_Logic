import logger_setup
from logging import *
from global_constants import *
from typing import Optional
from pprint import pformat

logger = getLogger(__name__)

def recursive_generate_prime_implicants(
        combinedMintermTableAndIndex: list[list[list[any]]],
        mintermLength: int,
        recursionLevel: int = 0,
        minimizedMinterms: Optional[list[list[any]]] = None
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

        logger.debug(f"Minterm table length ({tableLength}) is insufficient for combining terms, returning it:\n{combinedMintermTableAndIndex}\n")

        return (combinedMintermTableAndIndex)
    
    primeImplicants: list[list[any]] = [[]]
    usedImplicants: list[any] = []

    newTerms: int = 0
    i: int = 0
    while True:

        logger.verbose(f"i: {i}")

        groupOne: list[any] = combinedMintermTableAndIndex[i]
        groupTwo: list[any] = combinedMintermTableAndIndex[i + 1]


        logger.debug(f"Group one: {groupOne}\nGroup two: {groupTwo}")

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

                    usedImplicants.append(termOne)
                    usedImplicants.append(termTwo)

                    combinedNewTerm: list[any] = combinedTermIndex + newTerm + mintermOperand

                    logger.verbose(f"New term:\n{newTerm}\nCombined new term:\n{combinedNewTerm}")

                    appendMinterm: bool = True
                    try:
                        appendMinterm = check_if_minterm_is_unique(newTerm, primeImplicants[i], mintermLength)
                        
                        if appendMinterm == False: logger.info(f"Will not append {newTerm} to {pformat(primeImplicants[i])}")
                    except:
                        # If primeImplicants[i] does not exist (which would raise an error), the new minterm is automatically not a duplicate
                        continue

                    if appendMinterm:
                        try:
                            logger.verbose(f"Try to append `{newTerm}` to:\n{pformat(primeImplicants[i])}")

                            primeImplicants[i].append(combinedNewTerm)
                        except:
                            logger.verbose(f"primeImplicants[{i}] does not exist, addind it and appending term.")
                            primeImplicants.append([])
                            primeImplicants[i].append(combinedNewTerm)
                        
                        newTerms += 1

                        #logger.debug(f"Current prime implicants:\n{print(primeImplicants)}", color = CYAN)
            
        i += 1
        if i == tableLength - 1:
            # Prevent index error. At this point all possible group combinations will have been checked
            break

    if len(primeImplicants) == 1:

        #uniquePrimeImplicants = remove_duplicate_minterms(primeImplicants[0], mintermLength)
        uniquePrimeImplicants = primeImplicants[0].copy()
        
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

        logger.debug(f"Prime implicants (returning this):\n{returnlist}")

        return returnlist
    elif len(primeImplicants) > 1:

        logger.debug(f"Going deeper with these prime implicants:\n{primeImplicants}")

        return recursive_generate_prime_implicants(primeImplicants, mintermLength, recursionLevel + 1)
    else:
        logger.warning(f"Reached the end of the function with nothing. This probably shouldn't happen?")
        return [None]
    

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