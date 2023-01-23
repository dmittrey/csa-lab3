section .text
_start:
addi x4, ZR, 20 ; Put 20 in x4

addi x5, ZR, 2  ; Set x2 start to 2
addi x1, ZR, 2  ; Set x1 start to 2

.findprime:
    addi x1, x1, 1  ; Inc x1
    cmp x4, +0(x1)  ; x1 - x4
    jg .findnumber  ; 16
    addi x3, ZR, 2  ; 
    .checkmod:
        rem x2, x1, x3
        beq .findprime
        addi x3, x3, 1
        cmp x3, +0(x1)
        beq .mulstep ; 14
        jmp .findprime
    .mulstep:
            mul x5, x5, x1
            jmp .findprime

.findnumber:
    addi x1, ZR, 0 ;16
    .nextnumber:
        add x1, x1, x5
        addi x3, ZR, 0
    .nextdivider:
        addi x3, x3, 1
        rem x2, x1, x3
        bne .nextnumber   

        cmp x3, +0(x4)
        beq .exit      ;25

        jmp .nextdivider
.exit:
    sw x1, +121(ZR)
    halt
