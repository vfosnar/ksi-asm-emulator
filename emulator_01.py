from disassembler import *


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

    def __init__(self):
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

        self.program = []  # Seznam bajtů
        self.running = True  # Může být uspáno pomocí instrukce HLT

    def run(self):
        while self.running:
            instr, span = parse_next_instruction(
                self.program, self.registers["IP"])
            self.registers["IP"] += span
            match instr.operation:
                case "ADD":
                    self.ADD(instr)
                case "MOV":
                    self.MOV(instr)
                case "HLT":
                    self.HLT()

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

        assert 0 < val < 2**8
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
                    offset += self.get_register(reg)

                output = self.get_byte(arg.segment, offset)
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

    def set_of(self, before: int, after: int, opsize: int):

        ...

    def MOV(self, instruction: Instruction):
        assert len(instruction.arguments) == 2
        arg1, arg2 = instruction.arguments

        to_insert = self.get_value(arg2)
        self.set_value(arg1, to_insert, instruction.size)

    def ADD(self, instruction):
        # TODO: Dodělat znaménkové přetečení
        vysledek = self.get_value(instruction.arguments[0])
        vysledek += self.get_value(instruction.arguments[1])
        self.set_cf(vysledek, instruction.size)
        vysledek %= 2**(8*instruction.size)

        self.set_value(instruction.arguments[0], vysledek, instruction.size)

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


if __name__ == "__main__":

    e = Emulator()
    e.program = [
        0xB0, 0x07,  # MOV AL, 7
        0xB4, 0x08,  # MOV AH, 8
        0x00, 0xE0,  # ADD AL, AH
        0xF4,  # HLT
    ] + [None for _ in range(42)]

    e.run()
    print(e.registers)

    # i1 = Instruction()
    # i1.operation = "MOV"
    # i1.arguments = [
    #     Register("AL"),
    #     Register("DL"),
    #     # Immutable(45)
    # ]

    # e = Emulator()
    # e.program = [None for _ in range(42)]

    # e.registers["DL"] = 123
    # print(e.registers["AL"])
    # e.MOV(i1)
    # print(e.registers["AL"])

    # e.registers["DS"] = 0

    # i2 = Instruction()
    # i2.operation = "MOV"
    # i2.size = 16
    # i2.arguments = [
    #     Memmory(None, 0, "DS"),
    #     Immutable(2735),
    # ]

    # print(e.program[0])
    # e.MOV(i2)
    # print(e.program[0])
    # print(e.program[1])

    # e.set_register("AX", 0b1111_1111_1111_1111)

    # print(e.get_register("AX"))

    # i3 = Instruction()
    # i3.operation = "AND"
    # i3.size = 16
    # i3.arguments = [
    #     Register("AX"),
    #     Immutable(0b11101),
    # ]
    # e.XOR(i3)
    # print(e.get_register("AX"))
