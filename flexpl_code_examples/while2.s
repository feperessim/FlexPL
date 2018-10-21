.section .data

.section .text

.globl _start

_start:


pushl $5


call test_while

addl $4, %esp

movl %eax, %ebx
movl $1, %eax

int $0x80

.type test_while, @function
test_while:

pushl %ebp
movl %esp, %ebp

subl $4, %esp
movl $2,%eax
movl %eax,-4(%ebp)
subl $4, %esp
movl $6,%eax
movl %eax,-8(%ebp)
subl $4, %esp
movl $1,%eax
movl %eax,-12(%ebp)
subl $4, %esp
movl $0,%eax
movl %eax,-16(%ebp)
start_loop_0:
movl -16(%ebp), %eax
movl -8(%ebp), %ebx
cmpl %ebx, %eax
jge exit_label_0
movl -12(%ebp), %eax
movl -4(%ebp), %ebx
imull %eax, %ebx
movl %ebx, %eax
movl %eax, -12(%ebp)
movl -16(%ebp), %ebx
movl $1,%ecx
addl %ebx, %ecx
movl %ecx, %ebx
movl %ebx, -16(%ebp)
jmp start_loop_0
exit_label_0:
movl -12(%ebp), %ecx
movl  %ecx,  %eax
movl %eax, %ebx
movl %ebp, %esp
popl %ebp
ret

