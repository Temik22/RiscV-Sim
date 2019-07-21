import sys
import argparse

# todo list:
# 1. how to organize memory and have classification between .word/.half/.byte
# 2. organize debug mode
# 3. make less params

altRegNames = {'zero': 'x0', 'ra': 'x1', 'sp': 'x2', 'gp': 'x3', 'tp': 'x4', 't0': 'x5', 't1': 'x6', 't2': 'x7', 's0': 'x8', 's1': 'x9', 'a0': 'x10', 'a1': 'x11',
               'a2': 'x12', 'a3': 'x13', 'a4': 'x14', 'a5': 'x15', 'a6': 'x16', 'a7': 'x17', 's2': 'x18', 's3': 'x19', 's4': 'x20', 's5': 'x21', 's6': 'x22', 's7': 'x23',
               's8': 'x24', 's9': 'x25', 's10': 'x26', 's11': 'x27', 't3': 'x28', 't4': 'x29', 't5': 'x30', 't6': 'x31'}


class Answer:
    status = ''
    value = ''


class startStatus:
    debug = False
    steps = -1
    startLabel = ''

    def __init__(self, debug, label, steps):
        self.debug = debug
        self.steps = steps
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
    memory = []
    stack = []


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


def getAleternativeName(name):
    for key, value in altRegNames.items():
        if value == name:
            return key


def printRegisters(machine):
    # print out current situation of registers
    temp = []
    for key, value in machine.registers.items():
        string = ''
        string += '{0}({1})'.format(getAleternativeName(key), key)
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
    for i in range(len(file.directives)):
        data = file.directives[i].find('.data')
        rodata = file.directives[i].find('.rodata')
        if data != -1:
            for j in range(i + 1, len(file.directives)):
                if file.directives[j].startswith('.'):
                    break
                answer = memoryAdd(machine, file.directives[j], False)
                file.memLabels[answer.name] = answer.startValue
        if rodata != -1:
            for j in range(i + 1, len(file.directives)):
                if file.directives[j].startswith('.'):
                    break
                answer = memoryAdd(machine, file.directives[j], True)
                file.memLabels[answer.name] = answer.startValue


