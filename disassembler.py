


def parse_param(p: str) -> 'Parameter': # Part of assembler
    # Register
    if p in REGISTERS:
        return Register(p)
    
    # Immutable
    try:
        print(parse_number(p))
        return Immutable(parse_number(p))
    except:
        pass

    # Memmory
    if p[0] == '[' and p[-1] == "]":
        p = p[1:-1]
        a = Memmory(None, None)
        for r in Mod00_RM:
            if r in p:
                a.source = r
                p = p.replace(r + '+', "+")
                break
        else:
            raise Exception("Nebyl rozpoznán segment")
        
        if p[0] == "+":
            p = p.replace('+', '')
            a.displacement = parse_number(p) # If is not ok, it's the users problem.
        
        return a

    if "PTR" in p:
        p.replace("PTR", "", 1) # Hope not
        p.replace("FAR", "", 1)
        return Label(p, include_segment=True)

    # Pointer
    # TODO: Add

    raise Exception(f"Nebylo možné zpracovat parametr {p}")
    ...

def parse_number(s: str) -> int:
    if s[-1] == "h":
        return int(s[:-1], 16)
    elif s[-1] == "b":
        return int(s[:-1], 2)
    return int(s)


def zpracuj_dalsi_instrukci(segment, IP): # Disassembler
    instruction = Instruction()
    span = 0

    def load_next():
        nonlocal span
        byte = segment[IP + span]
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
    if properties == '-': return instruction


    for arg in properties.split():
        if arg in REGISTERS:
            instruction.arguments.append(Register(arg))
            continue

        if arg[0] == "O": # Doesn't have modrm nor any other argument (trust me, i checked.)
            # Little endian
            byte += load_next() + load_next()* 2**8
            instruction.arguments.append(byte)
            continue

        if arg[0] == "A":
            raise NotImplementedError("TODO: dodělat")
                
        # From here to bottom, all instructions have ModR/M
        if instruction.modrm is None:
            instruction.modrm = ModRM(load_next(), arg[1] == "b")

        if arg[0] == "G":
            instruction.arguments.append(Register(instruction.modrm.reg))
        
        if arg[0] == "I":
            # This is always second argument, so no problem with the ModRM
            byte = load_next()
            if arg[1] != "b":            
                byte = byte + load_next() * 2**8 

            instruction.arguments.append(Immutable(byte))

        if arg[0] == "E":
            # Problem TODO: Fucking solve this bitch
            instruction.arguments.append(instruction.modrm.rm)

        if arg[0] == "S":
            instruction.arguments.append(
                Register(segments_idk[instruction.modrm.reg_val])
            )

        if arg[0] == "M":
            raise NotImplementedError("Tuhle instrukci nevedeme.")

    # 1) Načíst byte.
    #    - Pokud je prefix, načti další a pamatuj si ho
    # 2) Zpracuj opcode - dešifruj, k čemu patří
    # 3) Zpracuj ModR/M, pokud ho potřebuju
    # 4) Pokud potřebuji další data, tak si je načtu (poznám podle R/M bitů)¨
    # Mám to ;-)

    # Zpracování ModR/M
    # 1. Načtu ModR/M
    # 2. Zjistím Mod
    #   case 00: Nic dalšího  
    #   case 01: Načti další byte (displacement)
    #   case 10: Načti další slovo (displacement)
    #   case 11: Bude to z registru do registru

    ...



RM_reg_r8 = ["AL", "CL", "DL", "BL", "AH", "CH", "DH", "BH"]
RM_r16 = ["AX", "CX", "DX", "BX", "SP", "BP", "SI", "DI"]
RM_regs_myoff = RM_reg_r8 + RM_r16

segments_idk = ["ES", "CS", "SS", "DS", "FS", "GS"]

Mod00_RM = ["BX+SI","BX+DI","BP+SI","BP+DI", "SI", "DI", "BP", "BX"] # !! If mod=00, Místo BP je pouze displacement16!!
RM_ext = ["", "+disp8", "+disp16"]

REGISTERS = {
    "AL", "BL", "CL", "DL", "AH", "BH", "CH", "DH", "AX", "BX", "CX", "DX", "SI", 
    "DI", "ES", "SS", "CS", "DS"
}

