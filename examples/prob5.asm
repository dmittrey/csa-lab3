section .text
_start:
mov AC, +0(ZR)
mov DR, +1(ZR)

increment:
addi AC, AC, 1

rem x4, AC, DR ; %1
addi DR, DR, 1
bne ZR, x4, increment

rem x4, AC, DR ; %1
addi DR, DR, 1
bne ZR, x4, increment

rem x4, AC, DR ; %1
addi DR, DR, 1
bne ZR, x4, increment

rem x4, AC, DR ; %1
addi DR, DR, 1
bne ZR, x4, increment

rem x4, AC, DR ; %1
addi DR, DR, 1
bne ZR, x4, increment

rem x4, AC, DR ; %1
addi DR, DR, 1
bne ZR, x4, increment

rem x4, AC, DR ; %1
addi DR, DR, 1
bne ZR, x4, increment

rem x4, AC, DR ; %1
addi DR, DR, 1
bne ZR, x4, increment

rem x4, AC, DR ; %1
addi DR, DR, 1
bne ZR, x4, increment

rem x4, AC, DR ; %1
addi DR, DR, 1
bne ZR, x4, increment

rem x4, AC, DR ; %1
addi DR, DR, 1
bne ZR, x4, increment

rem x4, AC, DR ; %1
addi DR, DR, 1
bne ZR, x4, increment

rem x4, AC, DR ; %1
addi DR, DR, 1
bne ZR, x4, increment

rem x4, AC, DR ; %1
addi DR, DR, 1
bne ZR, x4, increment

rem x4, AC, DR ; %1
addi DR, DR, 1
bne ZR, x4, increment

rem x4, AC, DR ; %1
addi DR, DR, 1
bne ZR, x4, increment

rem x4, AC, DR ; %1
addi DR, DR, 1
bne ZR, x4, increment

rem x4, AC, DR ; %1
addi DR, DR, 1
bne ZR, x4, increment

rem x4, AC, DR ; %1
addi DR, DR, 1
bne ZR, x4, increment

rem x4, AC, DR ; %20
bne ZR, x4, increment

sw AC, +1(ZR)   ; Save symbol to output device(cell #1)

halt