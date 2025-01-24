PREFIXES = ["CS:", "DS:", "ES:", "SS:"]

INSTRUCTIONS_v2 = {
    # Wierd data set. But why??
    # Rozdělení do <instrukce><velikost> je hnusné, ale trochu to pomohlo zredukovat řádky.
    # Tuples (parameter, info) je nutný kvůli GRP instrukcím.
    # A navíc, kdo nemá rád špagety??
    "ADD8": [
        ("Eb Gb", {"opcode": 0}),
        ("Gb Eb", {"opcode": 2}),
        ("AL Ib", {"opcode": 4}),
        ("Eb Ib", {"opcode": 128, "modrm": 0}),
        ("Eb Ib", {"opcode": 130, "modrm": 0}),
        ("Ev Ib", {"opcode": 131, "modrm": 0}),
    ],
    "ADD16": [
        ("Ev Gv", {"opcode": 1}),
        ("Gv Ev", {"opcode": 3}),
        ("AX Iv", {"opcode": 5}),
        ("Ev Iv", {"opcode": 129, "modrm": 0}),
    ],
    "PUSH16": [
        ("ES", {"opcode": 6}),
        ("CS", {"opcode": 14}),
        ("SS", {"opcode": 22}),
        ("DS", {"opcode": 30}),
        ("AX", {"opcode": 80}),
        ("CX", {"opcode": 81}),
        ("DX", {"opcode": 82}),
        ("BX", {"opcode": 83}),
        ("SP", {"opcode": 84}),
        ("BP", {"opcode": 85}),
        ("SI", {"opcode": 86}),
        ("DI", {"opcode": 87}),
    ],
    "PUSH32": [("Mp", {"opcode": 255, "modrm": 48})],
    "POP16": [
        ("ES", {"opcode": 7}),
        ("SS", {"opcode": 23}),
        ("DS", {"opcode": 31}),
        ("AX", {"opcode": 88}),
        ("CX", {"opcode": 89}),
        ("DX", {"opcode": 90}),
        ("BX", {"opcode": 91}),
        ("SP", {"opcode": 92}),
        ("BP", {"opcode": 93}),
        ("SI", {"opcode": 94}),
        ("DI", {"opcode": 95}),
        ("Ev", {"opcode": 143}),
    ],
    "OR8": [
        ("Eb Gb", {"opcode": 8}),
        ("Gb Eb", {"opcode": 10}),
        ("AL Ib", {"opcode": 12}),
        ("Eb Ib", {"opcode": 128, "modrm": 8}),
        ("Eb Ib", {"opcode": 130, "modrm": 8}),
        ("Ev Ib", {"opcode": 131, "modrm": 8}),
    ],
    "OR16": [
        ("Ev Gv", {"opcode": 9}),
        ("Gv Ev", {"opcode": 11}),
        ("AX Iv", {"opcode": 13}),
        ("Ev Iv", {"opcode": 129, "modrm": 8}),
    ],
    "ADC8": [
        ("Eb Gb", {"opcode": 16}),
        ("Gb Eb", {"opcode": 18}),
        ("AL Ib", {"opcode": 20}),
        ("Eb Ib", {"opcode": 128, "modrm": 16}),
        ("Eb Ib", {"opcode": 130, "modrm": 16}),
        ("Ev Ib", {"opcode": 131, "modrm": 16}),
    ],
    "ADC16": [
        ("Ev Gv", {"opcode": 17}),
        ("Gv Ev", {"opcode": 19}),
        ("AX Iv", {"opcode": 21}),
        ("Ev Iv", {"opcode": 129, "modrm": 16}),
    ],
    "SBB8": [
        ("Eb Gb", {"opcode": 24}),
        ("Gb Eb", {"opcode": 26}),
        ("AL Ib", {"opcode": 28}),
        ("Eb Ib", {"opcode": 128, "modrm": 24}),
        ("Eb Ib", {"opcode": 130, "modrm": 24}),
        ("Ev Ib", {"opcode": 131, "modrm": 24}),
    ],
    "SBB16": [
        ("Ev Gv", {"opcode": 25}),
        ("Gv Ev", {"opcode": 27}),
        ("AX Iv", {"opcode": 29}),
        ("Ev Iv", {"opcode": 129, "modrm": 24}),
    ],
    "AND8": [
        ("Eb Gb", {"opcode": 32}),
        ("Gb Eb", {"opcode": 34}),
        ("AL Ib", {"opcode": 36}),
        ("Eb Ib", {"opcode": 128, "modrm": 32}),
        ("Eb Ib", {"opcode": 130, "modrm": 32}),
        ("Ev Ib", {"opcode": 131, "modrm": 32}),
    ],
    "AND16": [
        ("Ev Gv", {"opcode": 33}),
        ("Gv Ev", {"opcode": 35}),
        ("AX Iv", {"opcode": 37}),
        ("Ev Iv", {"opcode": 129, "modrm": 32}),
    ],
    "DAA0": [("", {"opcode": 39})],
    "SUB8": [
        ("Eb Gb", {"opcode": 40}),
        ("Gb Eb", {"opcode": 42}),
        ("AL Ib", {"opcode": 44}),
        ("Eb Ib", {"opcode": 128, "modrm": 40}),
        ("Eb Ib", {"opcode": 130, "modrm": 40}),
        ("Ev Ib", {"opcode": 131, "modrm": 40}),
    ],
    "SUB16": [
        ("Ev Gv", {"opcode": 41}),
        ("Gv Ev", {"opcode": 43}),
        ("AX Iv", {"opcode": 45}),
        ("Ev Iv", {"opcode": 129, "modrm": 40}),
    ],
    "DAS0": [("", {"opcode": 47})],
    "XOR8": [
        ("Eb Gb", {"opcode": 48}),
        ("Gb Eb", {"opcode": 50}),
        ("AL Ib", {"opcode": 52}),
        ("Eb Ib", {"opcode": 128, "modrm": 48}),
        ("Eb Ib", {"opcode": 130, "modrm": 48}),
        ("Ev Ib", {"opcode": 131, "modrm": 48}),
    ],
    "XOR16": [
        ("Ev Gv", {"opcode": 49}),
        ("Gv Ev", {"opcode": 51}),
        ("AX Iv", {"opcode": 53}),
        ("Ev Iv", {"opcode": 129, "modrm": 48}),
    ],
    "AAA0": [("", {"opcode": 55})],
    "CMP8": [
        ("Eb Gb", {"opcode": 56}),
        ("Gb Eb", {"opcode": 58}),
        ("AL Ib", {"opcode": 60}),
        ("Eb Ib", {"opcode": 128, "modrm": 56}),
        ("Eb Ib", {"opcode": 130, "modrm": 56}),
        ("Ev Ib", {"opcode": 131, "modrm": 56}),
    ],
    "CMP16": [
        ("Ev Gv", {"opcode": 57}),
        ("Gv Ev", {"opcode": 59}),
        ("AX Iv", {"opcode": 61}),
        ("Ev Iv", {"opcode": 129, "modrm": 56}),
    ],
    "AAS0": [("", {"opcode": 63})],
    "INC16": [
        ("AX", {"opcode": 64}),
        ("CX", {"opcode": 65}),
        ("DX", {"opcode": 66}),
        ("BX", {"opcode": 67}),
        ("SP", {"opcode": 68}),
        ("BP", {"opcode": 69}),
        ("SI", {"opcode": 70}),
        ("DI", {"opcode": 71}),
        ("Ev", {"opcode": 255, "modrm": 0}),
    ],
    "INC8": [("Eb", {"opcode": 254, "modrm": 0})],
    "DEC16": [
        ("AX", {"opcode": 72}),
        ("CX", {"opcode": 73}),
        ("DX", {"opcode": 74}),
        ("BX", {"opcode": 75}),
        ("SP", {"opcode": 76}),
        ("BP", {"opcode": 77}),
        ("SI", {"opcode": 78}),
        ("DI", {"opcode": 79}),
        ("Ev", {"opcode": 255, "modrm": 8}),
    ],
    "DEC8": [("Eb", {"opcode": 254, "modrm": 8})],
    "JO8": [("Jb", {"opcode": 112})],
    "JNO8": [("Jb", {"opcode": 113})],
    "JB8": [("Jb", {"opcode": 114})],
    "JNB8": [("Jb", {"opcode": 115})],
    "JZ8": [("Jb", {"opcode": 116})],
    "JNZ8": [("Jb", {"opcode": 117})],
    "JBE8": [("Jb", {"opcode": 118})],
    "JA8": [("Jb", {"opcode": 119})],
    "JS8": [("Jb", {"opcode": 120})],
    "JNS8": [("Jb", {"opcode": 121})],
    "JPE8": [("Jb", {"opcode": 122})],
    "JPO8": [("Jb", {"opcode": 123})],
    "JL8": [("Jb", {"opcode": 124})],
    "JGE8": [("Jb", {"opcode": 125})],
    "JLE8": [("Jb", {"opcode": 126})],
    "JG8": [("Jb", {"opcode": 127})],
    "TEST8": [
        ("Gb Eb", {"opcode": 132}),
        ("AL Ib", {"opcode": 168}),
        ("Eb Ib", {"opcode": 246, "modrm": 0}),
    ],
    "TEST16": [
        ("Gv Ev", {"opcode": 133}),
        ("AX Iv", {"opcode": 169}),
        ("Ev Iv", {"opcode": 247, "modrm": 0}),
    ],
    "XCHG8": [("Gb Eb", {"opcode": 134})],
    "XCHG16": [
        ("Gv Ev", {"opcode": 135}),
        ("CX AX", {"opcode": 145}),
        ("DX AX", {"opcode": 146}),
        ("BX AX", {"opcode": 147}),
        ("SP AX", {"opcode": 148}),
        ("BP AX", {"opcode": 149}),
        ("SI AX", {"opcode": 150}),
        ("DI AX", {"opcode": 151}),
    ],
    "MOV8": [
        ("Eb Gb", {"opcode": 136}),
        ("Gb Eb", {"opcode": 138}),
        ("AL Ob", {"opcode": 160}),
        ("Ob AL", {"opcode": 162}),
        ("AL Ib", {"opcode": 176}),
        ("CL Ib", {"opcode": 177}),
        ("DL Ib", {"opcode": 178}),
        ("BL Ib", {"opcode": 179}),
        ("AH Ib", {"opcode": 180}),
        ("CH Ib", {"opcode": 181}),
        ("DH Ib", {"opcode": 182}),
        ("BH Ib", {"opcode": 183}),
        ("Eb Ib", {"opcode": 198}),
    ],
    "MOV16": [
        ("Ev Gv", {"opcode": 137}),
        ("Gv Ev", {"opcode": 139}),
        ("Ew Sw", {"opcode": 140}),
        ("Sw Ew", {"opcode": 142}),
        ("AX Ov", {"opcode": 161}),
        ("Ov AX", {"opcode": 163}),
        ("AX Iv", {"opcode": 184}),
        ("CX Iv", {"opcode": 185}),
        ("DX Iv", {"opcode": 186}),
        ("BX Iv", {"opcode": 187}),
        ("SP Iv", {"opcode": 188}),
        ("BP Iv", {"opcode": 189}),
        ("SI Iv", {"opcode": 190}),
        ("DI Iv", {"opcode": 191}),
        ("Ev Iv", {"opcode": 199}),
    ],
    "LEA16": [("Gv M", {"opcode": 141})],
    "NOP0": [("", {"opcode": 144})],
    "CBW0": [("", {"opcode": 152})],
    "CWD0": [("", {"opcode": 153})],
    "CALL32": [("Ap", {"opcode": 154}), ("Mp", {"opcode": 255, "modrm": 24})],
    "CALL16": [("Jv", {"opcode": 232}), ("Ev", {"opcode": 255, "modrm": 16})],
    "WAIT0": [("", {"opcode": 155})],
    "PUSHF0": [("", {"opcode": 156})],
    "POPF0": [("", {"opcode": 157})],
    "SAHF0": [("", {"opcode": 158})],
    "LAHF0": [("", {"opcode": 159})],
    "MOVSB0": [("", {"opcode": 164})],
    "MOVSW0": [("", {"opcode": 165})],
    "CMPSB0": [("", {"opcode": 166})],
    "CMPSW0": [("", {"opcode": 167})],
    "STOSB0": [("", {"opcode": 170})],
    "STOSW0": [("", {"opcode": 171})],
    "LODSB0": [("", {"opcode": 172})],
    "LODSW0": [("", {"opcode": 173})],
    "SCASB0": [("", {"opcode": 174})],
    "SCASW0": [("", {"opcode": 175})],
    "RET16": [("Iw", {"opcode": 194})],
    "RET0": [("", {"opcode": 195})],
    "LES16": [("Gv Mp", {"opcode": 196})],
    "LDS16": [("Gv Mp", {"opcode": 197})],
    "RETF16": [("Iw", {"opcode": 202})],
    "RETF0": [("", {"opcode": 203})],
    "INT0": [("3", {"opcode": 204})],
    "INT8": [("Ib", {"opcode": 205})],
    "INTO0": [("", {"opcode": 206})],
    "IRET0": [("", {"opcode": 207})],
    "AAM0": [("I0", {"opcode": 212})],
    "AAD0": [("I0", {"opcode": 213})],
    "XLAT0": [("", {"opcode": 215})],
    "CO-PROCESSOR INSTRUCTIONS0": [("", {"opcode": 216})],
    "LOOPNZ8": [("Jb", {"opcode": 224})],
    "LOOPZ8": [("Jb", {"opcode": 225})],
    "LOOP8": [("Jb", {"opcode": 226})],
    "JCXZ8": [("Jb", {"opcode": 227})],
    "IN8": [
        ("AL Ib", {"opcode": 228}),
        ("AX Ib", {"opcode": 229}),
        ("AL DX", {"opcode": 236}),
    ],
    "IN16": [("AX DX", {"opcode": 237})],
    "OUT8": [("Ib AL", {"opcode": 230}), ("Ib AX", {"opcode": 231})],
    "OUT16": [("DX AL", {"opcode": 238}), ("DX AX", {"opcode": 239})],
    "JMP16": [("Jv", {"opcode": 233})],
    "JMP32": [
        ("Ap", {"opcode": 234}),
        ("Mp", {"opcode": 255, "modrm": 32}),
        ("Mp", {"opcode": 255, "modrm": 40}),
    ],
    "JMP8": [("Jb", {"opcode": 235})],
    "LOCK0": [("", {"opcode": 240})],
    "REPNZ0": [("", {"opcode": 242})],
    "REPZ0": [("", {"opcode": 243})],
    "HLT0": [("", {"opcode": 244})],
    "CMC0": [("", {"opcode": 245})],
    "CLC0": [("", {"opcode": 248})],
    "STC0": [("", {"opcode": 249})],
    "CLI0": [("", {"opcode": 250})],
    "STI0": [("", {"opcode": 251})],
    "CLD0": [("", {"opcode": 252})],
    "STD0": [("", {"opcode": 253})],
    "ROL8": [
        ("Eb 1", {"opcode": 208, "modrm": 0}),
        ("Eb CL", {"opcode": 208, "modrm": 0}),
    ],
    "ROL16": [
        ("Ev 1", {"opcode": 209, "modrm": 0}),
        ("Ev CL", {"opcode": 209, "modrm": 0}),
    ],
    "ROR8": [
        ("Eb 1", {"opcode": 208, "modrm": 8}),
        ("Eb CL", {"opcode": 208, "modrm": 8}),
    ],
    "ROR16": [
        ("Ev 1", {"opcode": 209, "modrm": 8}),
        ("Ev CL", {"opcode": 209, "modrm": 8}),
    ],
    "RCL8": [
        ("Eb 1", {"opcode": 208, "modrm": 16}),
        ("Eb CL", {"opcode": 208, "modrm": 16}),
    ],
    "RCL16": [
        ("Ev 1", {"opcode": 209, "modrm": 16}),
        ("Ev CL", {"opcode": 209, "modrm": 16}),
    ],
    "RCR8": [
        ("Eb 1", {"opcode": 208, "modrm": 24}),
        ("Eb CL", {"opcode": 208, "modrm": 24}),
    ],
    "RCR16": [
        ("Ev 1", {"opcode": 209, "modrm": 24}),
        ("Ev CL", {"opcode": 209, "modrm": 24}),
    ],
    "SHL8": [
        ("Eb 1", {"opcode": 208, "modrm": 32}),
        ("Eb CL", {"opcode": 208, "modrm": 32}),
    ],
    "SHL16": [
        ("Ev 1", {"opcode": 209, "modrm": 32}),
        ("Ev CL", {"opcode": 209, "modrm": 32}),
    ],
    "SHR8": [
        ("Eb 1", {"opcode": 208, "modrm": 40}),
        ("Eb CL", {"opcode": 208, "modrm": 40}),
    ],
    "SHR16": [
        ("Ev 1", {"opcode": 209, "modrm": 40}),
        ("Ev CL", {"opcode": 209, "modrm": 40}),
    ],
    "SAR8": [
        ("Eb 1", {"opcode": 208, "modrm": 56}),
        ("Eb CL", {"opcode": 208, "modrm": 56}),
    ],
    "SAR16": [
        ("Ev 1", {"opcode": 209, "modrm": 56}),
        ("Ev CL", {"opcode": 209, "modrm": 56}),
    ],
    "NOT8": [("Eb Ib", {"opcode": 246, "modrm": 16})],
    "NOT16": [("Ev Iv", {"opcode": 247, "modrm": 16})],
    "NEG8": [("Eb Ib", {"opcode": 246, "modrm": 24})],
    "NEG16": [("Ev Iv", {"opcode": 247, "modrm": 24})],
    "MUL8": [("Eb Ib", {"opcode": 246, "modrm": 32})],
    "MUL16": [("Ev Iv", {"opcode": 247, "modrm": 32})],
    "IMUL8": [("Eb Ib", {"opcode": 246, "modrm": 40})],
    "IMUL16": [("Ev Iv", {"opcode": 247, "modrm": 40})],
    "DIV8": [("Eb Ib", {"opcode": 246, "modrm": 48})],
    "DIV16": [("Ev Iv", {"opcode": 247, "modrm": 48})],
    "IDIV8": [("Eb Ib", {"opcode": 246, "modrm": 56})],
    "IDIV16": [("Ev Iv", {"opcode": 247, "modrm": 56})],
}

