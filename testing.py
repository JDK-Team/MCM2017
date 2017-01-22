def aitChoiceFn(choicesList, default=0, prevPath=[]):  # go back to the scanner you came from or go to zone D
    dropOffNode = prevPath[-2]
    startIndex = len(dropOffNode) - 1
    for letter in range(len(dropOffNode)):
        if (isInt(dropOffNode[letter])):
            startIndex = letter
            break
    index = int(dropOffNode[startIndex:])
    return index

def isInt(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

choicesList = [3,6,3,5,3,6]
prevPath = ["start0", "idCheck2", "dropOff10", "ait2"]
print(aitChoiceFn(choicesList, 0, prevPath))
