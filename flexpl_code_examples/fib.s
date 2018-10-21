.section .data
                               
.section .text                 

.globl _start

_start:

#pushl $2                      

pushl $9                      

  
call fib                       

addl $4, %esp
  
movl %eax, %ebx
movl $1, %eax
  
int $0x80

.type fib, @function
fib:

pushl %ebp
movl %esp, %ebp

movl 8(%ebp), %eax
movl $0,%ebx
cmpl %eax, %ebx
jne exit_label_0
movl $0,%eax
movl  %eax,  %eax
jmp else_exit_label_0
exit_label_0:
movl 8(%ebp), %ebx
movl $1,%ecx
cmpl %ebx, %ecx
jne exit_label_1
movl $1,%eax
movl  %eax,  %eax
jmp else_exit_label_1
exit_label_1:
movl 8(%ebp), %ebx
movl $1,%ecx
subl %ecx, %ebx
movl %ebx, %ecx
pushl %ebx
call fib
addl $4, %esp
movl 8(%ebp), %ebx
movl  %ebx,  %eax
movl 8(%ebp), %ecx
movl $2,%edx
subl %edx, %ecx
movl %ecx, %edx
pushl %ecx
call fib
addl $4, %esp
movl 8(%ebp), %ecx
movl  %ecx,  %eax
addl %ebx, %ecx
movl %ecx, %ebx
movl  %ebx,  %eax
else_exit_label_1:
else_exit_label_0:
movl %eax, %ebx
movl %ebp, %esp
popl %ebp
ret
