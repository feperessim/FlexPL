.section .data

.section .text

.globl _start

_start:

#pushl $2

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

movl 8(%ebp), %eax
movl $0,%ebx
cmpl %eax, %ebx
jne exit_label_0
movl $1,%eax
movl  %eax,  %eax
jmp else_exit_label_0
exit_label_0:
movl 8(%ebp), %ebx
movl 8(%ebp), %ecx
movl $1,%edx
subl %edx, %ecx
movl %ecx, %edx
pushl %ecx
call fat
addl $4, %esp
movl 8(%ebp), %ecx
movl  %ecx,  %eax
imull %ebx, %eax
movl %eax, %ebx
movl  %ebx,  %eax
else_exit_label_0:
movl %eax, %ebx
movl %ebp, %esp
popl %ebp
ret

