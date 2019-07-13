import sys
import argparse

# todo list:
# 1. how to organize memory and have classification between .word/.half/.byte
# 2. organize debug mode
# 3. make less params

altRegNames = {'zero': 'x0', 'ra': 'x1', 'sp': 'x2', 'gp': 'x3', 'tp': 'x4', 't0': 'x5', 't1': 'x6', 't2': 'x7', 's0': 'x8', 's1': 'x9', 'a0': 'x10', 'a1': 'x11',
               'a2': 'x12', 'a3': 'x13', 'a4': 'x14', 'a5': 'x15', 'a6': 'x16', 'a7': 'x17', 's2': 'x18', 's3': 'x19', 's4': 'x20', 's5': 'x21', 's6': 'x22', 's7': 'x23',
               's8': 'x24', 's9': 'x25', 's10': 'x26', 's11': 'x27', 't3': 'x28', 't4': 'x29', 't5': 'x30', 't6': 'x31'}


class machineAnswer:
    name = ''
    status = ''


class startStatus:
    debug = False
    startLabel = ''

    def __init__(self, debug, label):
        self.debug = debug
        self.startLabel = label


class answerFromMem:
    name = ''
    startValue = 0

    def __init__(self, name, value):
        self.name = name
        self.startValue = value


class MemoryByte:
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


def memoryAdd(machine, string, type):
    # TODO()
    temp = string.split(':')
    temp[1] = temp[1].strip()
    print(temp)
    return temp[0]


def performInstructions(machine, marks, instructions, startStatus):
    # Think about end point that stops simulation
    end = False
    current = marks.get(startStatus.startLabel)
    while not end:
        line = instructions[current]
        command = line.split(' ')[0]
        line = line[len(command):].split(',')
        line = [i.strip() for i in line]
        print('{0} : {1}'.format(command, line))
        if command == 'lw':
            setRegValue(machine, line[0], int(line[1]))

        elif command == 'add':
            result = getRegValue(
                machine, line[1]) + getRegValue(machine, line[2])
            setRegValue(machine, line[0], result)

        # I think it must be rewrited with find()
        # add and addi have same function but different arguments
        #
        # elif command == 'addi':
        #     result = getRegValue(machine, line[1]) + int(line[2])
        #     setRegValue(machine, line[0], result)

        elif command == 'sub':
            result = getRegValue(
                machine, line[1]) - getRegValue(machine, line[2])
            setRegValue(machine, line[0], result)

        elif command == 'and':
            result = getRegValue(
                machine, line[1]) & getRegValue(machine, line[2])
            setRegValue(machine, line[0], result)

        elif command == 'or':
            result = getRegValue(
                machine, line[1]) | getRegValue(machine, line[2])
            setRegValue(machine, line[0], result)

        elif command == 'xor':
            result = getRegValue(
                machine, line[1]) ^ getRegValue(machine, line[2])
            setRegValue(machine, line[0], result)

        elif command == 'sll':
            result = getRegValue(
                machine, line[1]) << getRegValue(machine, line[2])
            setRegValue(machine, line[0], result)

        elif command == 'srl':
            result = getRegValue(
                machine, line[1]) >> getRegValue(machine, line[2])
            setRegValue(machine, line[0], result)

        elif command == 'j':
            if marks.get(line[0]) != None:
                current = marks[line[0]] - 1
            else:
                print('jump error')

        elif command == 'beq':
            if getRegValue(machine, line[0]) == getRegValue(machine, line[1]):
                current = marks[line[2]] - 1
            else:
                continue

        elif command == 'bne':
            if getRegValue(machine, line[0]) != getRegValue(machine, line[1]):
                current = marks[line[2]] - 1
            else:
                continue

        elif command == 'bge':
            if getRegValue(machine, line[0]) >= getRegValue(machine, line[1]):
                current = marks[line[2]] - 1
            else:
                continue

        elif command == 'blt':
            if getRegValue(machine, line[0]) < getRegValue(machine, line[1]):
                current = marks[line[2]] - 1
            else:
                continue

        else:
            print('command not found')

        current += 1

        if current == len(instructions):
            end = True




def getRegValue(machine, name):
    if machine.registers.get(name) != None:
        return machine.registers[name]
    elif machine.registers.get(altRegNames[name]) != None:
        return machine.registers[altRegNames[name]]
    else:
        print('cannot get register value')


def setRegValue(machine, name, value):
    if machine.registers.get(name) != None:
        machine.registers[name] = value
    elif machine.registers.get(altRegNames[name]) != None:
        machine.registers[altRegNames[name]] = value
    else:
        print('cannot set register value')


def createParser():
    # TODO()
    parser = argparse.ArgumentParser()
    parser.add_argument('-debug', action="store_const", const=True)
    return parser


def main():
    machine = simInit()
    file = parseFile('temp.s')
    parseDirectives(machine, file)
    start = startStatus(False, 'main')
    performInstructions(machine, file.names, file.instructions, start)
    printRegisters(machine)
    # count = file.names['swap']
    # print(file.instructions[count])
    # parser = createParser()
    # params = parser.parse_args(sys.argv[1:])


main()
