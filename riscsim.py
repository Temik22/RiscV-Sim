import sys
import argparse

# todo list:
# 1. how to organize memory and have classification between .word/.half/.byte
# 2. organize debug mode


class answerFromMem:
    name = ''
    startValue = 0

    def __init__(self, name, value):
        self.name = name
        self.startValue = value


class MemoryBit:
    value = 0
    readonly = False

    def __init__(self, value=0, read=False):
        self.value = value
        self.readonly = read


class Machine:
    # class of simulator that is needed for changing machine status
    registers = {}
    memory = {}
    last_mem_byte = 0


class File:
    name = ''
    memLabels = {}
    names = {}
    directives = []
    instructions = []

    def __init__(self, name, labels, names, direct, inst):
        self.name = name
        self.memLabels = labels
        self.names = names
        self.directives = direct
        self.instructions = inst


def simInit():
    machine = Machine()
    for i in range(32):
        machine.registers['x' + str(i)] = 0
        # machine.registers['f' + str(i)] = 0.0
    return machine


def printRegisters(machine):
    # print out current situation of registers
    temp = []
    for key, value in machine.registers.items():
        string = ''
        string += key
        string += ': '
        string += str(value)
        temp.append(string)

    for i in range(8):
        string = ''
        for j in range(4):
            string += temp[j + i * 4]
            string += '\t'
        print(string)


def parseFile(name):
    # parse and make File object with ordered instructions,
    # there are names that pointed on some places in instructions array
    strings = []
    with open(name, 'r') as inp:
        temp = inp.readlines()
        temp = [i.strip() for i in temp]

    for el in temp:
        if el != '':
            strings.append(el)

    labels = {}
    marks = {}
    inst = []
    direct = []
    inside = False
    count = 0
    for el in strings:
        if el == '.text':
            inside = True
            continue
        if inside:
            if el[-1] == ':':
                marks[el[:-1]] = count
            else:
                inst.append(el)
                count += 1
        else:
            direct.append(el)

    file = File(name, labels, marks, direct, inst)
    return file


def parseDirectives(machine, file):
    # .data and .rodata were made
    settings = []
    for i in range(len(file.directives)):
        n = file.directives[i].find('.data')
        m = file.directives[i].find('.rodata')
        if n != -1:
            for j in range(i + 1, len(file.directives)):
                if file.directives[j].startswith('.'):
                    break
                settings.append(memoryAdd(machine, file.directives[j], False))
        if m != -1:
            for j in range(i + 1, len(file.directives)):
                if file.directives[j].startswith('.'):
                    break
                settings.append(memoryAdd(machine, file.directives[j], True))
    print(settings)


def memoryAdd(machine, string, type):
    # TODO()
    temp = string.split(':')
    temp[1] = temp[1].strip()
    print(temp)
    return temp[0]


def makeInstuctions(machine, marks, instructions, startLabel):
    # TODO()
    end = False
    current = marks.get(startLabel)
    while not end:
        line = instructions[current]


def createParser():
    # TODO()
    parser = argparse.ArgumentParser()
    parser.add_argument('-debug', action="store_const", const=True)
    return parser


def main():
    machine = simInit()
    file = parseFile('lisa.s')
    printRegisters(machine)
    parseDirectives(machine, file)
    # count = file.names['swap']
    # print(file.instructions[count])
    # parser = createParser()
    # params = parser.parse_args(sys.argv[1:])


main()
