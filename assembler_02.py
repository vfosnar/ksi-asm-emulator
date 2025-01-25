from data import *

class Assembler:
    def __init__(self):

        ...
    
    def _assemble(self):
        ...



if __name__ == "__main__":

    program = """

segment code
label   MOV AX, 7
        MOV BX, 42
        ADD AX, BX
hellow  MOV CX, 0
"""

    assembler = Assembler(program)
    
    bytes = assembler.bytecode


    

    