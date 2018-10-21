.section .data

.section .text

.globl _start

_start:


pushl $5


call fat

addl $4, %esp

movl %eax, %ebx
movl $1, %eax

int $0x80


.type fat, @function
fat:

pushl %ebp
movl %esp, %ebp

subl $4, %esp
movl $1,%eax
movl %eax,-4(%ebp)
start_loop_0:
movl 8(%ebp), %eax
movl $0,%ebx
cmpl %ebx, %eax
jle exit_label_0
movl -4(%ebp), %eax
movl 8(%ebp), %ebx
imull %eax, %ebx
movl %ebx, %eax
movl %eax, -4(%ebp)
movl 8(%ebp), %ebx
movl $1,%ecx
subl %ecx, %ebx
movl %ebx, %ecx
movl %ebx, 8(%ebp)
jmp start_loop_0
exit_label_0:
movl -4(%ebp), %ecx
movl  %ecx,  %eax
movl %eax, %ebx
movl %ebp, %esp
popl %ebp
ret

