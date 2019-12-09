from enum import Enum

class RecordType(Enum):
    H = 'H'
    T = 'T'
    M = 'M'
    E = 'E'


class Record:
    def __init__(self, rtype, name, addr, length, code = None):
        self.recordType   = rtype
        self.programName  = name     # H: Col. 2~7
        self.startingAddr = addr     # H: Col. 8~13  / E: Col. 2~7  / T & M: Col. 2~7
        self.length       = length   # H: Col. 14-19 / T & M: Col. 8~9
        self.code         = code     # T: Col. 10~69
        

def ReadRecords(OBJ_DIR):
    hRecord = None
    tRecords = dict()
    mRecords = dict()
    eRecord = None

    f = open(OBJ_DIR, 'r')
    for line in f.readlines():
        line = line.replace('\n', '')

        if line[0] == RecordType.H.value:
            hRecord = Record(RecordType.H.value, line[1:7], int(line[7:13], 16), int(line[13:19], 16))

        elif line[0] == RecordType.T.value:
            tRecord = Record(RecordType.T.value, None, int(line[1:7], 16), int(line[7:9], 16), line[9:])
            tRecords[tRecord.startingAddr] = tRecord

        elif line[0] == RecordType.M.value:
            mRecord = Record(RecordType.M.value, None, int(line[1:7], 16), int(line[7:9], 16))
            mRecords[mRecord.startingAddr] = mRecord

        elif line[0] == RecordType.E.value:
            eRecord = Record(RecordType.E.value, None, int(line[1:7], 16), None)
        
    f.close()

    return (hRecord, tRecords, mRecords, eRecord)