
import sys
import Records as rc
import Symbols as sym
import OpcodeHelper as oh
import Assembly as asm

OBJ_DIR = 'input/test.obj'
SYM_DIR = 'input/test.sym'

ASM_DIR = 'output/out.asm'

if __name__ == '__main__':
    # input
    hRecord, tRecords, mRecords, eRecord = rc.ReadRecords(OBJ_DIR)
    symbols = sym.ReadSymbols(SYM_DIR)
    ocHelper = oh.OpcodeHelper()

    # for output
    BASE_R = 0
    LOCCTR = 0
    assembly = asm.CreateAssembly()

    # Symbol
    locList = list(symbols.keys())     # Symbol locs
    locList.extend(tRecords.keys())    # Text locs
    locList.append(hRecord.length)     # program max length
    locList.sort()

    for sLoc, s in symbols.items():
        operand = None
        if s.dType == 'BYTE' or s.dType == 'RESB' or s.dType == 'WORD' or s.dType == 'RESW':
            nextLoc = 0
            for loc in locList:
                if sLoc < loc:
                    nextLoc = loc
                    break
            
            size = nextLoc - sLoc
            operand = size      # BYTE or RESB
            if s.dType == 'WORD' or s.dType == 'RESW':
                operand = int(size / 3)
        
        assembly[sLoc] = asm.AssemblyLine(s.loc, s.label, s.dType, operand)

    # Text
    for tLoc, t in tRecords.items():

        LOCCTR = tLoc
        finishLoc = tLoc + t.length

        while LOCCTR < finishLoc:
            curAsm = None
            if assembly.get(LOCCTR) == None:
                curAsm = asm.AssemblyLine(LOCCTR)
            else:
                curAsm = assembly[LOCCTR]
            
            startIdx = (LOCCTR - tLoc) * 2
            curHalfByteLen = 0

            # BYTE, WORD directives
            if curAsm.mnemonic == 'BYTE':
                curHalfByteLen = curAsm.operand * 2
                curAsm.objCode = t.code[startIdx: startIdx + curHalfByteLen]

            elif curAsm.mnemonic == 'WORD':
                curHalfByteLen = curAsm.operand * 3 * 2
                curAsm.objCode = t.code[startIdx: startIdx + curHalfByteLen]

            else:
                curOpcode = int(t.code[startIdx: startIdx + 2], 16) & 0b11111100
                curFormat = ocHelper.getOpcode(curOpcode).opFormat
                
                # format checking
                if curFormat == oh.OpcodeFormatType.ONE.value:
                    curHalfByteLen = 2
                    curAsm.mnemonic = ocHelper.getOpcode(curOpcode).mnemonic.split(' ')[0]
                    curAsm.objCode = t.code[startIdx: startIdx + curHalfByteLen]


                elif curFormat == oh.OpcodeFormatType.TWO.value:
                    curHalfByteLen = 4

                    m = ocHelper.getOpcode(curOpcode).mnemonic.split(' ')
                    curAsm.mnemonic = m[0]
                    curAsm.objCode = t.code[startIdx: startIdx + curHalfByteLen]
                    
                    r12 = int(curAsm.objCode[2:4], 16)
                    r1 = ocHelper.getRegisterMnemonic(r12 >> 4)
                    r2 = ocHelper.getRegisterMnemonic(r12 & 0b1111)
                    
                    if len(m) >= 2:
                        if 'r1' in m[1]:
                            curAsm.operand = r1

                    if len(m) >= 3:
                        if 'r2' in m[2]:
                            curAsm.operand += ',' + r2

                    if curAsm.mnemonic == 'CLEAR':
                        if r1 == 'B':
                            BASE_R = 0

                else:   # 3/4
                    ni = int(t.code[startIdx + 1], 16) & 0b11
                    xbpe = int(t.code[startIdx + 2], 16)
                    x = xbpe & 0b1000
                    b = xbpe & 0b0100
                    p = xbpe & 0b0010
                    e = xbpe & 0b0001
                    
                    curHalfByteLen = e == 1 and 8 or 6
                    m = ocHelper.getOpcode(curOpcode).mnemonic.split(' ')

                    curAsm.mnemonic = m[0]
                    curAsm.objCode = t.code[startIdx: startIdx + curHalfByteLen]

                    # set flags
                    if ni == 0b10:
                        curAsm.indirectFlag = True
                    elif ni == 0b01:
                        curAsm.immediateFlag = True
                    if x != 0:
                        curAsm.indexAddrFlag = True
                    if e != 0:
                        curAsm.extendedFlag = True

                    # calculate operand loc & find loc label
                    operandLoc = int(curAsm.objCode[3:], 16)

                    if p != 0:
                        # -2048 <= disp <= 2047
                        if operandLoc > pow(2, 11) - 1:
                            operandLoc -= pow(2,12)
                        elif operandLoc < -pow(2, 11):
                            operandLoc += pow(2,12)
                        operandLoc += LOCCTR + int(curHalfByteLen / 2)

                    elif b != 0:
                        # 0 <= disp <= 4095
                        operandLoc += BASE_R

                    if len(m) >= 2 and m[1] == 'm':     # except RSUB
                        curAsm.operand = operandLoc

                        if symbols.get(operandLoc) != None and operandLoc != 0:
                            curAsm.operand = symbols[operandLoc].label

                    # set BASE register (for relative loc label)
                    if curAsm.mnemonic == 'LDB':
                        if ni == 0b10:  # not working, TBD
                            BASE_R = assembly[operandLoc].operand
                        elif ni == 0b01:
                            BASE_R = operandLoc
                        else:
                            BASE_R = LOCCTR
            

            # update assembly line & set next loc
            assembly[LOCCTR] = curAsm
            LOCCTR += int(curHalfByteLen / 2)


    # Header & End
    header = asm.AssemblyLine(hRecord.startingAddr, hRecord.programName, 'START', hRecord.startingAddr)
    end = asm.AssemblyLine(None, mnemonic='END', operand=symbols[eRecord.startingAddr].label)

    # Write Assembly file
    asm.WriteAssembly(ASM_DIR, header, assembly, end)