OPCODES = [
    # Parsed from http://www.mlsite.net/8086/#tbl_map1
    # 0x0_
    ('ADD', 'Eb Gb'), ('ADD', 'Ev Gv'), ('ADD', 'Gb Eb'), ('ADD',
                                                           'Gv Ev'), ('ADD', 'AL Ib'), ('ADD', 'AX Iv'), ('PUSH', 'ES'), ('POP', 'ES'),
    ('OR', 'Eb Gb'), ('OR', 'Ev Gv'), ('OR', 'Gb Eb'), ('OR',
                                                        'Gv Ev'), ('OR', 'AL Ib'), ('OR', 'AX Iv'), ('PUSH', 'CS'), ('', ''),

    # 0x1_
    ('ADC', 'Eb Gb'), ('ADC', 'Ev Gv'), ('ADC', 'Gb Eb'), ('ADC',
                                                           'Gv Ev'), ('ADC', 'AL Ib'), ('ADC', 'AX Iv'), ('PUSH', 'SS'), ('POP', 'SS'),
    ('SBB', 'Eb Gb'), ('SBB', 'Ev Gv'), ('SBB', 'Gb Eb'), ('SBB',
                                                           'Gv Ev'), ('SBB', 'AL Ib'), ('SBB', 'AX Iv'), ('PUSH', 'DS'), ('POP', 'DS'),

    # 0x2_
    ('AND', 'Eb Gb'), ('AND', 'Ev Gv'), ('AND', 'Gb Eb'), ('AND',
                                                           'Gv Ev'), ('AND', 'AL Ib'), ('AND', 'AX Iv'), ('ES:', 'prefix'), ('DAA', ''),
    ('SUB', 'Eb Gb'), ('SUB', 'Ev Gv'), ('SUB', 'Gb Eb'), ('SUB',
                                                           'Gv Ev'), ('SUB', 'AL Ib'), ('SUB', 'AX Iv'), ('CS:', 'prefix'), ('DAS', ''),

    # 0x3_
    ('XOR', 'Eb Gb'), ('XOR', 'Ev Gv'), ('XOR', 'Gb Eb'), ('XOR',
                                                           'Gv Ev'), ('XOR', 'AL Ib'), ('XOR', 'AX Iv'), ('SS:', 'prefix'), ('AAA', ''),
    ('CMP', 'Eb Gb'), ('CMP', 'Ev Gv'), ('CMP', 'Gb Eb'), ('CMP',
                                                           'Gv Ev'), ('CMP', 'AL Ib'), ('CMP', 'AX Iv'), ('DS:', 'prefix'), ('AAS', ''),

    # 0x4_
    ('INC', 'AX'), ('INC', 'CX'), ('INC', 'DX'), ('INC',
                                                  'BX'), ('INC', 'SP'), ('INC', 'BP'), ('INC', 'SI'), ('INC', 'DI'),
    ('DEC', 'AX'), ('DEC', 'CX'), ('DEC', 'DX'), ('DEC',
                                                  'BX'), ('DEC', 'SP'), ('DEC', 'BP'), ('DEC', 'SI'), ('DEC', 'DI'),

    # 0x5_
    ('PUSH', 'AX'), ('PUSH', 'CX'), ('PUSH', 'DX'), ('PUSH',
                                                     'BX'), ('PUSH', 'SP'), ('PUSH', 'BP'), ('PUSH', 'SI'), ('PUSH', 'DI'),
    ('POP', 'AX'), ('POP', 'CX'), ('POP', 'DX'), ('POP',
                                                  'BX'), ('POP', 'SP'), ('POP', 'BP'), ('POP', 'SI'), ('POP', 'DI'),

    # 0x6_  Not relevant for KSI emulator
    ('--', ''), ('--', ''), ('--', ''), ('--',
                                         ''), ('--', ''), ('--', ''), ('--', ''), ('--', ''),
    ('--', ''), ('--', ''), ('--', ''), ('--',
                                         ''), ('--', ''), ('--', ''), ('--', ''), ('--', ''),

    # 0x7_
    ('JO', 'Jb'), ('JNO', 'Jb'), ('JB', 'Jb'), ('JNB', 'Jb'), ('JZ',
                                                               'Jb'), ('JNZ', 'Jb'), ('JBE', 'Jb'), ('JA', 'Jb'),
    ('JS', 'Jb'), ('JNS', 'Jb'), ('JPE', 'Jb'), ('JPO',
                                                 'Jb'), ('JL', 'Jb'), ('JGE', 'Jb'), ('JLE', 'Jb'), ('JG', 'Jb'),

    # 0x8_
    ('GRP1', 'Eb Ib'), ('GRP1', 'Ev Iv'), ('GRP1', 'Eb Ib'), ('GRP1', 'Ev Ib'), ('TEST',
                                                                                 'Gb Eb'), ('TEST', 'Gv Ev'), ('XCHG', 'Gb Eb'), ('XCHG', 'Gv Ev'),
    ('MOV', 'Eb Gb'), ('MOV', 'Ev Gv'), ('MOV', 'Gb Eb'), ('MOV',
                                                           'Gv Ev'), ('MOV', 'Ew Sw'), ('LEA', 'Gv M'), ('MOV', 'Sw Ew'), ('POP', 'Ev'),

    # 0x9_
    ('NOP', ''), ('XCHG', 'CX AX'), ('XCHG', 'DX AX'), ('XCHG', 'BX AX'), ('XCHG',
                                                                           'SP AX'), ('XCHG', 'BP AX'), ('XCHG', 'SI AX'), ('XCHG', 'DI AX'),
    ('CBW', ''), ('CWD', ''), ('CALL', 'Ap'), ('WAIT',
                                               ''), ('PUSHF', ''), ('POPF', ''), ('SAHF', ''), ('LAHF', ''),

    # 0xA_
    ('MOV', 'AL Ob'), ('MOV', 'AX Ov'), ('MOV', 'Ob AL'), ('MOV',
                                                           'Ov AX'), ('MOVSB', ''), ('MOVSW', ''), ('CMPSB', ''), ('CMPSW', ''),
    ('TEST', 'AL Ib'), ('TEST', 'AX Iv'), ('STOSB', ''), ('STOSW',
                                                          ''), ('LODSB', ''), ('LODSW', ''), ('SCASB', ''), ('SCASW', ''),

    # 0xB_
    ('MOV', 'AL Ib'), ('MOV', 'CL Ib'), ('MOV', 'DL Ib'), ('MOV', 'BL Ib'), ('MOV',
                                                                             'AH Ib'), ('MOV', 'CH Ib'), ('MOV', 'DH Ib'), ('MOV', 'BH Ib'),
    ('MOV', 'AX Iv'), ('MOV', 'CX Iv'), ('MOV', 'DX Iv'), ('MOV', 'BX Iv'), ('MOV',
                                                                             'SP Iv'), ('MOV', 'BP Iv'), ('MOV', 'SI Iv'), ('MOV', 'DI Iv'),

    # 0xC_
    ('', ''), ('', ''), ('RET', 'Iw'), ('RET', ''), ('LES',
                                                     'Gv Mp'), ('LDS', 'Gv Mp'), ('MOV', 'Eb Ib'), ('MOV', 'Ev Iv'),
    ('', ''), ('', ''), ('RETF', 'Iw'), ('RETF', ''), ('INT',
                                                       '3'), ('INT', 'Ib'), ('INTO', ''), ('IRET', ''),

    # 0xD_
    ('GRP2', 'Eb 1'), ('GRP2', 'Ev 1'), ('GRP2', 'Eb CL'), ('GRP2',
                                                            'Ev CL'), ('AAM', 'I0'), ('AAD', 'I0'), ('', ''), ('XLAT', ''),
    ('CO-PROCESSOR INSTRUCTIONS', ''), ('--', ''), ('--',
                                                    ''), ('--', ''), ('--', ''), ('--', ''), ('--', ''), ('--', ''),

    # 0xE_
    ('LOOPNZ', 'Jb'), ('LOOPZ', 'Jb'), ('LOOP', 'Jb'), ('JCXZ', 'Jb'), ('IN',
                                                                        'AL Ib'), ('IN', 'AX Ib'), ('OUT', 'Ib AL'), ('OUT', 'Ib AX'),
    ('CALL', 'Jv'), ('JMP', 'Jv'), ('JMP', 'Ap'), ('JMP', 'Jb'), ('IN',
                                                                  'AL DX'), ('IN', 'AX DX'), ('OUT', 'DX AL'), ('OUT', 'DX AX'),

    # 0xF_
    ('LOCK', ''), ('', ''), ('REPNZ', ''), ('REPZ', ''), ('HLT',
                                                          ''), ('CMC', ''), ('GRP3a', 'Eb'), ('GRP3b', 'Ev'),
    ('CLC', ''), ('STC', ''), ('CLI', ''), ('STI', ''), ('CLD',
                                                         ''), ('STD', ''), ('GRP4', 'Eb'), ('GRP5', 'Ev'),
]

