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
ld x4, +h(ZR)
sw x4, +121(ZR)   ; Save symbol to output device(cell #1)

ld x4, +e(ZR)
sw x4, +121(ZR)

ld x4, +l(ZR)
sw x4, +121(ZR)

ld x4, +l(ZR)
sw x4, +121(ZR)

ld x4, +o(ZR)
sw x4, +121(ZR)

ld x4, +space(ZR)
sw x4, +121(ZR)

ld x4, +w(ZR)
sw x4, +121(ZR)

ld x4, +o(ZR)
sw x4, +121(ZR)

ld x4, +r(ZR)
sw x4, +121(ZR)

ld x4, +l(ZR)
sw x4, +121(ZR) 

ld x4, +d(ZR)
sw x4, +121(ZR)

halt