def memoryAdd(machine, string, readOnly):
    # TODO()
    start = len(machine.memory)
    temp = string.split(':')
    name = temp[0]
    temp[1] = temp[1].strip()
    i = 0
    while temp[1][i] != ' ':
        i += 1
    param = temp[1][:i]
    values = temp[1][i:].split(',')
    values = [int(i.strip()) for i in values]
    for value in values:
        if param == '.word':
            piece1 = MemoryByte(value % 256, readOnly)
            piece2 = MemoryByte(value // 256, readOnly)
            piece3 = MemoryByte(value // (256 * 256), readOnly)
            piece4 = MemoryByte(value // (256 * 256 * 256), readOnly)
            machine.memory.append(piece1)
            machine.memory.append(piece2)
            machine.memory.append(piece3)
            machine.memory.append(piece4)
        elif param == '.half':
            piece1 = MemoryByte(value % 256, readOnly)
            piece2 = MemoryByte(value // 256, readOnly)
            machine.memory.append(piece1)
            machine.memory.append(piece2)
        elif param == '.byte':
            piece1 = MemoryByte(value % 256, readOnly)
            machine.memory.append(piece1)
    return answerFromMem(name, start)


def performInstructions(machine, file, start):
    # Think about end point that stops simulation
    end = False
    current = file.names.get(start.startLabel)
    simStatus = Answer()
    print('Start simulation ...')
    tempDebug = False
    if start.debug:
        print(
            'Simulation was started in debug mode.\
            \nPrint [s] for perform one instruction,\
 [c] for perform all instructions.\
            \nPrint [print] for registers values')
        tempDebug = True
    while not end:
        if tempDebug:
            while True:
                action = input().strip()
                if action == 's':
                    break
                elif action == 'c':
                    tempDebug = False
                    break
                elif action == 'print':
                    printRegisters(machine)
                    continue
                else:
                    print('command not found. try again ...')
                    continue

        line = file.instructions[current]
        command = line.split(' ')[0]
        line = line[len(command):].split(',')
        line = [i.strip() for i in line]
        print('{0} : {1}'.format(command, line))
        if command == 'la':
            setRegValue(machine, line[0], file.memLabels[line[1]])

        elif command == 'lw' or command == 'lh' or command == 'lb':
            i = 0
            while line[1][i] != '(':
                i += 1
            delta = int(line[1][:i])
            register = line[1][i + 1:len(line[1]) - 1]
            result = 0
            if command == 'lw':
                for i in reversed(range(1, 4)):
                    result += machine.memory[getRegValue(
                        machine, register) + delta + i].value
                    result *= 256
                result += machine.memory[getRegValue(
                    machine, register) + delta].value
            elif command == 'lh':
                result += machine.memory[getRegValue(
                    machine, register) + delta + 1].value * 256
                result += machine.memory[getRegValue(
                    machine, register) + delta].value
            else:
                result += machine.memory[getRegValue(
                    machine, register) + delta].value
            setRegValue(machine, line[0], result)

        elif command == 'li':
            setRegValue(machine, line[0], int(line[1]))

        elif command == 'add':
            result = getRegValue(
                machine, line[1]) + getRegValue(machine, line[2])
            setRegValue(machine, line[0], result)

        elif command == 'addi':
            result = getRegValue(machine, line[1]) + int(line[2])
            setRegValue(machine, line[0], result)

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
            if file.names.get(line[0]) != None:
                current = file.names[line[0]] - 1
            else:
                simStatus.status = 'error'
                simStatus.value = 'jump error: no such label [{}]'.format(
                    line[0])
                break

        elif command == 'beq':
            if getRegValue(machine, line[0]) == getRegValue(machine, line[1]):
                current = file.names[line[2]] - 1
            else:
                continue

        elif command == 'bne':
            if getRegValue(machine, line[0]) != getRegValue(machine, line[1]):
                current = file.names[line[2]] - 1
            else:
                continue

        elif command == 'bge':
            if getRegValue(machine, line[0]) >= getRegValue(machine, line[1]):
                current = file.names[line[2]] - 1
            else:
                continue

        elif command == 'blt':
            if getRegValue(machine, line[0]) < getRegValue(machine, line[1]):
                current = file.names[line[2]] - 1
            else:
                continue

        else:
            simStatus.status = 'error'
            simStatus.value = 'command not found [{}]'.format(command)
            break

        current += 1
        start.steps -= 1

        if current == len(file.instructions) or start.steps == 0:
            simStatus.status = 'success'
            simStatus.value = 'simulation was finished'
            end = True
    return simStatus


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
    parser = argparse.ArgumentParser(description='Python based Risc V simulator',
                                     epilog='(c) Memaster 2019 alpha 1.0',
                                     add_help=True)
    parser.add_argument('-d', '--debug', action="store_true",
                        help='switch simulator in debug mode')
    parser.add_argument('-i', '--info', action='store_true',
                        help='print registers before end of work')
    parser.add_argument('-s', '--steps', type=int,
                        help='it\'s a number of steps before simulation will be stoped')
    parser.add_argument(
        '-b', '--begin', help='name of label from which simulation starts. default value: main')
    parser.add_argument('fileName', nargs='?',
                        help='name of file (*.s) with instructions')
    return parser


def main():
    parser = createParser()
    params = parser.parse_args(sys.argv[1:])
    if params.fileName:
        debug = False
        steps = -1
        begin = 'main'
        machine = simInit()
        file = parseFile(params.fileName)
        parseDirectives(machine, file)
        if params.steps:
            steps = params.steps
        if params.debug:
            debug = True
            steps = -1
        if params.begin:
            begin = params.begin
        start = startStatus(debug, begin, steps)
        result = performInstructions(machine, file, start)
        if params.info:
            printRegisters(machine)
        print('Status: {0}\nDescription: {1}'.format(
            result.status, result.value))
    else:
        print('Status: error\nDescription: file name was not specified')


main()
