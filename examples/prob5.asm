section .text
_start:
addi AC, ZR, 0
addi DR, ZR, 1

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

sw AC, +121(ZR)   ; Save symbol to output device(cell #1)

halt