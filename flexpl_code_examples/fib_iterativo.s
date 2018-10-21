.section .data
                               
.section .text                 

.globl _start

_start:

#pushl $2                      

pushl $10
  
call fib_iterativo                       

addl $4, %esp
  
movl %eax, %ebx
movl $1, %eax
  
int $0x80

fib_iterativo:

pushl %ebp
movl %esp, %ebp

subl $4, %esp
movl $0,%eax
movl %eax,-4(%ebp)
subl $4, %esp
movl $1,%eax
movl %eax,-8(%ebp)
movl 8(%ebp), %eax
movl $2,%ebx
movl %eax, %eax
movl %ebx, %ebx
movl $0, %edx
idivl %ebx
movl %eax, 8(%ebp)
start_loop_0:
movl 8(%ebp), %ebx
movl $0,%ecx
cmpl %ecx, %ebx
jle exit_label_0
movl -4(%ebp), %eax
movl -8(%ebp), %ebx
addl %eax, %ebx
movl %ebx, %eax
movl %eax, -4(%ebp)
movl -8(%ebp), %ebx
movl -4(%ebp), %ecx
addl %ebx, %ecx
movl %ecx, %ebx
movl %ebx, -8(%ebp)
movl 8(%ebp), %ecx
movl $1,%edx
subl %edx, %ecx
movl %ecx, %edx
movl %ecx, 8(%ebp)
jmp start_loop_0
exit_label_0:
movl -4(%ebp), %eax
movl  %eax,  %eax
movl %eax, %ebx
movl %ebp, %esp
popl %ebp
ret
