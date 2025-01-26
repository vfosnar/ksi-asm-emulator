from assembler import assemble
from emulator import Emulator

# Dá se i načíst ze souboru (.asm)
code = """
segment code
        MOV BX, data
        MOV DS, BX
        MOV BX, n
        MOV AL, [BX]
        nop             ; V AL by mělo být 42 
        HLT

segment data
n       db 42
x       resb 4
y       db 0ABh
"""

# Převést na bytecode
program = assemble(code)

# Inicialozovat tím emulátor
emulator = Emulator(program)

# Supstit
emulator.run()

# Výsledek můžete pozorovat např. na registrech
print(emulator.registers)
