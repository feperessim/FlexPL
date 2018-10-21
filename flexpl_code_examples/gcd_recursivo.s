.section .data
                               
.section .text                 

.globl _start

_start:

pushl $49

pushl $84
  
call gcd_recursivo                       

addl $4, %esp

movl $0, %edx
movl %eax, %ebx
movl $1, %eax
  
int $0x80

.type gcd_recursivo, @function
gcd_recursivo:

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
movl -4(%ebp), %ebx
movl $0,%ecx
cmpl %ebx, %ecx
je exit_label_0
movl -4(%ebp), %eax
pushl %eax
movl 12(%ebp), %ebx
pushl %ebx
call gcd_recursivo
addl $8, %esp
movl 8(%ebp), %ebx
movl  %eax, %ebx
jmp else_exit_label_0
exit_label_0:
movl 12(%ebp), %ecx
movl  %ecx,  %eax
else_exit_label_0:
movl %eax, %ebx
movl %ebp, %esp
popl %ebp
ret
