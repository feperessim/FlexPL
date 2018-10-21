.section .data
                               
.section .text                 

.globl _start

_start:

pushl $49

pushl $84
  
call gcd_iterativo 

addl $4, %esp

movl $0, %edx
movl %eax, %ebx
movl $1, %eax
  
int $0x80


.type gcd_iterativo, @function
gcd_iterativo:

pushl %ebp
movl %esp, %ebp

subl $4, %esp
movl 8(%ebp), %eax
movl 12(%ebp), %ebx
movl %eax, %eax
movl %ebx, %ebx
movl $0, %edx
idivl %ebx
movl %edx, -4(%ebp)
start_loop_0:
movl -4(%ebp), %ebx
movl $0,%ecx
cmpl %ebx, %ecx
je exit_label_0
movl 12(%ebp), %eax
movl %eax, 8(%ebp)
movl -4(%ebp), %ebx
movl %ebx, 12(%ebp)
movl 8(%ebp), %ecx
movl 12(%ebp), %edx
movl %ecx, %eax
movl %edx, %ebx
movl $0, %edx
idivl %ebx
movl %edx, -4(%ebp)
jmp start_loop_0
exit_label_0:
movl 12(%ebp), %edx
movl  %edx,  %eax
movl %eax, %ebx
movl %ebp, %esp
popl %ebp
ret
