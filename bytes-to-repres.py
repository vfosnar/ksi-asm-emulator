
prefixes = {
    0x2E: "CS",
    0x3E: "DS",
    0x26: "ES",
    0x36: "SS",
    # Samozřejmě existuje spousta dalších prefixů s různou funkcionalitou,
    # nám ale budou stačit tyto, které blíže specifikují registr
}


OPCODES = {
    # MOV pouze symbolicky, kontroluje se uvnitř inicializátoru
    # třídy <instruction>
    # "B0-B1": "MOV reg, imm8",
    # "B8-BF": "MOV reg, imm16",
    # "89": "MOV reg/mem, reg",
    # "8B": "MOV reg, reg/mem",

    # Co tu není:
    # - ADCm ADDm


    "01": "ADD reg/mem, reg",
    "03": "ADD reg, reg/mem",

    0x90: "NOP"
    # Příkazů existuje více
}

HAS_MODRM = {

}


class Instrucion:
    def __init__(self, opcode: int):
        self.opcode = opcode
        self.type = OPCODES[]
        self.containsModRM = "idk"
        pass

    # Static??
    def byte_to_instruction(optcode: int):

        ...


def next_instruction(segment, IP):
    span = 0
    byte = segment[IP + span]  # Předpokládá se, že validní

    prefix = None
    if byte in prefixes:
        prefix = prefixes[byte]
        span += 1
        byte = segment[IP + span]

    instrucion = Instrucion(byte)

    if instrucion.containsModRM:
