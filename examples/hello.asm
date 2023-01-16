section .data
h: 'h'
e: 'e'
l: 'l'
o: 'o'
space: ' '
w: 'w'
r: 'r'
d: 'd'

section .text
_start:
ld AC, h
sw AC, +1(ZR)   ; Save symbol to output device(cell #1)

ld AC, e
sw AC, +1(ZR)

ld AC, l
sw AC, +1(ZR)

ld AC, l
sw AC, +1(ZR)

ld AC, o
sw AC, +1(ZR)

ld AC, space
sw AC, +1(ZR)

ld AC, w
sw AC, +1(ZR)

ld AC, o
sw AC, +1(ZR)

ld AC, r
sw AC, +1(ZR)

ld AC, l
sw AC, +1(ZR) 

ld AC, d
sw AC, +1(ZR)

halt