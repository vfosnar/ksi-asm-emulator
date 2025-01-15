

def convert_to_instructions(line: str) -> list[int]:  # List bajtů
    output = []

    line = line.split(";", 1)[0]
    is_first_char = line[0].isalpha()

    parts = line.split()

    if is_first_char:
        parts.pop(0)

    match parts[0]:
        case "NOP":
            return [0x90]
        case "MOV":
            return convert_ADD(*parts[1:])

    assert False, f"Instrukce {parts[0]} není implementována"


def zpracuj_dalsi_instrukci():
    # 1) Načíst byte.
    #    - Pokud je prefix, načti další a pamatuj si ho
    # 2) Zpracuj opcode - dešifruj, k čemu patří
    # (early exit, pokud nepotřebuji ModR/M)
    # 3) Zpracuj ModR/M, pokud ho potřebuju
    # 4) Pokud potřebuji další data, tak si je načtu (poznám podle R/M bitů)¨
    # Mám to ;-)

    ...


class Instruction:
    def __init__(self):
        self.opcode = 9
        self.prefix = None  # | "DS" | "CS" | ...
        self.modrm = None  # |


if __name__ == "__main__":

    program = [
        "   MOV AX, BX",
        "   NOP         ; Tohle je tu, aby to nic nedělalo",
        "navest ADD CX, DX"
    ]

    for line in program:
        print(convert_to_instructions(line))
