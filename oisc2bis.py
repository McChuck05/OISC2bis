# OISC:2bis master program
# Copyright (C) 2022 McChuck
# Released under GNU General Public License
# See LICENSE for more details.
# Many thanks to Lawrence Woodman for inspiration and examples.
# Check out         https://techtinkering.com/articles/subleq-a-one-instruction-set-computer/
# And especially    https://techtinkering.com/2009/05/15/improving-the-standard-subleq-oisc-architecture/
# And maybe watch   https://www.youtube.com/watch?v=FvwcRaE9yxc

import sys
import os
from oisc2bis_parser import Parser
from oisc2bis_vm import VM
try:
    from getch import getch, getche         # Linux
except ImportError:
    from msvcrt import getch, getche        # Windows


def Write_file(out_file, mem, neg0):
    count = 0
    maxpc = len(mem)
    neg = False
    if neg0 > 0:
        printneg = mem[neg0:]
        printneg.reverse()
        printmem = mem[:neg0]
        printmem.extend(printneg)
    for pc in range(maxpc):
        if pc == neg0 and pc != 0:
            out_file.write("\n\n% --NEGATIVE--: --NEGATIVE-- \n\n")
            neg = True
            count = 0
        a = printmem[pc]
        out_file.write('{} '.format(a))
        count += 1
        if count % 2 == 0:
            out_file.write("; ")
        if count == 10:
            out_file.write("\n")
            count = 0
    out_file.write("\n")



def Oisc2bis(args):
    try:
        in_name = args[0]
        out_name = None
        if len(args) == 2:
            out_name = args[1]
        parser = Parser()
        vm = VM()
        mem = []
        with open(in_name, "r") as in_file:
            raw = in_file.read()
            mem, neg0 = parser.parse(raw)
            in_file.close()
        if  out_name != None:
            with open(out_name, "w") as out_file:
                Write_file(out_file, mem, neg0)
                out_file.close()
        vm.do_vm(mem, neg0)
    except(ValueError, IndexError):
        print("I just don't know what went wrong!\n")
        in_file.close()

def main(args):
    try:
        print()
        if len(args) == 1:
            print()
            Oisc2bis(args)
        elif len(args) == 2:
            if os.path.isfile(args[1]):
                print(args[1], "exists.  Overwrite? ", end="", flush=True)
                answer = getche()
                if answer in ["y", "Y"]:
                    print()
                    print(args[1], "replaced \n\n", flush=True)
                    Oisc2bis(args)
                else:
                    print()
                    print(args[1], "retained \n\n", flush=True)
                    Oisc2bis([args[0]])
            else:
                print("creating", args[1], "\n\n", flush=True)
                Oisc2bis(args)
        else:
            print("\nusage: python oisc2bis.py infile.o2a [outfile.o2c]\n")
    except FileNotFoundError:
        print("\n< *Peter_Lorre* >\nYou eediot!  What were you theenking?\nTry it again, but thees time with a valid file name!\n</ *Peter_Lorre* >\n")
        print("\nusage: python oisc2bis.py infile.o2a [outfile.o2c]\n")


if __name__ == '__main__':
    print("\nOISC:2bis starting up.")
    try:
        main(sys.argv[1:])
    except IndexError:
        print("\nusage:  python oisc2bis.py infile.o2a [outfile.o2c]")
    finally:
        print("\n\nOISC:2bis shutting down.\n")