OPCODES = [
    # 0x0_
    ('ADD', 'Eb Gb'), ('ADD', 'Ev Gv'), ('ADD', 'Gb Eb'), ('ADD', 'Gv Ev'), ('ADD', 'AL Ib'), ('ADD', 'AX Iv'), ('PUSH', 'ES'), ('POP', 'ES'),
    ('OR', 'Eb Gb'), ('OR', 'Ev Gv'), ('OR', 'Gb Eb'), ('OR', 'Gv Ev'), ('OR', 'AL Ib'), ('OR', 'AX Iv'), ('PUSH', 'CS'), ('-', '-'),
    
    # 0x1_
    ('ADC', 'Eb Gb'), ('ADC', 'Ev Gv'), ('ADC', 'Gb Eb'), ('ADC', 'Gv Ev'), ('ADC', 'AL Ib'), ('ADC', 'AX Iv'), ('PUSH', 'SS'), ('POP', 'SS'),
    ('SBB', 'Eb Gb'), ('SBB', 'Ev Gv'), ('SBB', 'Gb Eb'), ('SBB', 'Gv Ev'), ('SBB', 'AL Ib'), ('SBB', 'AX Iv'), ('PUSH', 'DS'), ('POP', 'DS'),
    
    # 0x2_
    ('AND', 'Eb Gb'), ('AND', 'Ev Gv'), ('AND', 'Gb Eb'), ('AND', 'Gv Ev'), ('AND', 'AL Ib'), ('AND', 'AX Iv'), ('ES:', 'prefix'), ('DAA', ''),
    ('SUB', 'Eb Gb'), ('SUB', 'Ev Gv'), ('SUB', 'Gb Eb'), ('SUB', 'Gv Ev'), ('SUB', 'AL Ib'), ('SUB', 'AX Iv'), ('CS:', 'prefix'), ('DAS', '-'),
   
    # 0x3_
    ('XOR', 'Eb Gb'), ('XOR', 'Ev Gv'), ('XOR', 'Gb Eb'), ('XOR', 'Gv Ev'), ('XOR', 'AL Ib'), ('XOR', 'AX Iv'), ('SS:', 'prefix'), ('AAA', ''),
    ('CMP', 'Eb Gb'), ('CMP', 'Ev Gv'), ('CMP', 'Gb Eb'), ('CMP', 'Gv Ev'), ('CMP', 'AL Ib'), ('CMP', 'AX Iv'), ('DS:', 'prefix'), ('AAS', '-'),

    # 0x4_
    ('INC', 'AX'), ('INC', 'CX'), ('INC', 'DX'), ('INC', 'BX'), ('INC', 'SP'), ('INC', 'BP'), ('INC', 'SI'), ('INC', 'DI'),
    ('DEC', 'AX'), ('DEC', 'CX'), ('DEC', 'DX'), ('DEC', 'BX'), ('DEC', 'SP'), ('DEC', 'BP'), ('DEC', 'SI'), ('DEC', 'DI'),

    # 0x5_
    ('PUSH', 'AX'), ('PUSH', 'CX'), ('PUSH', 'DX'), ('PUSH', 'BX'), ('PUSH', 'SP'), ('PUSH', 'BP'), ('PUSH', 'SI'), ('PUSH', 'DI'),
    ('POP', 'AX'), ('POP', 'CX'), ('POP', 'DX'), ('POP', 'BX'), ('POP', 'SP'), ('POP', 'BP'), ('POP', 'SI'), ('POP', 'DI'),

    # 0x6_
    ('PRAZDNE NEBO TAK NECO', '-'), ('--', '-'), ('--', '-'), ('--', '-'), ('--', '-'), ('--', '-'), ('--', '-'), ('--', '-'),
    ('--', '-'), ('--', '-'), ('--', '-'), ('--', '-'), ('--', '-'), ('--', '-'), ('--', '-'), ('--', '-'),

    # 0x7_
    ('JO', 'Jb'), ('JNO', 'Jb'), ('JB', 'Jb'), ('JNB', 'Jb'), ('JZ', 'Jb'), ('JNZ', 'Jb'), ('JBE', 'Jb'), ('JA', 'Jb'),
    ('JS', 'Jb'), ('JNS', 'Jb'), ('JPE', 'Jb'), ('JPO', 'Jb'), ('JL', 'Jb'), ('JGE', 'Jb'), ('JLE', 'Jb'), ('JG', 'Jb'),

    # 0x8_
    ('GRP1', 'Eb Ib'), ('GRP1', 'Ev Iv'), ('GRP1', 'Eb Ib'), ('GRP1', 'Ev Ib'), ('TEST', 'Gb Eb'), ('TEST', 'Gv Ev'), ('XCHG', 'Gb Eb'), ('XCHG', 'Gv Ev'),
    ('MOV', 'Eb Gb'), ('MOV', 'Ev Gv'), ('MOV', 'Gb Eb'), ('MOV', 'Gv Ev'), ('MOV', 'Ew Sw'), ('LEA', 'Gv M'), ('MOV', 'Sw Ew'), ('POP', 'Ev'),

    # 0x9_
    ('NOP', '-'), ('XCHG', 'CX AX'), ('XCHG', 'DX AX'), ('XCHG', 'BX AX'), ('XCHG', 'SP AX'), ('XCHG', 'BP AX'), ('XCHG', 'SI AX'), ('XCHG', 'DI AX'),
    ('CBW', '-'), ('CWD', '-'), ('CALL', 'Ap'), ('WAIT', '-'), ('PUSHF', '-'), ('POPF', '-'), ('SAHF', '-'), ('LAHF', '-'),

    # 0xA_
    ('MOV', 'AL Ob'), ('MOV', 'AX Ov'), ('MOV', 'Ob AL'), ('MOV', 'Ov AX'), ('MOVSB', '-'), ('MOVSW', '-'), ('CMPSB', '-'), ('CMPSW', '-'),
    ('TEST', 'AL Ib'), ('TEST', 'AX Iv'), ('STOSB', '-'), ('STOSW', '-'), ('LODSB', '-'), ('LODSW', '-'), ('SCASB', '-'), ('SCASW', '-'),

    # 0xB_
    ('MOV', 'AL Ib'), ('MOV', 'CL Ib'), ('MOV', 'DL Ib'), ('MOV', 'BL Ib'), ('MOV', 'AH Ib'), ('MOV', 'CH Ib'), ('MOV', 'DH Ib'), ('MOV', 'BH Ib'),
    ('MOV', 'AX Iv'), ('MOV', 'CX Iv'), ('MOV', 'DX Iv'), ('MOV', 'BX Iv'), ('MOV', 'SP Iv'), ('MOV', 'BP Iv'), ('MOV', 'SI Iv'), ('MOV', 'DI Iv'),

    # 0xC_
    ('-', '-'), ('-', '-'), ('RET', 'Iw'), ('RET', '-'), ('LES', 'Gv Mp'), ('LDS', 'Gv Mp'), ('MOV', 'Eb Ib'), ('MOV', 'Ev Iv'),
    ('-', '-'), ('-', '-'), ('RETF', 'Iw'), ('RETF', '-'), ('INT', '3'), ('INT', 'Ib'), ('INTO', '-'), ('IRET', '-'),

    # 0xD_
    ('GRP2', 'Eb 1'), ('GRP2', 'Ev 1'), ('GRP2', 'Eb CL'), ('GRP2', 'Ev CL'), ('AAM', 'I0'), ('AAD', 'I0'), ('-', '-'), ('XLAT', '-'),
    ('--', 'co-processor'), ('--', '-'), ('--', '-'), ('--', '-'), ('--', '-'), ('--', '-'), ('--', '-'), ('--', '-'),

    # 0xE_
    ('LOOPNZ', 'Jb'), ('LOOPZ', 'Jb'), ('LOOP', 'Jb'), ('JCXZ', 'Jb'), ('IN', 'AL Ib'), ('IN', 'AX Ib'), ('OUT', 'Ib AL'), ('OUT', 'Ib AX'),
    ('CALL', 'Jv'), ('JMP', 'Jv'), ('JMP', 'Ap'), ('JMP', 'Jb'), ('IN', 'AL DX'), ('IN', 'AX DX'), ('OUT', 'DX AL'), ('OUT', 'DX AX'),

    # 0xF_
    ('LOCK', '-'), ('-', '-'), ('REPNZ', '-'), ('REPZ', '-'), ('HLT', '-'), ('CMC', '-'), ('GRP3a', 'Eb'), ('GRP3b', 'Ev'),
    ('CLC', '-'), ('STC', '-'), ('CLI', '-'), ('STI', '-'), ('CLD', '-'), ('STD', '-'), ('GRP4', 'Eb'), ('GRP5', 'Ev'),

]


