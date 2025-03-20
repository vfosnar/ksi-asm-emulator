from assembler import assemble
from emulator import Emulator

# Dá se i načíst ze souboru (.asm)
code = """
segment code
..start
        MOV AX, stack
        MOV SS, AX
        MOV SP, top

        POP AX          ; F_1
        POP BX          ; F_0
        POP DX          ; n

        PUSH BX         ; vratim F_0
        CMP DX, 1
        JL end          ; pokud je n = 0, program skonci

        PUSH AX         ; vratim F_1

        CMP DX, 2
        JL end

loop:
        CALL func
        DEC DX
        CMP DX, 2
        JL end
        JNC loop

func:
        POP AX         ; F_n-1
        POP BX         ; F_n-2
        
        PUSH AX        ; F_n-1
        ADD AX, BX     ; F_n
        POP CX         ; vratim si F_n-1
        PUSH BX        ; vratim F_n-2
        PUSH CX        ; vratim f_n-1
        PUSH AX        ; ulozim F_n
        RET

end:
        HLT

segment stack
        resb 65530
top:    dw 1  ; F_1
        dw 0  ; F_0
        dw 3  ; n


"""


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
