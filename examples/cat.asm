section .text
_start:
ld AC, +0(ZR)   ; Load symbol from input device(cell #0)
sw AC, +1(ZR)   ; Save symbol to output device(cell #1)
halt