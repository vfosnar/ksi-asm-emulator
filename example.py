from assembler import assemble
from emulator import Emulator

# Dá se i načíst ze souboru (.asm)
code = """
segment code
        MOV BX, data    ; Pokud chcete používat data, musíte nastavit DS
        MOV DS, BX

        MOV BX, n
        MOV AL, [BX]    ; Do AL se přenese 42
        
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
