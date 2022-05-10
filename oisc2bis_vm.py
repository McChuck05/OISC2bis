# OISC:2bis virtual machine
# Copyright (C) 2022 McChuck
# Released under GNU General Public License
# See LICENSE for more details.


try:
    from getch import getch, getche         # Linux
except ImportError:
    from msvcrt import getch, getche        # Windows

import math

class VM:
    stack = []
    returnstack = []
    memory = []
    neg0 = 0
    neg_max = 0

    def do_vm(self, passmem, passneg0):
        try:
            pointer = 0
            running = True
            input_buffer = []
            self.memory = passmem
            self.neg0 = passneg0
            if passneg0 > 0:
                self.neg_max = passneg0 - (len(passmem) + 1)

            def execute(i):         #   coprocessor instructions on stack elements
                if i == 0:          #   NOP
                    pass
                elif i == 1:        #   input char
                    a = getche()
                    self.stack.append(ord(a))
                elif i == -1:       #   print char
                    a = self.stack.pop(-1)
                    if a >= 0:
                        print(chr(int(a)), end="", flush=True)
                    else:
                        print("\n\nCan't print a negative character!\n", flush=True)
                        raise ValueError
                elif i == 2:        #   input digit
                    a = getche()
                    if a.isdigit():             # for longer numbers, use a.isnumeric()
                        self.stack.append(int(a))
                    else:
                        print("\nExpected a digit\n", flush=True)
                        self.stack.append(-1)
                elif i == -2:       #   output number
                    a = self.stack.pop(-1)
                    print(a, end="", flush=True)
                elif i == 3:        #   DUP     A - A A
                    self.stack.append(self.stack[-1])
                elif i == -3:       #   DROP    A -
                    a = self.stack.pop(-1)
                elif i == 4:        #   OVER    A B - A B A
                    a = self.stack[-2]
                    self.stack.append(a)
                elif i == -4:       #   SWAP    A B - B A
                    a = self.stack.pop(-2)
                    self.stack.append(a)
                elif i == 5:        #   Roll Left   A B C D - D A B C
                    a = self.stack.pop(-1)
                    self.stack.insert(0, a)
                elif i == -5:       #   Roll Right  A B C D - B C D A
                    a = self.stack.pop(0)
                    self.stack.append(a)
                elif i == 6:        #   REVERSE     A B C D - D C B A
                    self.stack.reverse()
                elif i == -6:       #   CLEAR       A B C -
                    self.stack = []
                elif i == 7:        #   Depth             - A
                    a = len(self.stack)
                    self.stack.append(a)
                elif i == -7:       #   PICK A          A - A
                    a = self.stack.pop(-1)
                    self.stack.append(self.stack[-a])
                elif i == 8:        #   bitwise True    - A
                    self.stack.append(-1)
                elif i == -8:       #   bitwise False   - A
                    self.stack.append(0)
                elif i == 9:        #   bitwide AND     A B - A
                    b = self.stack.pop(-1)
                    a = self.stack.pop(-1)
                    self.stack.append(a & b)
                elif i == -9:       #   bitwise NOT     A - A
                    a = self.stack.pop(-1)
                    self.stack.append(~a)
                elif i == 10:       #   bitwise OR      A B - A
                    b = self.stack.pop(-1)
                    a = self.stack.pop(-1)
                    self.stack.append(a | b)
                elif i == -10:      #   bitwise XOR     A B - A
                    b = self.stack.pop(-1)
                    a = self.stack.pop(-1)
                    self.stack.append(a ^ b)
                elif i == 11:        #   Shift A left by B bits      A B - A
                    b = self.stack.pop(-1)
                    a = self.stack.pop(-1)
                    self.stack.append(a << b)
                elif i == -11:      #   Shift A right by B bits     A B - A
                    b = self.stack.pop(-1)
                    a = self.stack.pop(-1)
                    self.stack.append(a >> b)
                elif i == 12:      #   A * B           A B - A
                    b = self.stack.pop(-1)
                    a = self.stack.pop(-1)
                    self.stack.append(b * a)
                elif i == -12:      #   A / B           A B - A
                    b = self.stack.pop(-1)
                    a = self.stack.pop(-1)
                    self.stack.append(a / b)
                elif i == 13:       #   A // B          A B - A
                    b = self.stack.pop(-1)
                    a = self.stack.pop(-1)
                    self.stack.append(a // b)
                elif i == -13:      #   A % B           A B - A
                    b = self.stack.pop(-1)
                    a = self.stack.pop(-1)
                    self.stack.append(a % b)
                elif i == 14:       #   e**A          A - A       natural anti-log
                    a = self.stack.pop(-1)
                    self.stack.append(math.exp(a))
                elif i == -14:      #   ln(A)           A - A      natural log
                    a = self.stack.pop(-1)
                    self.stack.append(math.log(a))
                elif i == 15:       #   convert to int  A - A       adjusts a tiny bit to cover float rounding errors
                    a = self.stack.pop(-1)
                    if a > 0:
                        self.stack.append(int(a + 0.0000001))
                    else:
                        self.stack.append(int(a - 0.0000001))
                elif i == -15:      #   convert to float    A - A
                    a = self.stack.pop(-1)
                    self.stack.append(float(a))
                elif i == 16:       #   alloc memory (positive or negative) A -
                    a = self.stack.pop(-1)
                    blanks = [0] * abs(a)
                    newmem = self.memory[:self.neg0] + blanks + self.memory[self.neg0:]
                    if a > 0:
                        self.neg0 += a
                    else:
                        self.neg_max += a
                    self.memory = newmem
                elif i == -16:       #   free memory (poitive or negative)   A -
                    a = self.stack.pop(-1)
                    if a > 0:
                        self.neg0 -= a
                        newmem = self.memory[:self.neg0] + self.memory[self.neg0:]
                    else:
                        newmem = self.memory[:self.neg0] + self.memory[(self.neg0 - a):]
                        self.neg_max -= a
                    self.memory = newmem
                elif i == 17:       #   A + B           A B - A
                    b = self.stack.pop(-1)
                    a = self.stack.pop(-1)
                    self.stack.append(a + b)
                elif i == -17:      #   A - B           A B - A
                    b = self.stack.pop(-1)
                    a = self.stack.pop(-1)
                    self.stack.append(a - b)
                elif i == 18:       #   sin(A)          A - A
                    a = self.stack.pop(-1)
                    self.stack.append(math.sin(a))
                elif i == -18:      #   asin(A)         A - A
                    a = self.stack.pop(-1)
                    self.stack.append(math.asin(a))
                elif i == 19:      #   cos(A)          A - A
                    a = self.stack.pop(-1)
                    self.stack.append(math.cos(a))
                elif i == -19:      #   acos(A)         A - A
                    a = self.stack.pop(-1)
                    self.stack.append(math.acos(a))
                elif i == 20:       #   tan(A)          A - A
                    a = self.stack.pop(-1)
                    self.stack.append(math.tan(a))
                elif i == -20:      #   atan(A)         A - A
                    a = self.stack.pop(-1)
                    self.stack.append(math.atan(a))
                elif i == 21:       #   sinh(A)         A - A
                    a = self.stack.pop(-1)
                    self.stack.append(math.sinh(a))
                elif i == -21:      #   asinh(A)        A - A
                    a = self.stack.pop(-1)
                    self.stack.append(math.hsinh(a))
                elif i == 22:       #   cosh(A)         A - A
                    a = self.stack.pop(-1)
                    self.stack.append(math.cosh(a))
                elif i == -22:      #   acosh(A)        A - A
                    a = self.stack.pop(-1)
                    self.stack.append(math.acosh(a))
                elif i == 23:       #   tanh(A)         A - A
                    a = self.stack.pop(-1)
                    self.stack.append(math.tanh(a))
                elif i == -23:      #   atanh(A)        A - A
                    a = self.stack.pop(-1)
                    self.stack.append(math.atanh(a))

                return      # end execute(i)


            def isindirect(i):
                return(type(i) is float)

            def mem_eval(i):
                if isindirect(i):
                    if i > 0:                   # adjust for float rounding errors
                        a = abs(int(i + 0.0000001))
                    else:
                        a = abs(int(i - 0.0000001))
                    if a >= self.neg0:
                        print("Memory location ", a, "out of bounds", flush=True)
                        raise IndexError
                    mem_ref = self.memory[a]
                    if mem_ref >= self.neg0 or mem_ref < self.neg_max:
                        print("Indirect memory location", mem_ref, "out of bounds", flush=True)
                        raise IndexError
                    mem_val = self.memory[mem_ref]
                else:
                    mem_ref = abs(i)
                    if mem_ref >= self.neg0:
                        print("Memory location", mem_ref, "out of bounds", flush=True)
                        raise IndexError
                    mem_val = self.memory[mem_ref]
                return(mem_ref, mem_val)


            while running:
                nextpoint = pointer + 2
                a = self.memory[pointer]
                b = self.memory[pointer + 1]
                instr_type = 0
                a_ref = 0; a_val = 0
                b_ref = 0; b_val = 0

                if a != 0:
                    a_ref, a_val = mem_eval(a)
                    if a > 0:
                        instr_type += 6
                    else:
                        instr_type += 3
                if b != 0:
                    b_ref, b_val = mem_eval(b)
                    if b > 0:
                        instr_type += 2
                    else:
                        instr_type += 1
                if instr_type == 0:                 #   0 0     Halt                            /halt
                    running = False
                elif instr_type == 1:               #   0 -     if B<=0, Return                 /ret
                    if b_val <= 0:
                        if len(self.returnstack) > 0:
                            nextpoint = self.returnstack.pop(-1)
                        else:
                            running = False
                elif instr_type == 2:               #   0 +     Exec B                          /exec
                    execute(b_val)
                elif instr_type == 3:               #   - 0     Pop to A                        /pop
                    self.memory[a_ref] = self.stack.pop(-1)
                elif instr_type == 4:               #   - -     if A<=0, Relative Jump by B     /relj
                    if a_val <= 0:
                        nextpoint = pointer + b_val
                elif instr_type == 5:               #   - +     if A<=0, Jump B                 /jump
                    if a_val <= 0:
                        nextpoint = b_ref
                elif instr_type == 6:               #   + 0     Push A                          /push
                    self.stack.append(a_val)
                elif instr_type == 7:               #   + -     if A<=0, Call B                 /call
                    if a_val <= 0:
                        self.returnstack.append(nextpoint)
                        nextpoint = b_ref
                elif instr_type == 8:               #   + +     B -= A                          /sub
                    self.memory[b_ref]  = b_val - a_val
                else:
                    print("\n\nUnexpected error.  How did you do this?", flush=True)
                    print(pointer, a, b, "\n", flush=True)
                    running = False
                    raise ValueError

                if nextpoint < 0:
                    running = False
                else:
                    pointer = nextpoint


        except IndexError:
            print("\nMemory out of bounds error at instruction", pointer)
            running = False
            raise
