





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
            self.rm = x[self.rm_val]
        
        else:
            self.rm = Mod00_RM[self.rm_val] + RM_ext[self.mod]

            


        

RM_reg_r8 = ["AL", "CL", "DL", "BL", "AH", "CH", "DH", "BH"]
RM_r16 = ["AX", "CX", "DX", "BX", "SP", "BP", "SI", "DI"]
RM_regs_myoff = RM_reg_r8 + RM_r16

Mod00_RM = ["[BX+SI]","[BX+DI]","[BP+SI]","[BP+DI]", "[SI]", "[DI]", "disp16", "[BX]"]
RM_ext = ["", "+disp8", "+disp16"]


if __name__ == "__main__":
    print("aaaaaaa")

    x = ModRM(0b10111101, True)
    print(x.reg)
    print(x.rm)

    

