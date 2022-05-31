import numpy as np

def string_to_code(string):
    code = []
    for s in string:
        if s == "I":
            code.append(0)
        elif s == "X":
            code.append(1)
        elif s == "Y":
            code.append(2)
        elif s == "Z":
            code.append(3)
        else:
            raise
    return code

def code_to_string(code):
    string = ""
    for c in code:
        if c == 0:
            string += "I"
        elif c == 1:
            string += "X"
        elif c == 2:
            string += "Y"
        elif c == 3:
            string += "Z"
        else:
            raise
    return string

def multiply_code(code1, code2):
    group_table = np.array([
        [0, 1, 2, 3],
        [1, 0, 3, 2],
        [2, 3, 0, 1],
        [3, 2, 1, 0]
    ])
    # code3 = code1 * code2
    code3 = []
    for i, j in zip(code1, code2):
        code3.append(group_table[i,j])
    return code3

def check_commute(code1, code2):
    commute = 1
    for i,j in zip(code1, code2):
        if i == 0 or j == 0 or i == j:
            commute *= 1
        else:
            commute *= -1
    flag = bool((1+commute)/2)
    return flag
    
class PauliOperator:
    def __init__(self,string):
        self.string = string
        self.code = string_to_code(string)
        
    def __repr__(self):
        return self.string
                
    def __mul__(self, other):
        new_code = multiply_code(self.code, other.code)
        new_string = code_to_string(new_code)
        new_pauli = PauliOperator(new_string)
        return new_pauli
    
    def is_commute(self, other):
        flag = check_commute(self.code, other.code)
        return flag