from disassembler import *

class Byte:
    def __init__(self, type, value):
        self.type = "prefix"  # Prefix | instruction | data
        self.value = "CS"

        self.type = "instruction"
        self.value = "MOV _, AX"

        self.type = "data"
        self.value = 125


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

        self.program = []  # Seznam se segmenty
        self.running = True  # Může být uspáno pomocí instrukce HLT

    def run(self):
        # Předpokládám, že zde dostanu validní poskládaný kód
        ...


    def get_register(self, reg):
        assert reg in REGISTERS

        if reg[1] == "X":
            output = self.registers[reg[0]+"H"] << 8
            output += self.registers[reg[0]+"L"]
            return output
        
        return self.registers[reg]

    def load_register(self, reg: str, val: int):
        if reg[1] == "X":
            assert 0 < val < 2**16
            self.registers[reg[0]+'L'] = val % 2**8
            self.registers[reg[0]+'H'] = val // 2**8
            return

        assert 0 < val < 2**8
        self.registers[reg] = val

    def get_byte(self, segment, offset):
        assert True  # requested value is not None
        ...

    def load_byte(self, segment, offset, span, value):
        # Parametr span určuje, kolik bajtů se má uložit
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
                self.load_register(arg1.name, to_insert)
            case Memmory():
                offset = arg2.displacement
                for reg in arg2.source.split("+"):
                    offset += self.get_register(reg)

                # LENGTH!!??
                self.load_byte(arg2.segment, offset + i, ..., to_insert)

    def ADD(self, instruction):
        pass

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
        Immutable(45)
    ]

    e = Emulator()
    e.MOV(i)

