

def convert_to_instructions(line: str) -> list[int]:  # List bajtů
    output = []

    line = line.split(";", 1)[0]
    is_first_char = line[0].isalpha()

    things = line.split()

    if is_first_char:
        things.pop(0)

    match things[0]:
        case "NOP":
            return [0x90]
        case "MOV":
            return convert_ADD(*things[1:])

    assert False, f"Instrukce {things[0]} není implementována"


def convert_ADD(p1, p2):
    return ["Tady bude add"]


if __name__ == "__main__":

    program = [
        "   MOV AX, BX",
        "   NOP         ; Tohle je tu, aby to nic nedělalo",
        "navest ADD CX, DX"
    ]

    for line in program:
        print(convert_to_instructions(line))
