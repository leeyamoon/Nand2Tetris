// This file is part of nand2tetris, as taught in The Hebrew University,
// and was written by Aviv Yaish, and is published under the Creative 
// Common Attribution-NonCommercial-ShareAlike 3.0 Unported License 
// https://creativecommons.org/licenses/by-nc-sa/3.0/

// An implementation of a sorting algorithm. 
// An array is given in R14 and R15, where R14 contains the start address of the 
// array, and R15 contains the length of the array. 
// You are not allowed to change R14, R15.
// The program should sort the array in-place and in descending order - 
// the largest number at the head of the array.
// You can assume that each array value x is between -16384 < x < 16384.
// You can assume that the address in R14 is at least >= 2048, and that 
// R14 + R15 <= 16383. 
// No other assumptions can be made about the length of the array.
// You can implement any sorting algorithm as long as its runtime complexity is 
// at most C*O(N^2), like bubble-sort. 


// index = index of outerloop, R1 = temp to switch, inner = index of the inner loop

@R15
D=M
@index
M=D-1
(OUTLOOP)
@R14
D=M
@inner
M=D
(INLOOP)
@inner
A=M
D=M
A=A+1
D=D-M  //D belong to [i] and M to [i+1] --> if D-M <= 0 so NOT switch
@NOTSWITCH
D;JGE
//switch
@inner
A=M
D=M
@temp
M=D
@inner
A=M+1
D=M
A=A-1
M=D
@temp
D=M
@inner
A=M+1
M=D
(NOTSWITCH)
@inner
M=M+1
@R14
D=M
@R15
D=D+M //last reg
@inner
D=M-D //if A-D >= 0 then exit INLOOP
@ENDINL
D+1;JGE
@INLOOP
0;JMP
(ENDINL)
@index
M=M-1
D=M
@BEFEND
D;JLE
@OUTLOOP
0;JMP
(BEFEND)
@index
M=0
@temp
M=0
@inner
M=0
(END)
@END
0;JMP
