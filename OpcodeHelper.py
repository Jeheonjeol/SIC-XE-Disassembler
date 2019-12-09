from enum import Enum

OPCODE_DIR = 'input/SIC_BIN.txt'

class OpcodeFormatType(Enum):
    ONE = '1'
    TWO = '2'
    THREE_OR_FOUR = '3/4'


class Opcode:
    def __init__(self, mnemonic, opFormat, opcode, op, effect, notes = None):
        self.mnemonic = mnemonic
        self.opFormat = opFormat
        self.opcode = opcode
        self.op = op
        self.effect = effect
        self.notes = notes


class OpcodeHelper:
    def __init__(self):
        self.opcodes = self.readOpcodes(OPCODE_DIR)
    
    def readOpcodes(self, OPCODE_DIR):
        opcodes = dict()

        f = open(OPCODE_DIR, 'r')
        for line in f.readlines():
            temp = line.replace('\n', '').split('\t')

            notes = len(temp) >= 6 and temp[5] or None
            op = Opcode(temp[0], temp[1], temp[2], temp[3], temp[4], notes)
            opcodes[int(op.opcode, 16)] = op

        f.close()

        return opcodes

    def getOpcode(self, opcode):
        return self.opcodes[opcode]

    def getRegisterMnemonic(self, value):
        if value == 0:
            return 'A'
        elif value == 1:
            return 'X'
        elif value == 2:
            return 'L'
        elif value == 3:
            return 'B'
        elif value == 4:
            return 'S'
        elif value == 5:
            return 'T'
        elif value == 6:
            return 'F'
        elif value == 8:
            return 'PC'
        elif value == 9:
            return 'SW'

        return None
