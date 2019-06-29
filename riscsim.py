import sys
import argparse

registers = {}


class File:
    name = ''
    names = {}
    directives = []
    instructions = []


def init():

    for i in range(32):
        registers['x' + str(i)] = 0


def parseFile(name):
    file = File()
    file.name = name
    strings = []
    with open(name, 'r') as inp:
        temp = inp.readlines()
        temp = [i.strip() for i in temp]

    for el in temp:
        if el != '':
            strings.append(el)

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

    file.names = marks
    file.directives = direct
    file.instructions = inst
    return file


def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument()
    return parser


def main():
    init()
    file = parseFile('lisa.s')
    print(file.name)
    print(file.directives)
    print(file.names)
    print(file.instructions)
    count = file.names['swap']
    print(file.instructions[count])
    # parser = createParser()
    # params = parser.parse_args(sys.argv[1:])


main()
