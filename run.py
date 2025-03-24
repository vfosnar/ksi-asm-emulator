#!/usr/bin/env python3

import sys
from assembler import assemble
from emulator import Emulator

file_path = sys.argv[1]
with open(file_path, "r") as file:
    code = file.read()

# Převést na bajtkód
program, start, lines_info = assemble(code)

# Inicializovat tím emulátor
e = Emulator(program, start, lines_info)

# [volitelné] Nastavit vstup konzole, upravit maximální počet instrukcí, vypnutí debug módu (vypisování jednotlivých kroků)
e.console_input = "Hello\nWorld\n"
e.max_instructions = 100_000
# e.debugging_mode = False

# Supstit
e.run()

# Výsledek můžete pozorovat např. na registrech, výstupu konzole nebo na statistikách instrukcí
print(e.registers)
print("Console output:", e.console_output.replace("\n", "\\n"))
print(e.statistics)

print(e.program)
