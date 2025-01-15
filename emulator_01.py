
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
        registers = {
            # 16-bitový registr AX je složen ze dvou 8-botivých registrů AH,AL
            "AL": None,
            "AH": None,

            # Obdobně to mají i registry BX, CX, DX
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

            # Procesory mívají ještě další registy. Ty ale v této vlně nevyužijeme
        }

        self.program = []  # Seznam se segmenty
        self.running = True  # Může být uspáno pomocí instrukce HLT

    def next_instruction(self):

        ...

    def run(self):
        # Předpokládám, že zde dostanu validní poskládaný kód
        ...

    def get_data(self, segment, offset):
        assert True  # requested value is not None
        ...

    def save_data(self, segment, offset, span, value):
        # Parametr span určuje, kolik bajtů se má uložit
        ...

    def MOV(self, instruction):
        pass

    def ADD(self, r1, r2):
        pass

    def ADC(self, p1, p2):
        pass

    def SUB(self, p1, p2):
        pass

    def SBB(self, p1, p2):
        pass

    def INC(self, p1):
        pass

    def DEC(self, p1):
        pass

    def CMP(self, p1, p2):
        pass

    def CBW(self, p1, p2):
        pass

    # TODO: Chceme i CBD??
    # (Convert Byte to Doubleword)

    # ? Jak implementovat tyto??
    # MUL, IMUL, DIV, IDIV - doufám, že ne

    def AND(self, p1, p2):
        # AL & AH (pythonovksý operátor)
        pass

    def OR(self, p1, p2):
        # AL | AH (pythonovksý operátor)
        pass

    def XOR(self, p1, p2):
        # (p1 | p2) - (p1 & p2)
        pass

    def NOT(self, p1):
        # (AL - 2^8) * -1
        # (AX - 2^16) * -1
        pass

    def TEST(self, p1, p2):
        # And, akorát se neukládá. Jen nastavují příznaky
        pass

    def NOP(self):
        # Already implemented
        return

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

    def print_registers(self):  # Možná by se to hodilo, možná ne??
        x = """
        -------------
            High   Low 
          ┌─────┬─────┐
        A │ 24h │ 42h │
          ├─────┼─────┤
        B │ 24h │ 42h │
          ├─────┼─────┤
        C │ und │ und │
          ├─────┼─────┤
        D │ und │ und │
          └─────┴─────┘
        
           ┌──────┐
        AX │ 224h │
           ├──────┤
        BX | 244h |
           └──────┘

        """

        pass

    def _ORG_validate_registy():
        # All registers must be either None or (Int 0-255)
        ...


class Instruction:
    def __init__(self):
        self.prefix = None
        self.type = None  # String like "MOV" or "ADD"
        self.arguments = []


PREFIXES = {
    0x2E: "CS",
    0x3E: "DS",
    0x26: "ES",
    0x36: "SS",
    # Samozřejmě existuje spousta dalších prefixů s různou funkcionalitou,
    # nám ale budou stačit tyto, které blíže specifikují registr
}

OPCODES = {
    "B0-B1": "MOV reg, imm8",
    "B8-BF": "MOV reg, imm16/imm32",
    "89": "MOV reg/mem, reg",
    "8B": "MOV reg, reg/mem",


    "01": "ADD reg/mem, reg",
    "03": "ADD reg, reg/mem",

    0x90: "NOP"
}


def parse_next_instruction(segment, IP):
    # vrací:  (instrukce, [args], modifier, pocet_bitu)
    # např.:  ("MOV", ["AX", 5], None, 4)
    # nebo:   ("MOV", [1234, "AX"], "DS", 5)
    # nebo:   ("NOP", [], None, 1)
    span = 0

    def getByte():
        nonlocal span
        my_b = segment[IP + span]
        span += 1
        return my_b

    instruction = Instruction()

    a = getByte()

    if a in PREFIXES:
        instruction.prefix = PREFIXES[a]

        a = getByte()

    return instruction


if __name__ == "__main__":
    assembled = [
        # MOV AX, cs:[123h]
        0x2E,  # prefix: CS
        0xA1,  # instrukce: MOV AX, mem
        0x23,  # parametry: 123h (low endianita)
        0x01,

        0x90,  # NOP
        0x90,  # NOP
    ]

    abc = parse_next_instruction(assembled, 0)

    print(abc)

    print("Hello world")
    program = """
segment code
navesti MOV AL, 2
"""

    code = [
        Byte("instruction", "MOV AL _"),  # Načte do AL číslo 2
        Byte("data", 2),
        Byte("instruction", "HLT"),

    ]
    print("Ahoj svete")


# ========== DALŠÍ ZBYTEČNOSTI =================
# Pokud vás zajímají technické informace, klidně si to můžete
# prostudovat, ale není to předmětem této (ani jiné) úlohy.


class Byte:
    def __init__(self, value):
        self.value = value


# def next_instruction(segment, IP):  # Returns the
#     prefix = None
#     b: Byte = segment[IP]
#     instruction: str = b.value
#     span += 1

#     if b.type == "Prefix":
#         prefix = b.value
#         b = segment[IP + span]
#         instruction = b.value
#         IP += 1

#     if not "_" in instruction:
#         return (instruction, None, span)
