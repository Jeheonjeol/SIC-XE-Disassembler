class Symbol:
    def __init__(self, label, loc, flag, dType = None):
        self.label = label
        self.loc   = loc
        self.flag  = flag    # Resolved, Unresolved
        self.dType = dType   # BYTE, WORD, RESB, RESW

def ReadSymbols(SYM_DIR):
 
    symbols = dict()

    f = open(SYM_DIR, 'r')
    for line in f.readlines():
        temp = line.replace('\n', '').split('\t')

        dType = len(temp) >= 4 and temp[3] or None
        sym = Symbol(temp[0], int(temp[1], 16), temp[2], dType)
        symbols[sym.loc] = sym

    f.close()

    return symbols