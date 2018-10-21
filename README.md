# FlexPL
FlexPL is a small compiler written in Python3, with the help of PLY the implementation of lex and yacc parsing tools for Python.
The compiler was developed during the second semester of 2017 in a class of Compilers in a Computer Science course.
The sintax of FlexPL is similar to C, some examples can be found at the flexpl_code_examples directory. The compiler generates
assembly code for integer arithmetic. 

Usage: 

1. At line 9 in flexpl.py file give the file location to be compiled.
2. In the terminal navigate to the directory of flexpl.py and execute the command: python3 flexpl.
3. If everything goes fine, some assembly code was generated. Create a new file with '.s' extension 
copy and paste the following code:

.section .data

.section .text

.globl _start

_start:

pushl $value

call your_function_name_here

addl $4, %esp
  
movl %eax, %ebx
movl $1, %eax

int $0x80

4. Copy and paste generated by the compiler, after the code above.
You need to add pushl $value or remove it as many times as the function parameters you have in the reverse order
of the parameters of your function. And 'value' replaced with the apropriate value for the parameter(s).

5. To finaly compile and link execute the following commands: 

as --32  your_filename_here.s -o your_filename_here.o
ld -melf_i386 your_filename_here.o -o your_filename_here

6. Finally just run ./your_filename_here to execute the compiled program.

7. Execute the command 'echo $?' to see the returned result from the program.