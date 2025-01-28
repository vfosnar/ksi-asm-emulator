from disassembler import *
from assembler import assemble

# Flags
Flag = int
CF, PF, ZF, SF, OF = 0, 2, 6, 7, 11


MAX_INSTRUCTIONS = 500


class Emulator:

    def __init__(self, program):
        self.instructions_counter = 0

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

            "Fl": 0  # Flags register
        }

        self.program = program  # Seznam bajtů
        self.running = True  # Může být uspáno pomocí instrukce HLT

        self.instr_methods = {
            "MOV": self.MOV, "ADD": self.ADD, "ADC": self.ADC,
            "SUB": self.SUB, "SBB": self.SBB, "AND": self.AND,
            "OR": self.OR,   "XOR": self.XOR, "NEG": self.NEG,
            "NOP": self.NOP, "INC": self.INC, "DEC": self.DEC,
            "HLT": self.HLT, "CMP": self.CMP, "TEST": self.TEST,
            "JMP": self.JMP, "CALL": self.CALL, "JO": self.JO,
        }

    def run(self):
        while self.running:
            if self.instructions_counter > MAX_INSTRUCTIONS:
                raise Exception(
                    f"Váš program vykonal {self.instructions_counter} instrukcí. Zřejmě došlo k zacyklení. Pokud ne, navyšte hodnotu MAX_INSTRUCTIONS.")
            self.instructions_counter += 1

            # TODO: nechci to dát dovnitř třídy??
            instr, span = parse_next_instruction(
                self.program,
                self.get_register("CS") + self.registers["IP"]
            )
            self.registers["IP"] += span

            if instr.operation not in self.instr_methods:
                raise Exception(
                    f"This emulator doesn't support this operation: {instr.operation}")

            self.instr_methods[instr.operation](instr)

    def get_address(self, arg: Memmory):
        segment = self.get_register(arg.segment)
        offset += arg.displacement

        for reg in arg.source.split("+"):
            offset += self.get_register(reg)

        return segment + offset

    def get_register(self, reg: str):
        reg = reg.upper()
        assert reg in self.registers, f"There is no \"{reg}\" register in this emulator."

        if reg[1] == "X":
            output = self.get_register(reg[0]+"H") * 2**8
            output += self.get_register(reg[0]+"L")
            return output

        output = self.registers[reg]

        if reg == "DS" and output is None:
            raise Exception("Nemáte nastavený registr pro datový segment.")

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
            assert 0 <= val < 2**8
        else:
            assert 0 <= val < 2**16

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
        f_reg = self.registers["Fl"]
        f_reg = f_reg & ~(1 << flag)  # Make the flag 0

        if val:
            f_reg = f_reg | (1 << flag)

        self.registers["Fl"] = f_reg

    def get_flag(self, flag: Flag):
        f_reg = self.registers["Fl"]
        return (f_reg // (2**flag)) % 2

    def update_pf(self, result):
        counter = 0
        for _ in range(8):  # Kontroluje se dolní osmice
            counter += result % 2
            result //= 2

        self.set_flag(PF, counter % 2 == 0)

    def update_zf(self, result):
        self.set_flag(ZF, result == 0)

    def update_sf(self, result, opsize):
        """Sets the sign flag."""
        sign = result // 2**(8*opsize - 1)
        self.set_flag(SF, sign == 1)

    def update_cf(self, result, opsize):
        self.set_flag(CF, result >= 2**opsize)

    def update_of(self, result, opsize, numbers: list[int]):
        assert len(numbers) == 2, "Pro výpočet přetečení vložte dvě čísla."

        sign1 = get_bit(numbers[0], opsize - 1)
        sign2 = get_bit(numbers[1], opsize - 1)
        sign_res = get_bit(result, opsize - 1)

        is_overflow = (sign1 == sign2) and (sign1 != sign_res)
        self.set_flag(OF, is_overflow)

    def update_flags(self, result: int, opsize: int, flags: list[int],
                     previous_numbers: list[int] = []  # TODO: Lepší jméno
                     ):
        """Nastaví požadované příznaky. Výsledek vkládejte v přímém kódu s případným přetečením."""
        if CF in flags:
            self.update_cf(result, opsize)

        if OF in flags:
            self.update_of(result, opsize, previous_numbers)

        result = result % 2**opsize

        if SF in flags:
            self.update_sf(result, opsize)

        if ZF in flags:
            self.update_zf(result)

        if PF in flags:
            self.update_pf(result)

    # ======== INSTRUCTIONS: ==========
    # ------- MOVE INSTRUCTIONS: --------

    def MOV(self, instruction: Instruction):
        to_insert = self.get_value(instruction.arguments[1])
        self.set_value(instruction.arguments[0], to_insert, instruction.size)
        # MOV Nenastavouje příznaky

    # ------- ARITMETIC INSTRUCTION: --------
    def ADD(self, instruction: Instruction):
        val1 = self.get_value(instruction.arguments[0])
        val2 = self.get_value(instruction.arguments[1])

        result = val1 + val2

        self.set_value(instruction.arguments[0], result % (
            2**instruction.size), instruction.size)
        self.update_flags(result, instruction.size, [
                          OF, CF, ZF, PF, SF], [val1, val2])

    def ADC(self, instruction):
        val1 = self.get_value(instruction.arguments[0])
        val2 = self.get_value(instruction.arguments[1])
        cf = 1 if self.get_flag(CF) else 0
        result = val1 + val2 + cf

        self.set_value(instruction.arguments[0], result % (
            2**instruction.size), instruction.size)
        self.update_flags(result, instruction.size, [
                          OF, CF, ZF, PF, SF], [val1, val2])

    def SUB(self, instruction):
        val1 = self.get_value(instruction.arguments[0])
        val2 = self.get_value(instruction.arguments[1])
        result = val1 - val2

        self.set_value(
            instruction.arguments[0], result % 2**(instruction.size), instruction.size)
        self.update_flags(result, instruction.size, [
                          OF, CF, ZF, PF, SF], [val1, val2])

    def SBB(self, instruction):
        val1 = self.get_value(instruction.arguments[0])
        val2 = self.get_value(instruction.arguments[1])
        cf = 1 if self.get_flag(CF) else 0
        result = val1 - val2 - cf

        self.set_value(
            instruction.arguments[0], result % 2**(instruction.size), instruction.size)
        self.update_flags(result, instruction.size, [
                          OF, CF, ZF, PF, SF], [val1, val2])

    def INC(self, instruction):
        val = self.get_value(instruction.arguments[0]) + 1
        self.set_value(instruction.arguments[0], val % (
            2**instruction.size), instruction.size)
        self.update_flags(val, instruction.size, [OF, CF, ZF, PF, SF])

    def DEC(self, instruction):
        val = self.get_value(instruction.arguments[0]) - 1
        self.set_value(instruction.arguments[0], val % (
            2**instruction.size), instruction.size)
        self.update_flags(val, instruction.size, [OF, CF, ZF, PF, SF])

    def NEG(self, instruction):
        val = self.get_value(instruction.arguments[0])
        val = ~val + 1
        self.set_value(instruction.arguments[0], val % (
            2**instruction.size), instruction.size)
        self.update_flags(val, instruction.size, [OF, CF, ZF, PF, SF])

    def MUL(self, instruction):
        pass

    def IMUL(self, instruction):
        pass

    def DIV(self, instruction):
        pass

    def IDIV(self, instruction):
        pass

    # ------- LOGIC INSTRUCTIONS: --------
    def AND(self, instruction):
        val1 = self.get_value(instruction.arguments[0])
        val2 = self.get_value(instruction.arguments[1])
        result = val1 & val2

        self.set_value(instruction.arguments[0], result, instruction.size)
        self.update_flags(result, instruction.size, [ZF, PF, SF])

    def OR(self, instruction):
        val1 = self.get_value(instruction.arguments[0])
        val2 = self.get_value(instruction.arguments[1])
        result = val1 | val2

        self.set_value(instruction.arguments[0], result, instruction.size)

        self.update_sf(result, instruction.size)
        self.update_zf(result)
        self.update_pf(result)

    def XOR(self, instruction):
        val1 = self.get_value(instruction.arguments[0])
        val2 = self.get_value(instruction.arguments[1])
        result = val1 ^ val2

        self.set_value(instruction.arguments[0], result, instruction.size)

        self.update_sf(result, instruction.size)
        self.update_zf(result)
        self.update_pf(result)

    def NOT(self, instruction):
        val1 = self.get_value(instruction.arguments[0])
        result = ~val1
        self.set_value(instruction.arguments[0], result, instruction.size)
        # Nemění příznaky

    def CBW(self, instruction):
        pass

    # ------- COMPARING INSTRUCTIONS: --------
    def CMP(self, instruction):
        val1 = self.get_value(instruction.arguments[0])
        val2 = self.get_value(instruction.arguments[1])
        result = val1 - val2

        self.update_flags(result, instruction.size, [
                          OF, CF, ZF, PF, SF], [val1, val2])

    def TEST(self, instruction):
        # And, akorát se neukládá. Jen nastavuje příznaky (flags)
        val1 = self.get_value(instruction.arguments[0])
        val2 = self.get_value(instruction.arguments[1])
        result = val1 & val2

        self.update_flags(result, instruction.size, [ZF, PF, SF])

    # ------- PROGRAM BRANCHING INSTRUCTIONS: --------
    def JMP(self, instruction):
        if isinstance(instruction.arguments[0], Pointer):
            # Far jump
            self.registers["IP"] = instruction.arguments[0].offset
            self.registers["CS"] = instruction.arguments[0].segment
        else:
            # Near jump
            assert isinstance(instruction.arguments[0], Immutable)
            offset = instruction.arguments[0].value
            raise NotImplemented("TODO: Finish short jump")

    def CALL(self, instruction):
        # TODO:
        pass

    def JO(self, instruction):
        if self.get_flag(OF):
            self.set_register("IP",
                              self.get_register("IP") + instruction.arguments[0].value)

    # ------- ANOTHER INSTRUCTIONS: --------

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


def get_bit(number: int, position: int):
    return (number // 2**position) % 2


if __name__ == "__main__":

    overflwo_test = """
segment code
startt  MOV AL, 127
        ADD AL, 1
        JO konec
        HLT
        JMP FAR startt
konec   HLT
"""

    program = assemble(overflwo_test)
    print(program)

    e = Emulator(program)
    # e.registers["DS"] = 0  # For debugging purposes
    e.run()
    print(e.registers)
    print([hex(b) for b in e.program if b is not None])
