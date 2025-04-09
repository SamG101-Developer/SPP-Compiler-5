# Terms &amp; Definitions

<primary-label ref="header-label"/>

<secondary-label ref="doc-wip"/>

## Definitions

**Variables**: A variable is a named memory location that stores a value. The variable always has a type associated with
it, which is a fixed size, determined by the cumulative size of its attributes. It serves as a reference point for
accessing, modifying or performing operations on the data att hat location. A variable stores a value.

**Values**: A value is the data that is stored in a variable. Values can represent entities such as numbers, booleans,
or more complex structures, such as vectors. Values can be moved, copied, and borrowed. Note that whilst a value can be
_borrowed_, its associated variable is said to be _borrowed from_, where it lends its value to another variable, but
retains ownership of the value.

**Owned values**: An owned value is a value that exists in the current scope as in a non-borrowed state. The variable it
is tied to explicitly owns the value. An owned value was either created in, or moved into, the variable that contains it
in the current context, and is not borrowed from another variable.

**Borrowed value**: A borrowed value is a value borrowed from another variable. The owned value is accessed through a
guaranteed valid reference, allowing temporary usage of memory managed by another variable. Borrowing enables access to
a value without transferring ownership, facilitating shared or exclusive usage under controlled conditions. Borrowed
values will always be valid, and cannot outlive the lifetime of the owned value that is being borrowed.

**Move**: A "move" operation is a memory-management operation that transfers the value from one variable into another
variable. After the move, the original variable no longer retains access to the value, and any attempt to use the
variable results in a compile-time memory error. Typically, a move operation will occur when passing a value into a
function, returning from a function, or assigning a value to a variable.

**Partial Move**: A "partial move" operation is where ownership of a subset of an owned value is transferred to another
variable, such as a field of an object. The remaining value is now in a partially-moved state, and its variable
considered partially initialized. Partially initialized variables conform to strict memory rules, similar to that of
non-initialized variables.

{#fully-initialized}
**Fully initialized**: A fully initialized variable is a variable whose value doesn't contain any partial moves. The
entire section of memory allocated for the variable contains initialized bytes, and the variable is considered fully
initialized.

{#partially-initialized}
**Partially initialized**: A variable is partially initialized if its value has been partially moved. This means that
whilst the entire part of memory for the size of the variable's type is allocated, a subset of it contains no bytes,
where some fields have been moved from. These empty sections are non-initialized memory, but as the collective section
of memory representing the entire variable now contains a mix of initialized and non-initialized bytes, the variable is
considered partially initialized.

{#non-initialized}
**Non-initialized**: A non-initialized variable is a variable that has either been defined without a value, or has been
moved from. Therefore, all the bytes in the memory allocated for the variable are non-initialized, and the variable is
considered non-initialized. However, a partially-initialized variable that has had all its fields moved from is still
considered partially-initialized, because the rules of memory management are slightly different.
