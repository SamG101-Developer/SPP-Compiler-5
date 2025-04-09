# Compiled Memory Safety

<primary-label ref="header-label"/>

<secondary-label ref="doc-wip"/>

## Compiler features

As-well as compile-time checks, the S++ compiler also has a number of features to ensure memory safety at runtime. These
include:
- Stack canaries
- Address space layout randomization
- Read-only relocations
- Non-executable areas
- Fortified functions
- Shadow stacks
- Indirect branch tracking
- Digital signatures

## Stack canaries

Stack canaries are a security feature that helps prevent buffer overflows. The compiler creates a random 64-bit value
and stores it before the return address on the stack. If a buffer overflow occurs, the canary will be overwritten, and
the program will terminate.

A major is that string operations can simply include the canary in the string, such that it matches the expected value.
This is because canary values remain constant, and can be viewed in the binary. This is mitigated by the first byte of
the canary being `0x00`, which will terminate any string operations that may be performed on it.

The other issue is that because canary doesn't change, the process can be forked and brute-forced to find the canary
value. Whilst a canary value is randomly determined at runtime, it remains constant for the duration of the process,
including the forked process. This is mitigated by the canary being regenerated on fork.

## Address space layout randomization

S++ uses address space layout randomization (ASLR) to randomize the memory layout of a process. This makes it harder for
an attacker to predict the location of code or data in memory, and therefore harder to exploit.

Not only is the stack, heap and shared libraries ASLR'd, but the executable itself is also randomized. This is done by
using position-independent executables (PIE), which can be loaded at any address in memory.

## Read-only relocations

Using read-only relocations, the S++ compiler can mark certain sections of memory as read-only. This prevents an
attacker from modifying the code or data in these sections, and therefore prevents certain types of attacks. It forces
the GOT to be before the BSS section, eliminating the possibility of overwriting the GOT.

Full RELRO requires all symbols to be resolved at load time. This is suboptimal for large programs, as it can slow down
the loading process.

## Non-executable areas

S++ marks certain areas of the stack as non-executable. This prevents an attacker from executing code on the stack, and
therefore prevents stack-based buffer overflow attacks.

Every single area of the stack that shouldn't be executable is marked as non-executable - as the binary is created, not
only are all locations containing data marked as non-executable, but all non-executing instruction locations are marked
as non-executable too. This requires a shellcode attack to only overwrite executable locations, massively reducing the
attack surface.

## Fortified functions

All functions in S++ are fortified, meaning that they perform additional checks to ensure that they are used correctly.
This includes bounds checking and other safety checks. This helps prevent certain types of buffer overflow attacks, and
bugs in general.

The fortified functions are implemented in the standard library, so the programmer doesn't need to do anything special
to use them. Because the functions are part of compiler known classes, it is impossible to create objects low level
enough that in a non-fortified function, they could be used to exploit the fortified function. All low-level objects are
compiler known and fortified.

## Shadow stacks

Shadow stacks are a security feature that helps prevent return-oriented programming (ROP) attacks. The compiler creates
a separate stack that is used to store return addresses. This stack is protected from modification, as it is marked as
read-only.
