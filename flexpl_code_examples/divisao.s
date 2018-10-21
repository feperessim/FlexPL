.section .data
                               
.section .text                 

.globl _start

_start:

 
call division

addl $4, %esp
  
movl %eax, %ebx
movl $1, %eax
  
int $0x80

.type division, @function
division:

pushl %ebp
movl %esp, %ebp

subl $4, %esp
movl $2,%eax
movl %eax,-4(%ebp)
subl $4, %esp
movl $10,%eax
movl %eax,-8(%ebp)
subl $4, %esp
movl $10,%eax
movl $2,%ebx
movl %eax, %eax
movl %ebx, %ebx
idivl %ebx
movl %eax,-12(%ebp)
movl -12(%ebp), %eax
movl  %eax,  %eax
movl %eax, %ebx
movl %ebp, %esp
popl %ebp
ret
