from disassembler import *
from assembler import assemble # TODO: Tohle samozřejmě přepsat na jenom funkci assemble()

# Flags
Flag = int
CF, PF, ZF, SF, OF = 0, 2, 6, 7, 11


class Emulator:

    def __init__(self, program):
        self.registers = {
            # 16-bitový registr AX je složen ze dvou 8-botivých registrů AH,AL
            "AL": None,
            "AH": None,

            # Platí i pro registry BX, CX, DX
            "BL": None,
            "BH": None,
            "CL": None,
            "CH": None,
            "DL": None,
            "DH": None,

            "SP": None,  # Stack pointer

            "CS": 0,  # Code segment
            "DS": None,  # Data segment
            "SS": None,  # Stack segment
            "ES": None,  # Extra segment

            "IP": 0,  # Instruction pointer

            "FI": 0  # Flags register
        }

        self.program = program # Seznam bajtů
        self.running = True  # Může být uspáno pomocí instrukce HLT

        self.instr_methods = {
            "MOV": self.MOV, "ADD": self.ADD, "ADC": self.ADC,
            "SUB": self.SUB, "SBB": self.SBB, "AND": self.AND,
            "OR": self.OR,   "XOR": self.XOR, "NEG": self.NEG,
            "NOP": self.NOP, "INC": self.INC, "DEC": self.DEC,
            "HLT": self.HLT, "CMP": self.CMP, "TEST": self.TEST,
        }

    def run(self):
        while self.running:
            # TODO: nechci to dát dovnitř třídy??
            instr, span = parse_next_instruction(
                self.program, 
                self.get_register("CS") + self.registers["IP"]
            )
            self.registers["IP"] += span

            if instr.operation not in self.instr_methods:
                raise Exception(f"This emulator doesn't support this operation: {instr.operation}")
            
            self.instr_methods[instr.operation](instr)

    def get_address(self, arg: Memmory):
        segment = self.get_register(arg.segment)
        offset += arg.displacement

        for reg in arg.source.split("+"):
            offset += self.get_register(reg)

        return segment + offset
    
    def get_register(self, reg: str):
        reg = reg.upper()
        assert reg in REGISTERS, f"There is no \"{reg}\" register in this emulator."

        if reg[1] == "X":
            output = self.get_register(reg[0]+"H") * 2**8
            output += self.get_register(reg[0]+"L")
            return output

        output = self.registers[reg]
        assert output is not None, f"Trying to get value of register {reg} with undefined value."
        return output

    def set_register(self, reg: str, val: int):
        assert val >= 0, f"Do funkce set_register vkládejte hodnotu v přímém kódu, jako nezáporné číslo."

        if reg[1] == "X":
            assert 0 <= val <= 2**16, \
                f"Snažíte se do registru {reg} vložit hodnotu {val}, která je mimo rozsah."
            self.registers[reg[0]+'L'] = val % 2**8
            self.registers[reg[0]+'H'] = val // 2**8
            return

        if reg[1] in ["L", "H"]:
            assert 0 < val < 2**8
        else:
            assert 0 < val < 2**16

        self.registers[reg] = val

    def get_byte(self, segment, offset):
        val = self.program[segment + offset]
        assert val is not None, f"Trying to get value of undefined byte at {segment + offset}."
        return val

    def set_byte(self, segment, offset, value):
        assert 0 <= value <= 2**8
        seg = self.get_register(segment)
        self.program[seg + offset] = value

    def get_value(self, arg: Parameter):
        # Asi autorská pomocná funkce. Ať si to kdyžtak udělají sami.
        output = None

        match arg:
            case Immutable():
                output = arg.value
            case Memmory():
                offset = arg.displacement
                for reg in arg.source.split("+"):
                    if reg != "":
                        offset += self.get_register(reg)
                segment = self.get_register(arg.segment)
                output = self.get_byte(segment, offset)
            case Register():
                output = self.get_register(arg.name)

        return output

    def set_value(self, arg, val, size):
        match arg:
            case Register():
                self.set_register(arg.name, val)
            case Memmory():
                offset = arg.displacement

                if arg.source not in ["", None]:
                    for reg in arg.source.split("+"):
                        offset += self.get_register(reg)

                for i in range(size // 8):
                    self.set_byte(arg.segment, offset + i, val % 2**8)
                    val //= 2**8

    # ------- FLAGS: --------
    def set_flag(self, flag: Flag, val: bool):
        f_reg = self.registers["FI"]
        f_reg = f_reg & ~(1 << flag)  # Make the flag 0

        if val:
            f_reg = f_reg | (1 << flag)

    def get_flag(self, flag: Flag):
        f_reg = self.registers["FI"]
        return (f_reg // (2**flag)) % 2

    def set_pf(self, result):
        counter = 0
        for _ in range(8):  # Kontroluje se dolní osmice
            counter += result % 2
            result //= 2

        self.set_flag(PF, counter % 2 == 0)

    def set_zf(self, result):
        self.set_flag(ZF, result == 0)

    def set_sf(self, result, opsize):
        """Sets the sign flag."""
        sign = result // 2**(8*opsize - 1)
        self.set_flag(SF, sign == 1)

    def set_cf(self, result, opsize):
        carry = result > 2**(8*opsize)
        self.set_flag(CF, carry)

    def set_of(self, result, opsize):
        overflow = not (2**(8*opsize - 1) <= result < 2**(8*opsize))
        self.set_flag(OF, overflow)

    def set_state_flags(self, result: int, opsize: int):
        """Sets the ZF, PF and SF flag."""
        self.set_zf(result)
        self.set_pf(result)
        self.set_sf(result, opsize)    
    
    # ------- INSTRUCTIONS: --------
    def MOV(self, instruction: Instruction):
        assert len(instruction.arguments) == 2
        arg1, arg2 = instruction.arguments

        to_insert = self.get_value(arg2)
        self.set_value(arg1, to_insert, instruction.size)
        # MOV Nenastavouje příznaky

    # ------- ARITMETIC INSTRUCTION: --------
    def ADD(self, instruction):
        # TODO: Dodělat znaménkové přetečení
        val1 = self.get_value(instruction.arguments[0])
        val2 = self.get_value(instruction.arguments[1])

        vysledek = from_2compl(val1, instruction.size) + from_2compl(val2, instruction.size)
        self.set_of(vysledek, instruction.size)

        vysledek %= 2**(8*instruction.size)

        self.set_value(instruction.arguments[0], vysledek, instruction.size)

        self.set_state_flags(vysledek, instruction.size, [OF, CF, ZF, PF, SF])

        self.set_cf(vysledek, instruction.size)
        self.set_sf(vysledek, instruction.size)
        self.set_zf(vysledek)
        self.set_pf(vysledek)

        ...

    def ADC(self, instruction):
        val1 = self.get_value(instruction.arguments[0])
        val2 = self.get_value(instruction.arguments[1])
        cf = 1 if self.get_flag(CF) else 0 
        vysledek = val1 + val2 + cf 
        self.set_value(instruction.arguments[0], vysledek % 2**(instruction.size), instruction.size)
        # TODO: Dodělat flags

    def SUB(self, instruction):
        val1 = self.get_value(instruction.arguments[0])
        val2 = self.get_value(instruction.arguments[1]) 
        result = val1 - val2
        self.set_value(instruction.arguments[0], result % 2**(instruction.size), instruction.size)
        # TODO: Dodělat flags

    def SBB(self, instruction):
        val1 = self.get_value(instruction.arguments[0])
        val2 = self.get_value(instruction.arguments[1])
        cf = 1 if self.get_flag(CF) else 0
        result = val1 - val2 - cf
        self.set_value(instruction.arguments[0], result % 2**(instruction.size), instruction.size)
        # TODO: Dodělat flags

    def INC(self, instruction):
        val = self.get_value(instruction.arguments[0]) + 1
        val %= 2**(8*instruction.size)
        self.set_value(instruction.arguments[0], val, instruction.size)

        self.set_sf(val, instruction.size)
        self.set_zf(val)
        self.set_pf(val)
        self.set_flag(OF, val == 0)  # TODO: Tohle se mi nějak nezdá

    def DEC(self, instruction):
        val = self.get_value(instruction.arguments[0]) - 1
        val %= 2**(8*instruction.size)
        self.set_value(instruction.arguments[0], val, instruction.size)

    def NEG(self, instruction):
        val = self.get_value(instruction.arguments[0])
        val = ~val + 1
        self.set_value(instruction.arguments[0], val % 2**instruction.size, instruction.size)
        # TODO: doplnit flags

    def MUL(self, instruction):
        pass

    def IMUL(self, instruction):
        pass

    def DIV(self, instruction):
        pass

    def IDIV(self, instruction):
        pass

    # ------- LOGICKÉ INSTRUKCE: --------
    def AND(self, instruction):
        val1 = self.get_value(instruction.arguments[0])
        val2 = self.get_value(instruction.arguments[1])
        result = val1 & val2

        self.set_value(instruction.arguments[0], result, instruction.size)

        self.set_sf(result, instruction.size)
        self.set_zf(result)
        self.set_pf(result)

    def OR(self, instruction):
        val1 = self.get_value(instruction.arguments[0])
        val2 = self.get_value(instruction.arguments[1])
        result = val1 | val2

        self.set_value(instruction.arguments[0], result, instruction.size)

        self.set_sf(result, instruction.size)
        self.set_zf(result)
        self.set_pf(result)

    def XOR(self, instruction):
        val1 = self.get_value(instruction.arguments[0])
        val2 = self.get_value(instruction.arguments[1])
        result = val1 ^ val2

        self.set_value(instruction.arguments[0], result, instruction.size)

        self.set_sf(result, instruction.size)
        self.set_zf(result)
        self.set_pf(result)

    def NOT(self, instruction):
        val1 = self.get_value(instruction.arguments[0])
        result = ~val1
        self.set_value(instruction.arguments[0], result, instruction.size)
        # Nemění příznaky

    def CBW(self, instruction): 
        pass

    # ------- POROVNÁVACÍ  INSTRUKCE: --------
    def CMP(self, instruction):
        val1 = self.get_value(instruction.arguments[0])
        val2 = self.get_value(instruction.arguments[1])
        result = val1 - val2

        self.set_state_flags(result, instruction.size)

    def TEST(self, instruction):
        # And, akorát se neukládá. Jen nastavuje příznaky (flags)
        val1 = self.get_value(instruction.arguments[0])
        val2 = self.get_value(instruction.arguments[1])
        result = val1 & val2

        self.set_sf(result, instruction.size)
        self.set_zf(result)
        self.set_pf(result)

    # ------- DALŠÍ INSTRUKCE: --------
    def NOP(self, instruction):
        pass  # Already implemented ;-)

    def CBW(self, instruction):
        pass


    # ROL, ROR, RCR, RCL - Rotate
    # SAL, SHL, SAR, SHR - Shift

    # JUMP - Zvláštní úloha
    # JMP
    # JZ, JNZ, ... - Jumpy

    # STACK - Zvláštní úloha
    # PUSH, POP

    # CALL - Zvláštní úloha
    # CALL, RET

    # INTERUPTIONS - Zvláštní úloha
    # INT, IRET

    def HLT(self, instruction):
        # Už jsme ji pro Vás naprogramovali ;-)
        self.running = False


# TODO: Přemístit na lepší místo; vymyslet lepší název
def to_twos_complement(num, size):
    if num < 0:
        num += 2**size 
    return num

def from_2compl(num, size):
    if num > 2**(size - 1) - 1:
        num -= 2**size
    return num

if __name__ == "__main__":
    code3 = """
segment code
        MOV BX, data

        MOV AL, 11111111b
        MOV AH, 10011001b
        AND AL, AH
        MOV AX, 7
        NEG AX
        HLT


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

    test_code = """
segment code
        MOV BX, data    ; Nastaví datový segment. Není podstatné
        MOV DS, BX      

        MOV AX, 42
        SUB AX, [a]

        MOV BX, 15
        AND BX, 10101010b  ; b na konci označuje binární zápis čísla
        INC BX
        MOV [a], BX

        HLT        

segment data
a       db 12
"""

    program = assemble(code3)
    print(program)

    e = Emulator(program)
    # e.registers["DS"] = 0  # For debugging purposes
    e.run()
    print(e.registers)
    print([hex(b) for b in e.program if b is not None])
    