class Instruction:
    def __init__(self):
        self.operation: str = "MOV" # Dummy data - TODO: remove
        self.prefix: None | str = None  # None | "DS" | "CS" | ...
        self.arguments: list[Parameter] = [] 

        self.bytes = []  # Aspoň aby tu něco bylo 
        self.modrm: ModRM | None = None


class Register:
    def __init__(self, name):
        self.name = name
        self.size = 8 if name[1] in ['L', 'H'] else 16

class ModRM:
    def __init__(self, byte, is_8b: bool):
        self.byte = byte

        self.mod = byte // 64
        self.reg_val = (byte // 8) % 8
        self.rm_val = byte % 8
        
        self.reg = None
        self.rm = None

        # reg
        x = RM_reg_r8 if is_8b else RM_r16

        self.reg = x[self.reg_val]

        if self.mod == 3:
            self.rm = Register(x[self.rm_val])
        
        else:
            self.rm = Mod00_RM[self.rm_val] + RM_ext[self.mod]


class Immutable:
    def __init__(self, value):
        self.value = value

class Pointer:
    def __init__(self, segment: int, offset: int):
        self.segment = segment
        self.offset = offset

class Memmory:
    def __init__(self, displacement, source: str | None, segment="DS"):
        self.displacement = displacement
        self.segment = segment

        # Is none when mod=00 and rm=110
        self.source: str | None = source

class Label:
    def __init__(self, label: str, displacement: int = 0, include_segment = False):
        self.label = label
        # TODO: Get in the f*cking damn ship, everything is a label - Rick s02e10
        self.displacement: int = displacement
        self.include_segment = include_segment

Parameter = Register | Immutable | Memmory | Pointer
ParameterOrLabel = Parameter | Label



if __name__ == "__main__":
    p = parse_param("AX")
    p = parse_param("25")
    p = parse_param("11b")
    p = parse_param("[BX+SI+24h]")
    p = parse_param("[n]")

    print(p)