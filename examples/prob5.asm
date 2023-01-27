section .text
_start:
addi x4, x0, 1    ; d
addi x5, x0, 2    ; i
addi x6, x0, 20

.prob:
    cmp x5, +0(x6)
    jg .exit
    jmp .nok
.nokexit:
    add x4, x0, x3
    addi x5, x5, 1
    jmp .prob


; uses x1, x2, x3 -> x3 - nok, x2 - nod
.nok:
    add x1, x0, x4
    add x2, x0, x5

    jmp .nod
.nodexit:
    mul x3, x4, x5
    div x3, x3, x2
    jmp .nokexit

.nod:
    .looptop:
        cmp x1, +0(x0)  ; x1 - x, x2 - y
        beq .goback
        cmp x1, +0(x2)
        jg .modulo
        add x3, x0, x1
        add x1, x0, x2
        add x2, x0, x3

    .modulo:
        rem x1, x1, x2
        jmp .looptop

    .goback:
        jmp .nodexit

.exit:
    sw x3, +121(ZR) ; print nok
    sw x2, +121(ZR) ; print nod
    sw x4, +121(ZR) ; print d
    halt

