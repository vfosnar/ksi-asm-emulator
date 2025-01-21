from disassembler import *

def get_byteslength(instruction, args):
    # 3 možnosti:
    # - Immutable
    # - Register 
    # - Memmory
    #
    # Size:
    # byte/word/(none)
    # 
    # Taky potřebuju vědět:
    # Který opcode

    output = Instruction()


    output.operation = "MOV" # - TODO: extract from line
    output.size = 2  # Vyčíst z idk



    ...





def parse_param(p: str) -> 'Parameter': # Part of assembler
    """
    ! Work in progress. Yet can't handle labels nor math (MOV [label + 2], 42)
    ? Perhaps regex would be usefull??
    pls help
    """
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
        for r in MOD_00_RM:
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
    
    # Pointer
    if "PTR" in p:
        p.replace("PTR", "", 1) # Hope not
        p.replace("FAR", "", 1)
        return Label(p, include_segment=True)

    raise Exception(f"Nebylo možné zpracovat parametr {p}")
