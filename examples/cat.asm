section .text
_start:
ld AC, +120(ZR)   ; Load symbol from input device(cell #0)
sw AC, +121(ZR)   ; Save symbol to output device(cell #1)
halt