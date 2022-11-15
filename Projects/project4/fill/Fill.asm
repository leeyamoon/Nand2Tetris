// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.


(WHILE)
@SCREEN
D = A
@8191
D = D + A
@R0
M = D
@KBD
D = M
@LOOP0
D;JEQ
(LOOP1)
@R0
D = M
M = M - 1
A = D
M = -1
@SCREEN
D = D - A
@WHILE
D;JEQ
@LOOP1
0;JMP
(LOOP0)
@R0
D = M
M = M - 1
A = D
M = 0
@SCREEN
D = D - A
@WHILE
D;JEQ
@LOOP0
0;JMP



