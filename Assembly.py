
class AssemblyLine:
    def __init__(self, loc, label = None, mnemonic = None, operand = None, objCode = None):
        self.loc = loc
        self.label = label
        self.mnemonic = mnemonic
        self.operand = operand
        self.objCode = objCode

        self.indirectFlag = False
        self.immediateFlag = False
        self.extendedFlag = False
        self.indexAddrFlag = False

class AssemblyDict(dict):
    def __init__(self, header, end):
        dict.__init__(self)
        self.header = header
        self.end = end


    def writeAssemblyFile(self, ASM_DIR):
        f = open(ASM_DIR, 'w+')
        f.write('Loc\t\t\t\tSource statement\t\t\tObject code\n')
        f.write(self.makeString(self.header))

        keys = list(self.keys())
        keys.sort()
        for key in keys:
            asm = self[key]
            f.write(self.makeString(asm))
            if asm.mnemonic == 'LDB':   # BASE directive
                f.write(self.makeString(AssemblyLine(None, mnemonic='BASE', operand=asm.operand)))

        f.write(self.makeString(self.end))
        f.close()


    def makeString(self, asm):
        sSpace = ' ' * 4
        lspace = ' ' * 8

        ni = asm.indirectFlag  and '@'  or asm.immediateFlag and '#' or ' '
        e  = asm.extendedFlag  and '+'  or ' '
        x  = asm.indexAddrFlag and ',X' or ''

        loc      = asm.loc      != None and '%04X' % asm.loc                     or sSpace
        label    = asm.label    != None and '%-8s' % asm.label                   or lspace
        mnemonic = asm.mnemonic != None and '%-8s' % (e + asm.mnemonic)          or lspace
        operand  = asm.operand  != None and '%-8s' % (ni + str(asm.operand) + x) or lspace
        objCode  = asm.objCode  != None and '%-8s' % asm.objCode                 or lspace

        return '{}\t{}\t{}\t{}\t{}\n'.format(loc, label, mnemonic, operand, objCode)