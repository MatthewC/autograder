import copy

## HELPER FUNCTIONS ##
# Given a number n, return how many digits it has. 
def sizeof(n):
    if n == 0:
        return 1

    currentPower = 0

    while not currentPower == -1:
        if ( abs(n) // ( 10**currentPower ) ) == 0:
            return currentPower
        else:
            currentPower += 1 

# Combines two numbers (i.e (5, 10) = 510)
def concatNumbers(x, y):
    x = x * 10**(sizeof(y))
    return x + y

# Given n, return the first k digits.
def getLeftkDigits(n, k):
    if (sizeof(n) - k) < 0:
        return n
    return n // (10 ** (sizeof(n) - k))

# Given a number, removes k digits from the left.
def removeLeftkDigits(n, k):
    return int(n % (10 ** (sizeof(n) - k)))


def decodeList(n, crash=False):
    if crash:
        1/0
    decodedNums = []
    encodedNum = n

    while True:
        # Base case.
        if encodedNum == 0:
            break
        totalCount = sizeof(encodedNum)
        isNegative = getLeftkDigits(encodedNum, 1)
        countCount = getLeftkDigits( removeLeftkDigits(encodedNum, 1), 1 )
        count = getLeftkDigits( removeLeftkDigits(encodedNum, 2), countCount )

        encodedNum = removeLeftkDigits(encodedNum, (2 + countCount))
        
        # leading 0 can cause an issue, so a special case is included.
        if not sizeof(encodedNum) == (totalCount - (2 + countCount)):
            decodedNums.append(0)
        else:
            # Otherwise, simply append to the array. 
            decodedDigits = getLeftkDigits(encodedNum, count)
            decodedDigits = decodedDigits * (-1) ** (isNegative + 1)
            decodedNums.append(decodedDigits)

            encodedNum = removeLeftkDigits(encodedNum, count)
    return decodedNums

def capitalizeWords(wordList):
    if len(wordList) == 0:
        return
    return [wordList[0].upper()] + capitalizeWords(wordList[1:])

def printUpper(s):
    print(s.upper())

def cantUseLoops(wordList):
    L = []
    for word in wordList:
        L.append(word.upper())
    return L

def usesRecursionWhenTheyCant(wordList):
    if len(wordList) == 0:
        return
    return [wordList[0].upper()] + capitalizeWords(wordList[1:])


def isNotRecursive(wordList):
    L = []
    for word in wordList:
        L.append(word.upper())
    return L

def destructive(L, k):
    if L == []:
        return L
    if (k >= 0):
        for i in range(k):
            L.insert(0, L[-1])
            del L[-1]
    else:
        for i in range(abs(k)):
            L.insert(len(L), L[0])
            del L[0]
    return None


#Rotates a list without modifing the original parameter.
def destructiveFunctionFails(L, k):
    if L == []:
        return L
    lCopy = copy.copy(L)
	
    if (k >= 0):
        for i in range(k):
            lCopy.insert(0, lCopy[-1])
            del lCopy[-1]
    else:
        for i in range(abs(k)):
            lCopy.insert(len(L), lCopy[0])
            del lCopy[0]
    return lCopy

#Rotates a list without modifing the original parameter.
def nonDestructiveFunction(L, k):
    if L == []:
        return L
    lCopy = copy.copy(L)
	
    if (k >= 0):
        for i in range(k):
            lCopy.insert(0, lCopy[-1])
            del lCopy[-1]
    else:
        for i in range(abs(k)):
            lCopy.insert(len(L), lCopy[0])
            del lCopy[0]
    return lCopy

def nonDestructiveFunctionFails(L, k):
    if L == []:
        return L
    if (k >= 0):
        for i in range(k):
            L.insert(0, L[-1])
            del L[-1]
    else:
        for i in range(abs(k)):
            L.insert(len(L), L[0])
            del L[0]
    return None