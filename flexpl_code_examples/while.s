.section .data

.section .text

.globl _start

_start:


pushl $5


call fib

addl $4, %esp

movl %eax, %ebx
movl $1, %eax

int $0x80

.type fib, @function
fib:

pushl %ebp
movl %esp, %ebp

subl $4, %esp
movl $10,%eax
movl %eax,-4(%ebp)
subl $4, %esp
movl $0,%eax
movl %eax,-8(%ebp)
subl $4, %esp
movl $0,%eax
movl %eax,-12(%ebp)
start_loop_0:
movl -8(%ebp), %eax
movl -4(%ebp), %ebx
cmpl %ebx, %eax
jge exit_label_0
movl -8(%ebp), %eax
movl $1,%ebx
addl %eax, %ebx
movl %ebx, %eax
movl %eax, -8(%ebp)
movl -12(%ebp), %ebx
movl $10,%ecx
addl %ebx, %ecx
movl %ecx, %ebx
movl %ebx, -12(%ebp)
jmp start_loop_0
exit_label_0:
movl -12(%ebp), %ecx
movl  %ecx,  %eax
movl %eax, %ebx
movl %ebp, %esp
popl %ebp
ret

