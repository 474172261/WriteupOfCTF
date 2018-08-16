import json, base64, os, random
G1 = [0,255,200,8,145,16,208,54,90,62,216,67,153,119,254,24,35,32,7,112,161,108,12,127,98,139,64,70,199,75,224,14,235,22,232,173,207,205,57,83,106,39,53,147,212,78,72,195,43,121,84,40,9,120,15,33,144,135,20,42,169,156,214,116,180,124,222,237,177,134,118,164,152,226,150,143,2,50,28,193,51,238,239,129,253,48,92,19,157,41,23,196,17,68,140,128,243,115,66,30,29,181,240,18,209,91,65,162,215,44,233,213,89,203,80,168,220,252,242,86,114,166,101,47,159,155,61,186,125,194,69,130,167,87,182,163,122,117,79,174,63,55,109,71,97,190,171,211,95,176,88,175,202,94,250,133,228,77,138,5,251,96,183,123,184,38,74,103,198,26,248,105,37,179,219,189,102,221,241,210,223,3,141,52,217,146,13,99,85,170,73,236,188,149,60,132,11,245,230,231,229,172,126,110,185,249,218,142,154,201,36,225,10,21,107,58,160,81,244,234,178,151,158,93,34,136,148,206,25,1,113,76,165,227,197,49,187,204,31,45,59,82,111,246,46,137,247,192,104,27,100,4,6,191,131,56]

G2 = [1,229,76,181,251,159,252,18,3,52,212,196,22,186,31,54,5,92,103,87,58,213,33,90,15,228,169,249,78,100,99,238,17,55,224,16,210,172,165,41,51,89,59,48,109,239,244,123,85,235,77,80,183,42,7,141,255,38,215,240,194,126,9,140,26,106,98,11,93,130,27,143,46,190,166,29,231,157,45,138,114,217,241,39,50,188,119,133,150,112,8,105,86,223,153,148,161,144,24,187,250,122,176,167,248,171,40,214,21,142,203,242,19,230,120,97,63,137,70,13,53,49,136,163,65,128,202,23,95,83,131,254,195,155,69,57,225,245,158,25,94,182,207,75,56,4,185,43,226,193,74,221,72,12,208,125,61,88,222,124,216,20,107,135,71,232,121,132,115,60,189,146,201,35,139,151,149,68,220,173,64,101,134,162,164,204,127,236,192,175,145,253,247,79,129,47,91,234,168,28,2,209,152,113,237,37,227,36,6,104,179,147,44,111,62,108,10,184,206,174,116,177,66,180,30,211,73,233,156,200,198,199,34,110,219,32,191,67,81,82,102,178,118,96,218,197,243,246,170,205,154,160,117,84,14,1]

class A:

    def __init__(self, value):
        self.value = value % 256

    def __add__(self, _A):
        return A(self.value ^ _A.value)

    def __iadd__(self, _A):
        self.value ^= _A.value
        return self

    def __mul__(self, _A):
        if _A.value == 0 or self.value == 0:
            return A(0)
        return A(G2[(G1[self.value] + G1[_A.value]) % 255])

    def __imul__(self, _A):
        if _A.value == 0 or self.value == 0:
            self.value = 0
        else:
            self.value = G2[(G1[self.value] + G1[_A.value]) % 255]
        return self

    def __div__(self, _A):
        if _A.value == 0:
            raise ArithmeticError('Division by zero')
        return A(G2[(255 + G1[self.value] - G1[_A.value]) % 255])

    def __idiv__(self, _A):
        if _A.value == 0:
            raise ArithmeticError('Division by zero')
        self.value = G2[(255 + G1[self.value] - G1[_A.value]) % 255]
        return self


class SchLupp:

    def __init__(self, shares, threshold):
        self.shares = shares
        self.rng = random.SystemRandom()
        self.base_poly = [ self.rng.randint(0, 256) for _ in range(threshold - 1) ]

    def split(self, secret):
        secrets = [secret] + self.base_poly
        no_repeat_random = []
        result = []
        while len(no_repeat_random) < self.shares:
            drawn = self.rng.randint(1, 255)
            if drawn not in no_repeat_random:
                no_repeat_random += [drawn]

        for rand in no_repeat_random:
            B = A(1)
            S = A(0)
            X = A(rand)
            for num in secrets:
                S += B * A(num)
                B *= X

            result.append(S.value)

        return (no_repeat_random, result)


class Encoding:

    def __init__(self):
        self.splitter = SchLupp(10, 5)

    def split(self, numshares, threshold, key):
        xshares = [''] * numshares
        yshares = [''] * numshares
        for char in key:
            xcords, ycords = self.splitter.split(ord(char))
            for idx in range(numshares):
                xshares[idx] += chr(xcords[idx])
                yshares[idx] += chr(ycords[idx])

        return zip(xshares, yshares)

    def dump(self, shares, threshold, split):
        data = {'shares': shares,
         'threshold': threshold,
         'split': [base64.b64encode(split[0]), base64.b64encode(split[1])]}
        return json.dumps(data)