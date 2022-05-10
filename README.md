# OISC2bis

Obfuscated Indirect Subleq with Coprocessor: 2 word instruction, version 2.  (That's what 'bis' means, from the Latin.)

This is the new and improved version, now with an actual parser.  And a stack.  And you don't have to use a separate file for the negative memory assignments.

The raw numbers are extremely obfuscated, but the parser makes it easy to use.  This may be against the spirit of esolangs.  Positive, negative, and zero valued instructions change the effects, and decimals make arguments indirect.  All instructions are in positive memory (use the absolute value).  Negative memory can only be accessed indirectly.

Usage:  python oisc2bis.py infile.o2a [outfile.o2c]

    Two word instruction:  A B

    A B    Effect
    + +    B = B - A
    - +    if [A] <= 0, jump to B
    + -    if [A] <=0, call B
    - -    if [A] <= 0, relative jump by [B]
    + 0    Push [A] onto the stack
    - 0    Pop the stack into A
    0 +    Execute instruction [B] on the stack
    0 -    if [B] <= 0, return
    0 0    halt

    Assembler formats:

    #            comment
    %            data (optional in negative memory)
    name:        naming a memory word
    name         using a named word
    *name        indirect reference [[name]] (if N is 23, *N is 23.0)
    @            this word
    ?            next word
    % --NEGATIVE: --NEGATIVE--     mandatory memory separator
    !            0
    ;            end of instruction
    ,            separator
    " or '       string delimiters
    ZERO         automatically created word containing 0
    &            negative and pointer (parser internal use)

    /sub can be called with 1 or 2 words (and still works without the '/sub')
        X Y      [Y] = [Y] - [X]
        X        [X] = 0
    /call, /jump and /relj can be called with 1 or 2 words.  
           Branching to a negative address will halt.
        X Y      if [X] <= 0, branch to Y (relative jump by [Y])
        X        unconditional branch to X (relative jump by [X])
    /push, /pop and /exec are called with 1 word
        X        push [X] / pop to X / execute instruction [X]
    /ret can be called with 0 or 1 word.  If the return stack is empty, the program will halt.
        X        if [X] <= 0, return
        -        unconditional return (ZERO inserted)
    /halt        takes no arguments



    Stack instructions:

         Positive                      Negative
    1    input char ( -- a)            output char (a -- )
    2    input digit  ( -- a)          output number (a -- )
    3    DUP (a -- aa)                 DROP (a -- )
    4    OVER (ab -- aba)              SWAP (ab -- ba)
    5    roll left N (abcd1 -- bcda)   roll right N (abcd2 -- cdab)
    6    reverse stack (abcd -- dcba)  clear stack (abcd -- )
    7    depth of stack ( -- a)        pick N (abcd3 -- abcdb) 
    8    bitwise true ( -- -1)         bitwise false ( -- 0)
    9    bitwise AND (ab -- a&b)       bitwise NOT (a -- ~a)
    10   bitwise OR (ab -- a|b)        bitwise XOR (ab -- a^b)
    11   shift left N bits (aN -- a)   shift right N bits (aN -- a)
    12   times (ab -- a*b)             divide (ab -- a/b)
    13   int division (ab -- a//b)     remainder (ab -- a%b)
    14   exponent e (a -- exp(a))      natural log (a -- log(a))
    15   convert to integer (a -- a)   convert to float (a -- a)
    16   alloc N words (sign matters)  free N words (sign matters)
    17   plus (ab -- a+b)              minus (ab -- a-b)
    18   sin (a -- sin(a))             asin (a -- asin(a))
    19   cos (a -- cos(a))             acos (a -- acos(a))
    20   tan (a -- tan(a))             atan (a -- atan(a))
    21   sinh (a -- sinh(a))           asinh (a -- asinh(a))
    22   cosh (a -- cos(a))            acosh (a -- acosh(a))
    23   tanh (a -- cos(a))            atanh (a -- atanh(a))

