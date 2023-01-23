section .text
_start:
ld x4, +120(ZR)   ; Load symbol from input device(cell #0)
sw x4, +121(ZR)   ; Save symbol to output device(cell #1)
halt