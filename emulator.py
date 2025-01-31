from disassembler import *
from assembler import assemble
from converting_functions import *


class Emulator:

    def __init__(self, program):
        self.instructions_counter = 0
        self.MAX_INSTRUCTIONS = 10_000

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
            "JMP": self.JMP, "CALL": self.CALL, "PUSH": self.PUSH,
            "POP": self.POP, "RET": self.RET, "RETF": self.RETF,
            "INT": self.INT
        }

        self.console_input: str = "Hello\nworld\n"
        self.console_output: str = ""

        self._complete_instruction_dictionary()

    def run(self):
        while self.running:
            if self.instructions_counter > self.MAX_INSTRUCTIONS:
                raise Exception(
                    f"Váš program vykonal {self.instructions_counter} instrukcí. Zřejmě došlo k zacyklení. Pokud ne, navyšte hodnotu MAX_INSTRUCTIONS.")
            self.instructions_counter += 1

            # TODO: nechci to dát dovnitř třídy??
            instr, span = parse_next_instruction(
                self.program,
                self.get_register("CS") + self.registers["IP"]
            )

            print(
                f"IP: [{self.registers['CS']}:{self.registers['IP']}], instr: {instr.operation}")

            if instr.operation not in self.instr_methods:
                raise Exception(
                    f"This emulator doesn't support this operation: {instr.operation}")
            self.registers["IP"] += span

            self.instr_methods[instr.operation](instr)

    def _complete_instruction_dictionary(self):
        for instr in SIMPLE_CONDITION_JMPS.keys():
            self.instr_methods[instr] = self.conditional_jump

        for instr in MISSING_CONDITION_JMPS:
            self.instr_methods[instr] = self.conditional_jump

    def get_address(self, arg: Memmory):
        segment = self.get_register(arg.segment)
        offset += arg.displacement

        for reg in arg.source.split("+"):
            offset += self.get_register(reg)

        return segment + offset

    def get_register(self, reg: str):
        reg = reg.upper()

        if reg[1] == "X":
            output = self.get_register(reg[0]+"H") * 2**8
            output += self.get_register(reg[0]+"L")
            return output

        assert reg in self.registers, f"There is no \"{reg}\" register in this emulator."

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
        seg_val = self.get_register(segment)
        val = self.program[seg_val + offset]
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
                output = self.get_byte(arg.segment, offset)
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
        return (self.registers["Fl"] // (2**flag)) % 2

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
        cropped_result = result % 2**opsize

        if CF in flags:
            self.update_cf(result, opsize)

        if OF in flags:
            self.update_of(result, opsize, previous_numbers)

        if SF in flags:
            self.update_sf(cropped_result, opsize)

        if ZF in flags:
            self.update_zf(cropped_result)

        if PF in flags:
            self.update_pf(cropped_result)

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
        self.update_flags(val, instruction.size, [
                          OF, CF, ZF, PF, SF], [val + 1, 1])

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
            offset = from_twos_complement(
                instruction.arguments[0].value, instruction.size)
            offset += 1  # TODO: Why +1!?
            self.registers["IP"] = (self.registers["IP"] + offset) % 2**16

    def CALL(self, instruction: Instruction):
        is_far = isinstance(instruction.arguments[0], Pointer)

        instr = Instruction()
        instr.operation = "PUSH"
        if is_far:
            instr.arguments = [Register("CS")]
            self.PUSH(instr)

        val = self.get_register("IP") + len(instruction.bytes) - 1
        instr.arguments = [Immutable(val)]
        self.PUSH(instr)

        self.JMP(instruction)

    def RET(self, instruction):
        instr = Instruction()
        instr.operation = "POP"
        instr.arguments = [Register("IP")]

        self.POP(instr)

        if instruction.operation == "RETF":
            instr.arguments = [Register("CS")]
            self.POP(instr)

    def RETF(self, instruction):
        self.RET(instruction)

    def relative_jump(self, instruction: Instruction):
        distance = from_twos_complement(
            instruction.arguments[0].value, instruction.size)
        self.set_register("IP", self.get_register("IP") + distance)

    def conditional_jump(self, instruction: Instruction):
        # If is simple condition
        if instruction.operation in SIMPLE_CONDITION_JMPS:
            rules = SIMPLE_CONDITION_JMPS[instruction.operation]

            for flag, expected_value in rules:
                if self.get_flag(flag) != expected_value:
                    return

            self.relative_jump(instruction)
            return

        match instruction.operation:
            case "JL":
                if self.get_flag(SF) != self.get_flag(OF):
                    self.relative_jump(instruction)
            case "JNGE":
                if self.get_flag(SF) != self.get_flag(OF):
                    self.relative_jump(instruction)

            case "JG":
                if self.get_flag(SF) == self.get_flag(OF) and self.get_flag(ZF) == 0:
                    self.relative_jump(instruction)
            case "JNLE":
                if self.get_flag(SF) == self.get_flag(OF) and self.get_flag(ZF) == 0:
                    self.relative_jump(instruction)

            case "JLE":
                if self.get_flag(SF) != self.get_flag(OF) or self.get_flag(ZF) == 1:
                    self.relative_jump(instruction)
            case "JNG":
                if self.get_flag(SF) != self.get_flag(OF) or self.get_flag(ZF) == 1:
                    self.relative_jump(instruction)

            case "JGE":
                if self.get_flag(SF) == self.get_flag(OF):
                    self.relative_jump(instruction)
            case "JNL":
                if self.get_flag(SF) == self.get_flag(OF):
                    self.relative_jump(instruction)
            case _:
                raise Exception(
                    "There was a bug in emulator. Please contact developers. (ErrCode: 435)")

    # ------- STACK INSTRUCTIONS: --------
    def PUSH(self, instruction):
        val = self.get_value(instruction.arguments[0])

        sp = (self.get_register("SP") - 2) % 2**16
        self.set_register("SP", sp)

        self.set_byte('SS', sp, val % 2**8)
        self.set_byte('SS', sp + 1, val // 2**8)

    def POP(self, instruction):
        sp = self.get_register("SP")

        val = self.get_byte('SS', sp)
        val += self.get_byte('SS', sp + 1) * 2**8

        self.set_value(instruction.arguments[0], val, instruction.size)
        self.set_register("SP", (sp + 2) % 2**16)

    # ------- INTERUPT INSTRUCTIONS: --------

    def INT(self, instruction):
        # Handle interupt
        # TODO: Handling vlastního vektoru přerušení
        if instruction.arguments[0].value == 0x21:
            self.INT21h(instruction)

    def INT21h(self, instruction):
        """Loads one byte from console."""
        match self.get_register("AH"):
            case 0x01:  # Načíst bajt z konzole
                if self.console_input == "":
                    self.set_register("AL", 0)
                    self.set_flag(ZF, 1)
                else:
                    self.set_register("AL", ord(self.console_input[0]))
                    self.console_input = self.console_input[1:]
                    self.set_flag(ZF, 0)

            case 0x02:  # Vypsat znak
                self.console_output += chr(self.get_register("DL"))

            case 0x09:  # Vypsat řetězec
                offset = self.get_register("DX")
                byte = self.get_byte("DS", offset)
                while byte != 0:
                    self.console_output += chr(byte)
                    offset += 1
                    byte = self.get_byte("DS", offset)

            case 0x0A:  # Načíst řetězec
                offset = self.get_register("DX")
                max_len = self.get_byte("DS", offset)  # Length

                if self.console_input == "":
                    self.set_byte("DS", offset + 1, 0)
                    self.set_byte("DS", offset + 2, 0)
                    self.set_flag(ZF, 1)
                    return

                for i in range(max_len):
                    char = self.console_input[0]
                    self.console_input = self.console_input[1:]

                    if char == "\n":
                        break

                    self.set_byte("DS", offset + i + 2, ord(char))

                self.set_byte("DS", offset + 1, i)

    def IRET(self, instruction):
        pass

    # ------- ANOTHER INSTRUCTIONS: --------

    def NOP(self, instruction):
        pass  # Already implemented ;-)

    def CBW(self, instruction):
        pass

    # ROL, ROR, RCR, RCL - Rotate
    # SAL, SHL, SAR, SHR - Shift

    # STACK - Zvláštní úloha
    # PUSH, POP

    # CALL, RET

    # INTERUPTIONS - Zvláštní úloha
    # INT, IRET

    def HLT(self, instruction):
        # Už jsme ji pro Vás naprogramovali ;-)
        self.running = False


def get_bit(number: int, position: int):
    return (number // 2**position) % 2


if __name__ == "__main__":

    funkcni_cteni_a_psani_na_terminal = """
segment code
        MOV BX, data
        MOV DS, BX

        MOV AL, 9

loop_s  MOV CH, AL
        MOV AH, 1
        INT 21h     ; Load character
        JZ konec
        MOV AH, 2
        MOV DL, AL
        INT 21h     ; Print space
        MOV DL, 32
        INT 21h     ; Print space
        JMP FAR loop_s

konec   HLT


segment data
n       db 97,98,0
"""
    test_code = """
segment code
        MOV BX, data
        MOV DS, BX

        MOV DL, [nums]
        MOV DI, 1
cycle   MOV BL, [nums+DI]
        CMP BL, 0
        JNZ nozero
        JMP end
nozero  CMP BL, DL
        JB bellow
        JMP else
bellow  INC BL
        JMP endif
else    JA above
        JMP endif
above   DEC BL
endif   MOV byte [nums+DI], BL
        ADD DI,1
        JMP cycle
end     HLT

segment data
nums    db 64
        db 66
        db 64
        db 9
        db 0
"""

    brandejs_kostra = """
segment	code
..start	mov bx,data
	mov ds,bx
	mov bx,stack
	mov ss,bx
	mov sp,dno
    MOV BX, muj_stack
    MOV ES, BX

    MOV AX, 7
    MOV ES:[1], AX

	mov dx,mesg
	mov ah,9
	int 21h
	hlt

segment	data
bajt	db 12h
slovo	dw 2356h
mesg	db 'Ahoj','$'

segment	stack
	resb 16
dno:	db ?

segment muj_stack
    db 123
    resb 16

"""

    program = assemble(brandejs_kostra)
    print(program)

    e = Emulator(program)
    # e.registers["DS"] = 0  # For debugging purposes
    e.run()
    print(e.registers)
    print([hex(b) for b in e.program if b is not None])
    print(e.program)
    print("Console output:", e.console_output.replace("\n", "\\n"))
