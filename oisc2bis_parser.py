 # OISC:2bis parser
 # Copyright (C) 2022 McChuck
 # based on original Copyright (C) 2013 Chris Lloyd
        # https://github.com/cjrl
        # lloyd.chris@verizon.net
 # Released under GNU General Public License
 # See LICENSE for more details.


 #  A B     /sub    [B] = [B] - [A]
 #  B       /sub    [B] = 0                 B = B - B
 #  *A B    /sub    [B] = [B] - [[A]]       indirect referencing denoted by float type

 #  -A B    /jump   if [A]<=0, jump to B
 #  A -B    /call   if [A]<=0, call B       sets up for a return
 #  -A -B   /relj   if [A]<=0, relative jump by [B]
 #  A 0     /push   push [A] onto the stack
 #  -A 0    /pop    pop the stack to A
 #  0 B     /exec   execute instruction [B] on the stack
 #  0 -B    /ret    if [A]<=0, return
 #  0 0     /halt   halt (will also halt on a jump to negative address and on a return without a previous call)

 #  ?        next address
 #  @        this address
 #  label:   address label, cannot be the only thing on a line
 #  *label   pointer to address label, represented as a floating point number
 #  &        both negative and a pointer (created automatically)
 #  !        0
 #  ;        end of instruction
 #  ,        data separator
 #  #        comment
 #  " or '   string delimeters, must be data
 #  %        data indicator (optional in negative memory)
 #  % --NEGATIVE: --NEGATIVE--      begin negative memory MANDATORY


