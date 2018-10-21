.section .data

.section .text

.globl _start

_start:


#pushl $5


call odd_sum

	
addl $4, %esp

movl %eax, %ebx
movl $1, %eax

int $0x80


.type odd_sum, @function
odd_sum:

pushl %ebp
movl %esp, %ebp

subl $4, %esp
movl $0,%eax
movl %eax,-4(%ebp)
subl $4, %esp
movl $1,%eax
movl %eax,-8(%ebp)
start_loop_0:
movl -8(%ebp), %eax
movl $10,%ebx
cmpl %ebx, %eax
jge exit_label_0
movl -8(%ebp), %eax
movl $2,%ebx
movl %eax, %eax
movl %ebx, %ebx
movl $0, %edx
idivl %ebx
movl $0,%ebx
cmpl %edx, %ebx
je exit_label_1
movl -4(%ebp), %eax
movl -8(%ebp), %ebx
addl %eax, %ebx
movl %ebx, %eax
movl %eax, -4(%ebp)
exit_label_1:
movl -8(%ebp), %ebx
movl $1,%ecx
addl %ebx, %ecx
movl %ecx, %ebx
movl %ebx, -8(%ebp)
movl -8(%ebp), %ecx
movl $1,%edx
addl %ecx, %edx
movl %edx, %ecx
movl %ecx, -8(%ebp)
jmp start_loop_0
exit_label_0:
movl -4(%ebp), %eax
movl  %eax,  %eax
movl %eax, %ebx
movl %ebp, %esp
popl %ebp
ret
