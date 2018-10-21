.section .data
                               
.section .text                 

.globl _start

_start:

pushl $8
pushl $2                      

  
call power                    

addl $4, %esp
  
movl %eax, %ebx
movl $1, %eax
  
int $0x80

.type power, @function
power:

pushl %ebp
movl %esp, %ebp

subl $4, %esp
movl $1,%eax
movl %eax,-4(%ebp)
subl $4, %esp
movl $0,%eax
movl %eax,-8(%ebp)
start_loop_0:
movl -8(%ebp), %eax
movl 12(%ebp), %ebx
cmpl %ebx, %eax
jge exit_label_0
movl -4(%ebp), %eax
movl 8(%ebp), %ebx
imull %eax, %ebx
movl %ebx, %eax
movl %eax, -4(%ebp)
movl -8(%ebp), %ebx
movl $1,%ecx
addl %ebx, %ecx
movl %ecx, %ebx
movl %ebx, -8(%ebp)
jmp start_loop_0
exit_label_0:
movl -4(%ebp), %ecx
movl $1,%edx
subl %edx, %ecx
movl %ecx, %edx
movl  %ecx,  %eax
movl %eax, %ebx
movl %ebp, %esp
popl %ebp
ret
