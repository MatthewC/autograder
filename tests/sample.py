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

# Encodes a number using our pre-defined rules. (see hw post)
def encode(n):
    numSize = sizeof(n)
    countSize = sizeof(numSize)

    encoded = concatNumbers(numSize, abs(n))
    encoded = concatNumbers(countSize, encoded)
    # Check if +ve, or -ve.
    if n >= 0:
        encoded = concatNumbers(1, encoded)
    else:
        encoded = concatNumbers(2, encoded)
    return encoded

# Decodes a number using the same previous ruleset.
def decode(n):
    # Extract base information from number.
    signNum = getLeftkDigits(n, 1)
    countCount = getLeftkDigits( removeLeftkDigits(n, 1), 1)
    numCount = getLeftkDigits( removeLeftkDigits(n, 2), countCount)

    # Using the base information, extract the decoded number.
    num = removeLeftkDigits(n, (2 + countCount))
    num = getLeftkDigits(num, numCount)
    num = num * (-1)**(signNum + 1)

    # Any excess number is stored as a seperate element in the list.
    excessNums = removeLeftkDigits(n, (2 + countCount + numCount))
    return [num, excessNums]

def encodeList(L):
    encodedNumbers = encode(L[0])
    
    for num in L[1::]:
        encodedNum = encode(num)
        encodedNumbers = concatNumbers(encodedNumbers, encodedNum)
    return encodedNumbers

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

# Given a word, capitalize each letter recursively.
def capitalizeWord(word):
    # Base case
    if len(word) == 0:
        return ""
    # Check if letter is lower, if so using chr & ord make it uppercase.
    if word[0].islower():
        ret = chr(ord(word[0])-32)
    else:
        ret = word[0]
    return ret + capitalizeWord(word[1:])

# Given a list, convert each word in the last to all caps recursively.
def capitalizeWordsF(wordList):
    # Base case.
    if len(wordList) == 0:
        return []
    return [capitalizeWord(''.join(list(wordList[0])))] + capitalizeWords(wordList[1:])

def capitalizeWords(wordList):
    if len(wordList) == 0:
        return
    return [wordList[0].upper()] + capitalizeWords(wordList[1:])

def printUpper(s):
    print(s.upper())