RM_8_REGS = ["AL", "CL", "DL", "BL", "AH", "CH", "DH", "BH"]
RM_16_REGS = ["AX", "CX", "DX", "BX", "SP", "BP", "SI", "DI"]

SEG_REGS = ["ES", "CS", "SS", "DS", "FS", "GS"]

# !! If mod=00, Místo BP je pouze displacement16!!
MOD_00_RM = ["BX+SI", "BX+DI", "BP+SI", "BP+DI", "SI", "DI", "BP", "BX"]

REGISTERS = set(RM_8_REGS + RM_16_REGS + SEG_REGS)


GRPs = {
    "GRP1": [('ADD', ''), ('OR', ''), ('ADC', ''), ('SBB', ''), ('AND', ''), ('SUB', ''), ('XOR', ''), ('CMP', '')],
    "GRP2": [('ROL', ''), ('ROR', ''), ('RCL', ''), ('RCR', ''), ('SHL', ''), ('SHR', ''), ('--', ''), ('SAR', '')],
    "GRP3a": [('TEST', 'Eb Ib'), ('--', ''), ('NOT', ''), ('NEG', ''), ('MUL', ''), ('IMUL', ''), ('DIV', ''), ('IDIV', '')],
    "GRP3b": [('TEST', 'Ev Iv'), ('--', ''), ('NOT', ''), ('NEG', ''), ('MUL', ''), ('IMUL', ''), ('DIV', ''), ('IDIV', '')],
    "GRP4": [('INC', ''), ('DEC', ''), ('--', ''), ('--', ''), ('--', ''), ('--', ''), ('--', ''), ('--', '')],
    "GRP5": [('INC', ''), ('DEC', ''), ('CALL', ''), ('CALL', 'Mp'), ('JMP', ''), ('JMP', 'Mp'), ('PUSH', ''), ('--', '')]
}
