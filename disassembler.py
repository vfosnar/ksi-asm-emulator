from data import *
from converting_functions import *


def parse_next_instruction(program, address) -> tuple['Instruction', int]:
    """Just in time dissasembler"""
    instruction = Instruction()
    span = 0

    def load_next():
        nonlocal span
        byte = program[address + span]
        assert byte is not None, "Načítáte nedefinovaný bit jako instrukci. Nezapoměli jste HLT??"
        span += 1
        instruction.bytes.append(byte)
        return byte

    byte = load_next()
    operation, properties = OPCODES[byte]

    if "prefix" in properties:
        instruction.prefix = operation

        byte = load_next()
        operation, properties = OPCODES[byte]

    instruction.operation = operation

    # Handle GRP instructions
    if instruction.operation in GRPs:
        instruction.modrm = ModRM(load_next(), properties[1] == "b", load_next)
        instruction.operation, sp_properties = GRPs[instruction.operation][instruction.modrm.reg_val]

        if sp_properties != "":
            properties = sp_properties

    # Size of operation for better DevEx
    instruction.size = 0
    if "b" in properties:
        instruction.size = 8
    elif "w" in properties or "v" in properties:
        instruction.size = 16

    for arg in properties.split():
        # Codes that don't need ModRM byte:
        # (Do not wory, it would read ModR/M. Codes are structured, so that this wouldn't happen)
        if arg in REGISTERS:
            instruction.arguments.append(Register(arg))
            continue

        if "1" in arg:
            instruction.arguments.append(Immutable(1))
            continue
        if "3" in arg:
            instruction.arguments.append(Immutable(3))
            continue

        if arg[0] == "O":
            byte = load_next() + load_next() * 2**8
            instruction.arguments.append(byte)
            continue

        if arg[0] == "I":
            byte = load_next()
            if arg[1] != "b":
                byte = byte + load_next() * 2**8

            instruction.arguments.append(Immutable(byte))
            continue

        if arg[0] == "J":
            val = load_next()
            if instruction.size == 16:
                val += load_next() * 2**8

            val = from_twos_complement(val, instruction.size)

            instruction.arguments.append(Immutable(val))
                
            continue

        if arg[0] == "A":
            offset = load_next() + load_next() * 2**8
            segment = load_next() + load_next() * 2**8
            instruction.arguments.append(Pointer(segment, offset))
            continue

        # From here, all instructions do need ModR/M
        if instruction.modrm is None:
            instruction.modrm = ModRM(load_next(), arg[1] == "b", load_next)

        match arg[0]:
            case "G":
                instruction.arguments.append(instruction.modrm.reg)
            case "E":
                rm = instruction.modrm.rm
                if isinstance(rm, Memmory) and instruction.prefix is not None:
                    # To remove ":" from for ex. "ES:"
                    rm.segment = instruction.prefix[:-1]
                instruction.arguments.append(rm)
            case "S":
                instruction.arguments.append(
                    Register(SEG_REGS[instruction.modrm.reg_val])
                )
            case "M":
                raise NotImplementedError(
                    "Not relevant for KSI emulator.")  # TODO: better hláška
            case _:
                raise Exception("Unrecognised instruction property")

    return instruction, span


class Instruction:
    def __init__(self):
        self.operation: str = None
        self.prefix: None | str = None  # None | "DS" | "CS" | ...
        self.arguments: list[Parameter] = []

        self.size = 0   # 0 for RET; 1 for MOV AL, AH; 2 for MOV AX, BX

        self.bytes = []  # Aspoň aby tu něco bylo
        self.modrm: ModRM | None = None


class ModRM:
    def __init__(self, byte, is_8b: bool, load_byte):
        self.byte = byte

        self.mod: int = byte // 64
        self.reg_val: int = (byte // 8) % 8
        self.rm_val: int = byte % 8

        # so that there couldn't be None - TODO: rewrite
        self.rm: Memmory | Register = Register("Dummy")

        # Reg
        regs = RM_8_REGS if is_8b else RM_16_REGS
        self.reg: Register = Register(regs[self.reg_val])

        # R/M
        if self.mod == 3:
            self.rm = Register(regs[self.rm_val])
        else:
            if self.mod == 0 and self.rm_val == 6:
                displ = load_byte() + load_byte() * 2**8
                self.rm = Memmory(None, displ)
            else:
                displ = 0
                if self.mod >= 1:
                    displ = load_byte()

                if self.mod == 2:
                    displ = displ + load_byte() * 2**8

                self.rm = Memmory(MOD_00_RM[self.rm_val], displ)


class Register:
    def __init__(self, name):
        self.name: str = name
        self.size: int = 8 if name[1] in ['L', 'H'] else 16


class Immutable:
    def __init__(self, value):
        self.value = value


class Pointer:
    def __init__(self, segment: int, offset: int):
        self.segment = segment
        self.offset = offset


class Memmory:
    def __init__(self, source: str | None, displacement: int, segment="DS"):
        self.displacement: int = displacement
        self.segment = segment

        # Is None when mod=00 and rm=110
        self.source: str = source if source is not None else ""


Parameter = Register | Immutable | Memmory | Pointer


if __name__ == "__main__":
    x = parse_next_instruction([
        0x38,  # CMP BL, DH
        0xF3,
    ], 0)

    x = parse_next_instruction([
        0x80,
        0xFB,
        0x06,
    ], 0)

    x = parse_next_instruction([
        0xFE,
        0xC0,
        0x23,
        0x01,
        0x07,
    ], 0)

    x = parse_next_instruction([
        0xF7,
        0xD8,
    ], 0)

    x = parse_next_instruction([
        0x70, 0x03  # JO +3
    ], 0)

    print(x)

    # p = parse_param("AX")
    # p = parse_param("25")
    # p = parse_param("11b")
    # p = parse_param("[BX+SI+24h]")
    # p = parse_param("[n]")

    # print(p)


"""
DISASSEMBLER
- Zpracování pointerů


EMULÁTOR
- udělat vzorové řešení (dopsat předpřipravené funkce)
- otestovat
+ napsat testy na úlohy
"""