class Parser:

    tokens = []
    label_table = {}
    neg0 = 0


    def parse(self,string):
        string = self.expand_literals(string)
        string = string.replace('\n',';')
        string = string.replace('#',';#')
        string = string.replace(':',': ')
        string = string.replace('%','% ')
        string = string.replace('!', "0 ")
        string = string.replace('@', '@ ')
        string = string.replace('?', '? ')
        string = string.replace(',', ' ')
        self.strip_tokens(string)
        self.parse_labels()
        self.handle_macros()
        self.expand_instructions()
        self.update_labels()
        self.tokens = [token for token in sum(self.tokens, []) if token != '%']
        self.neg0 = self.label_table["--NEGATIVE--"]
        self.resolve_negativememory()
        self.resolve_labels();
        try:
            response = []
            for token in self.tokens:
                if '.' in str(token):
                    response.append(float(token))
                else:
                    response.append(int(token))
            return(response, self.neg0)
        except ValueError:
            print("Unmatched label:", token, flush=True)
            raise


    def strip_tokens(self, string):
        self.tokens = [token.split() for token in string.split(';') if not '#' in token and token.strip()]
        if 'ZERO:' not in sum(self.tokens, start=[]):
            spot = self.tokens.index(['%', '--NEGATIVE--:', '--NEGATIVE--'])
            self.tokens.insert(spot, ['%', 'ZERO:', '0'])


    def macro_fail(self, instr, token):
        print("Macro", instr, "failed at", token)
        raise ValueError


    def handle_macros(self):
        def setneg(i, count):
            if count == 1 or count == 3:
                instr1 = self.tokens[i][0]
                first_char = instr1[0]
                if first_char == '*':
                    instr1 = '&' + instr1[1:]
                else:
                    if instr1[0] != '-':
                        instr1 = '-' + instr1
                self.tokens[i][0] = instr1
            if count == 2 or count == 3:
                instr2 = self.tokens[i][1]
                first_char = instr2[0]
                if first_char == '*':
                    instr2 = '&' + instr2[1:]
                else:
                    if instr2[0] != '-':
                        instr2 = '-' + instr2
                self.tokens[i][1] = instr2
        # end setneg()

        for i, token in enumerate(self.tokens):
            instr = token[0]
            if instr[0] == '/':
                self.tokens[i].remove(instr)
                count = len(token)
                if count > 2:
                    self.macro_fail(instr, token)
                elif instr == "/sub":
                    if count == 0:
                        self.macro_fail(instr, token)
                elif instr == "/jump":
                    if count == 1:
                        self.tokens[i].insert(0, "-ZERO")
                    elif count == 2:
                        setneg(i, 1)
                    else:
                        self.macro_fail(instr, token)
                elif instr == "/call":
                    if count == 1:
                        self.tokens[i].insert(0, "ZERO")
                        setneg(i, 2)
                    elif count == 2:
                        setneg(i, 2)
                    else:
                        self.macro_fail(instr, token)
                elif instr == "/relj":
                    if count == 1:
                        self.tokens[i].insert(0, '-ZERO')
                        setneg(i, 2)
                    elif count == 2:
                        setneg(i, 3)
                    else:
                        self.macro_fail(instr, token)
                elif instr == "/push":
                    if count == 1:
                        self.tokens[i].append('0')
                    else:
                        self.macro_fail(instr, token)
                elif instr == "/pop":
                    if count == 1:
                        self.tokens[i].append("0")
                        setneg(i, 1)
                    else:
                        self.macro_fail(instr, token)
                elif instr == "/exec":
                    if count == 1:
                        self.tokens[i].insert(0, '0')
                    else:
                        self.macro_fail(instr, token)
                elif instr == "/ret":
                    if count == 1:
                        self.tokens[i].insert(0, '0')
                        setneg(i, 2)
                    else:
                        self.macro_fail(instr, token)
                elif instr == "/halt":
                    if count == 0:
                        self.tokens[i] = ['0', '0']
                    else:
                        self.macro_fail(instr, token)
                else:
                    self.macro_fail(instr, token)
    # end handle_macros()

    def resolve_negativememory(self):
        negmem = False
        maxtoken = len(self.tokens)
        how_many = maxtoken - self.neg0
        reversed_tokens = []
        for i, label in enumerate(self.label_table):
            value = self.label_table[label]
            if label == "--NEGATIVE--":
                negmem = True
            elif negmem == True:
                self.label_table[label] = self.neg0 - value
        for i in range(how_many):
            item = self.tokens.pop(-1)
            reversed_tokens.append(item)
        reversed_tokens.pop(-1)             # get rid of the '--NEGATIVE--' so data starts at -1
        self.tokens.extend(reversed_tokens)


    def resolve_labels(self):
        for i, token in enumerate(self.tokens):
            if token[0] == "*":                 # pointer
                token = token[1:]
                if token in self.label_table:
                    self.tokens[i] = float(self.label_table[token])
            elif token[0] == '&':               # pointer and negative
                token = token[1:]
                if token in self.label_table:
                     self.tokens[i] = -(float(self.label_table[token]))
            elif token[0] == '-':               # negative
                token = token[1:]
                if token in self.label_table:
                     self.tokens[i] = -(int(self.label_table[token]))
            elif token == '?':                  # next
                if i < self.neg0:
                    self.tokens[i] = i + 1
                else:
                    self.tokens[i] = i -len(self.tokens) - 1
            elif token == "@":                  # here
                if i < self.neg0:
                    self.tokens[i] = i
                else:
                    self.tokens[i] = i -len(self.tokens)
            elif token in self.label_table:
                self.tokens[i] = self.label_table[token]


    def update_labels(self):
        for i, label in enumerate(self.label_table):
            self.label_table[label] = self.get_label_index(label)


    def get_label_index(self,label):
        index = 0
        address, x = self.label_table[label]
        for i in range(address):
            index += len(self.tokens[i])
            if '%' in self.tokens[i][0]:
                index -= 1 
        if '%' in self.tokens[address][0]:
            return index + x - 1
        return index


    def expand_instructions(self):
        pastneg = False
        for token_index, token in enumerate(self.tokens):
            oprands = []
            if "--NEGATIVE--" in token:
                pastneg = True
            if not(token[0] == '%' or pastneg == True):
                how_many = len(token)
                if how_many == 1:
                    oprands = [token[0], token[0]]
                elif how_many == 2:
                    oprands = [token[0], token[1]]
                else:
                    oprands = token     # used for pre-compiled or raw numbers programs
                self.tokens[token_index] = oprands


    def parse_labels(self):
        for token_index, token in enumerate(self.tokens):
            for operand_index, operand in enumerate(token):
                if operand[-1] == ':':
                    token.remove(operand)
                    operand = operand[:-1]
                    self.label_table[operand] = (token_index, operand_index)


    def expand_literals(self,string):
        in_dq_literal = False       # "
        in_sq_literal = False       # '
        expanded_string = ""
        for char in string:
            if char == '"' and not in_sq_literal:
                in_dq_literal ^= True
            elif char == "'" and not in_dq_literal:
                in_sq_literal ^= True
            elif in_dq_literal or in_sq_literal:
                expanded_string += str(ord(char)) + ' '
            else:
                expanded_string += char
        return expanded_string
