import copy

#Rotates a list without modifing the original parameter.
def nDestructive(L, k):
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

# print(nDestructive([1,2,3,4], -1))
# print(nDestructive([1,2,3,4], 0))
# print(nDestructive([1,2,3,4], 1))


#### destructiveRotateList ####

# Rotates a list destructively
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
def destructive2(L, k):
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

#### destructiveRotateList ####

# Rotates a list destructively
def nDestructive2(L, k):
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
    # Base case.

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

def mustUseRecursion(wordList):
    if len(wordList) == 0:
        return
    return [wordList[0].upper()] + capitalizeWords(wordList[1:])

def mustUseRecursionF(wordList):
    L = []
    for word in wordList:
        L.append(word.upper())
    return L

def cantUseRecursion(wordList):
    for word in wordList:
        word = word.upper()
    return wordList

def cantUseRecursionF(wordList):
    if len(wordList) == 0:
        return
    return [wordList[0].upper()] + capitalizeWords(wordList[1:])

def printUpper(s):
    print(s.upper())


# Define a class per the 15-112 specification.
class Polynomial(object):
    def __init__(self, coeffs):
        self.coeffs = list(coeffs[:])
        
        # Get rid of leading 0s.
        for i in range(len(coeffs)):
            if coeffs[i] == 0:
                self.coeffs.pop(0)
            else:
                break
    
    def __repr__(self):
        return f'Polynomial(coeffs={self.coeffs})'
    
    def __hash__(self):
        return hash( tuple(self.coeffs) )

    def __eq__(self, others):
        # If we only have one coefficient, return the first coefficient.
        if len(self.coeffs) == 1:
            return self.coeffs[0]
        else:
            # Otherwise, check if the coefficients are the same.
            return isinstance(self, Polynomial) \
                and isinstance(others, Polynomial) \
                and (self.coeffs == others.coeffs)

    # Return the maxiumun degree of the polynomial.
    def degree(self):
        return len(self.coeffs) - 1 

    # Return a specific coefficient. 
    def coeff(self, x):
        return self.coeffs[self.degree() - x]

    # Evaluate the polynomial as f(x)
    def evalAt(self, x):
        evalValue = 0
        # For each coefficient, add x * the coefficient.
        for i in range(self.degree() + 1):
            evalValue += self.coeffs[i] * x ** (self.degree() - i)
        return evalValue

    # Scale a polynomial, and return a new instance.
    def scaled(self, scale):
        newCoeffs = self.coeffs[:]
        # For each coefficient, multiply it by the scale.
        for i in range(self.degree() + 1):
            newCoeffs[i] = newCoeffs[i] * scale
        return Polynomial(newCoeffs)

    # Get the deriviate of a polynomial.
    def derivative(self):
        newCoeffs = self.coeffs[0:-1]
        # Multiply each coefficient by it's power, and subtract it by one.
        for i in range(len(newCoeffs)):
            newCoeffs[i] = newCoeffs[i] * (self.degree() - i)
        return Polynomial(newCoeffs)
    
    # Add two polynomial together.
    def addPolynomial(self, other):
        # Ensure both are polynomials.
        if not isinstance(other, Polynomial): return None
        newCoeffs = []
        largerCoeffs = []
        smallerCoeffs = []
        # Find the larger set of coefficients.
        if self.degree() > other.degree():
            largerCoeffs = self.coeffs[::-1]
            smallerCoeffs = other.coeffs[::-1]
        else:
            largerCoeffs = other.coeffs[::-1]
            smallerCoeffs = self.coeffs[::-1]
        # Remove the larger coefficient from the smaller one.
        for i in range(len(largerCoeffs)):
            if i >= len(smallerCoeffs):
                newCoeffs.insert(0, largerCoeffs[i])
            else:
                newCoeffs.insert(0, largerCoeffs[i] + smallerCoeffs[i])
        return Polynomial(newCoeffs)

    def multiplyPolynomial(self, other):
        if not isinstance(other, Polynomial): return None
        newCoeffs = {}
        # For each coefficient, depending on it's position, add them.
        for i in range(len(self.coeffs)):
            for j in range(len(other.coeffs)):
                newP = i + j
                curCoeff = newCoeffs.get(newP, 0)
                newCoeffs[newP] = curCoeff + self.coeffs[i] * other.coeffs[j]
        return Polynomial(list(newCoeffs.values()))