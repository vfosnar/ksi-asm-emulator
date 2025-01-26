from disassembler import *
from assembler import * # TODO: Tohle samozřejmě přepsat na jenom funkci assemble()

class Byte:
    def __init__(self, type, value):
        self.type = "prefix"  # Prefix | instruction | data
        self.value = "CS"

        self.type = "instruction"
        self.value = "MOV _, AX"

        self.type = "data"
        self.value = 125


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

            "CS": None,  # Code segment
            "DS": None,  # Data segment
            "SS": None,  # Stack segment
            "ES": None,  # Extra segment

            "IP": 0,  # Instruction pointer

            # Flags (zde se ukládají informace ohledně operací) TODO: Líp vysvětlit
            "FI": 0
        }

        self.program = program # Seznam bajtů
        self.running = True  # Může být uspáno pomocí instrukce HLT

    def run(self):
        while self.running:
            instr, span = parse_next_instruction(
                self.program, self.registers["IP"])
            self.registers["IP"] += span
            match instr.operation:
                case "MOV":
                    self.MOV(instr)
                case "ADD":
                    self.ADD(instr)
                # TODO Donplnit zbyle instrukce

                case "AND":
                    self.AND(instr)

                case "OR":
                    self.OR(instr)
                case "XOR":
                    self.XOR(instr)
                
                case "NEG":
                    self.NEG(instr)


                case "NOP":
                    self.NOP(instr)
                case "HLT":
                    self.HLT()
                case unknown:
                    raise Exception(f"This emulator doesn't support this operation: {unknown}")

    def set_flag(self, flag: Flag, val: bool):
        f_reg = self.registers["FI"]
        f_reg = f_reg & ~(1 << flag)  # Make the flag 0

        if val:
            f_reg = f_reg | (1 << flag)

    def get_flag(self, flag: Flag):
        f_reg = self.registers["FI"]
        return (f_reg // (2**flag)) % 2

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

    def get_address(self, arg: Memmory):
        segment = self.get_register(arg.segment)
        offset += arg.displacement

        for reg in arg.source.split("+"):
            offset += self.get_register(reg)

        return segment + offset

    def set_register(self, reg: str, val: int):
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

    # Autorská pomocná funkce
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

    # Autorská pomocná funkce
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

    def set_flags(self, result: int, opsize: int, flags: list[Flag]):
        for flag in flags:
            if flag not in [OF, CF, ZF, PF, SF]:
                raise Exception(f"Flag {flag} is not supported.")
            self.set_flag(flag, False)
        
        # result is in twos complement
        if OF in flags and not (2**(opsize - 1) <= result < 2**opsize):
            self.set_flag(OF, True)
        
        if CF in flags:
            is_carry = not (2**(8*opsize) <= result < 2**(8*opsize + 1))
            self.set_flag(CF, is_carry)

        if ZF in flags:
            self.set_flag(ZF, result == 0)

        # Need binary number
        result = to_twos_complement(result, opsize)

        if PF in flags:
            counter = 0
            for _ in range(8):
                counter += result % 2
                result //= 2
            self.set_flag(PF, counter % 2 == 0)
        
        if SF in flags:
            sign = result // 2**(8*opsize - 1)
            self.set_flag(SF, sign == 1)
        
    def MOV(self, instruction: Instruction):
        assert len(instruction.arguments) == 2
        arg1, arg2 = instruction.arguments

        to_insert = self.get_value(arg2)
        self.set_value(arg1, to_insert, instruction.size)
        # MOV Nenastavouje příznaky

    def ADD(self, instruction):
        # TODO: Dodělat znaménkové přetečení
        val1 = self.get_value(instruction.arguments[0])
        val2 = self.get_value(instruction.arguments[1])

        vysledek = from_2compl(val1, instruction.size) + from_2compl(val2, instruction.size)
        self.set_of(vysledek, instruction.size)

        vysledek %= 2**(8*instruction.size)

        self.set_value(instruction.arguments[0], vysledek, instruction.size)

        self.set_flags(vysledek, instruction.size, [OF, CF, ZF, PF, SF])

        self.set_cf(vysledek, instruction.size)
        self.set_sf(vysledek, instruction.size)
        self.set_zf(vysledek)
        self.set_pf(vysledek)

        ...

    def ADC(self, instruction):
        pass

    def SUB(self, instruction):
        pass

    def SBB(self, instruction):
        pass

    def INC(self, instruction):
        val = self.get_value(instruction.arguments[0]) + 1
        val %= 2**(8*instruction.size)
        self.set_value(instruction.arguments[0], val, instruction.size)

        self.set_sf(val, instruction.size)
        self.set_zf(val)
        self.set_pf(val)
        self.set_flag(OF, val == 0)  # TODO: Tohle se mi nějak nezdá

    def DEC(self, instruction):
        pass

    def NEG(self, instruction):
        val = self.get_value(instruction.arguments[0])
        val = ~val + 1
        self.set_value(instruction.arguments[0], val, instruction.size)
        # TODO: doplnit flags

    def CMP(self, instruction):
        pass

    def CBW(self, instruction):
        pass

    # TODO: Chceme i CBD??
    # (Convert Byte to Doubleword)

    # ? Jak implementovat tyto??
    # MUL, IMUL, DIV, IDIV - doufám, že ne

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

    def TEST(self, instruction):
        # And, akorát se neukládá. Jen nastavuje příznaky (flags)
        val1 = self.get_value(instruction.arguments[0])
        val2 = self.get_value(instruction.arguments[1])
        result = val1 & val2

        self.set_sf(result, instruction.size)
        self.set_zf(result)
        self.set_pf(result)

    def NOP(self, instruction):
        # Already implemented for you ;-)
        pass

    # ROL, ROR, RCR, RCL - Rotate
    # SAL, SHL, SAR, SHR - Shift

    # JUMP - Zvláštní úloha
    # JMP
    # JZ, JNZ, ... - Jumpy
    # !? Krátký skok, dlouhý skok - to budou taky implementovat??

    # STACK - Zvláštní úloha
    # PUSH, POP

    # CALL - Zvláštní úloha
    # CALL, RET

    # INTERUPTIONS - Zvláštní úloha
    # INT, IRET

    def HLT(self):
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

    program = assemble(code3)
    print(program)

    e = Emulator(program)
    # e.registers["DS"] = 0  # For debugging purposes
    e.run()
    print(e.registers)
    print([hex(b) for b in e.program if b is not None])
    