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

            "IP": None,  # Instruction pointer

            # Flags (zde se ukládají informace ohledně operací) TODO: Líp vysvětlit
            "FI": 0
        }

        self.program = []  # Seznam bajtů
        self.running = True  # Může být uspáno pomocí instrukce HLT

    def run(self):
        # Předpokládám, že zde dostanu validní poskládaný kód
        ...

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
            output = self.get_register(reg[0]+"H") * 2**7
            output += self.get_register(reg[0]+"L")            
            return output
        
        output = self.registers[reg]
        assert output is not None, f"Trying to get value of register {reg} with undefined value."        
        return output

    def set_register(self, reg: str, val: int):
        if reg[1] == "X":
            assert 0 < val < 2**16, \
                f"Snažíte se do registru {reg} vložit hodnotu {val}, která je mimo rozsah."
            self.registers[reg[0]+'L'] = val % 2**8
            self.registers[reg[0]+'H'] = val // 2**8
            return

        assert 0 < val < 2**8
        self.registers[reg] = val

    def get_byte(self, segment, offset):
        assert True  # requested value is not None
        ...

    def set_byte(self, segment, offset, span, value):
        # Parametr span určuje, kolik bajtů se má uložit
        ...

    # Autorský pomocná funkce
    def get_value(self, arg):
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

    # Autorský pomocná funkce
    def set_value(self, arg, val):
        match arg:
            case Register():
                self.set_register(arg.name, val)
            case Memmory():
                offset = arg.displacement
                for reg in arg.source.split("+"):
                    offset += self.get_register(reg)

                # LENGTH!!??
                self.set_byte(arg.segment, offset + i, ..., val)

    def set_pf(self, result):
        counter = 0
        for _ in range(8):
            counter += result % 2
            result //= 2
        
        self.set_flag(PF, counter % 2 == 0)

    def set_cf(self, result, opsize):
        carry = result > 2**(8*opsize)
        self.set_flag(CF, carry)
    
    def set_of(self, result, opsize):
        ...


    def MOV(self, arg1, arg2):
        to_insert = 0  # Dummy value

        # First get the second value
        match arg2:
            case Immutable():
                to_insert = arg2.value
            case Memmory():
                offset = arg2.displacement
                for reg in arg2.source.split("+"):
                    offset += self.get_register(reg)

                to_insert = self.get_byte(arg2.segment, offset)
            case Register():
                to_insert = self.get_register(arg2.name)
            case _:
                raise Exception("Unsupported type of second argument in MOV")
            
        # Then insert it where it belongs
        match arg1:
            case Register():
                self.set_register(arg1.name, to_insert)
            case Memmory():
                offset = arg2.displacement
                for reg in arg2.source.split("+"):
                    offset += self.get_register(reg)

                # LENGTH!!??
                self.set_byte(arg2.segment, offset + i, ..., to_insert)

    def ADD(self, arg1, arg2):
        vysledek = self.get_value(arg1)
        vysledek += self.get_value(arg2)
        # vysledek += self.get_flag(OF) % 2  # For ADC

        # I need the operation size.
        # self.set_value(arg1, vysledek % )

        ...

    def ADC(self, instruction):
        pass

    def SUB(self, instruction):
        pass

    def SBB(self, instruction):
        pass

    def INC(self, instruction):
        pass

    def DEC(self, instruction):
        pass

    def CMP(self, instruction):
        pass

    def CBW(self, instruction):
        pass

    # TODO: Chceme i CBD??
    # (Convert Byte to Doubleword)

    # ? Jak implementovat tyto??
    # MUL, IMUL, DIV, IDIV - doufám, že ne

    def AND(self, instruction):
        # AL & AH (pythonovksý operátor)
        pass

    def OR(self, instruction):
        # AL | AH (pythonovksý operátor)
        pass

    def XOR(self, instruction):
        # (p1 | p2) - (p1 & p2)
        pass

    def NOT(self, instruction):
        # (AL - 2^8) * -1
        # (AX - 2^16) * -1
        pass

    def TEST(self, instruction):
        # And, akorát se neukládá. Jen nastavuje příznaky (flags)
        pass

    def NOP(self, instruction):
        # Already implemented ;-)
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
        """ 
        Uspí procesor (pro účely této úlohy se používá pro 
        ukončení programu - jinak by procesor porkačoval v načítání 
        instrukcí).
        * Už jsme ji pro Vás naprogramovali ;-)
        """
        self.running = False




if __name__ == "__main__":
    i = Instruction()
    i.operation = "MOV"
    i.arguments = [
        Register("AL"),
        Register("DL"),
        # Immutable(45)
    ]

    e = Emulator()

    e.registers["DL"] = 123
    e.MOV(*i.arguments)
    print(e.registers["AL"])


