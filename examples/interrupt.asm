section .text
_start:
addi mepc, PC, 0 
addi PC, mtvec, 0 

ld DR, +120(ZR) ; Read new word

addi PC, mepc, 0
