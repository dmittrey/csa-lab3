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
ld AC, +h(ZR)
sw AC, +1(ZR)   ; Save symbol to output device(cell #1)

ld AC, +e(ZR)
sw AC, +1(ZR)

ld AC, +l(ZR)
sw AC, +1(ZR)

ld AC, +l(ZR)
sw AC, +1(ZR)

ld AC, +o(ZR)
sw AC, +1(ZR)

ld AC, +space(ZR)
sw AC, +1(ZR)

ld AC, +w(ZR)
sw AC, +1(ZR)

ld AC, +o(ZR)
sw AC, +1(ZR)

ld AC, +r(ZR)
sw AC, +1(ZR)

ld AC, +l(ZR)
sw AC, +1(ZR) 

ld AC, +d(ZR)
sw AC, +1(ZR)

halt