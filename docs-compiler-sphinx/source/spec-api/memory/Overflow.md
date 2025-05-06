# Overflow

The areas that "overflow" might occur are:

- [Iteration/slicing/indexing](#iterationslicingindexing)
- [Numeric arithmetic](#numeric-arithmetic)

## Iteration/Slicing/Indexing

All iteration, slicing and indexing operations are checked at runtime to ensure that they do not overflow. This means
that any attempt to iterate over a collection that is empty, or to slice/index an array that is out of bounds, will
result in the program returning an exception into the `Ret[T, E]` type.

## Numeric Arithmetic

All numeric types have the full suite of operator method superimposed on them, only for the matching type. For example,
`I8 + I8` is fine, but `I8 + U8` or `I8 + I16` will not work. All these methods also return the same type as the
operation. For example, `I8 + I8` will return an `I8`. This enforces explicit numeric type usage with no implicit
conversion.

Overflows will typically occur from either initialization of a variable with a value > the maximum value of the type, or
from manipulation of the number via a mathematical operation. The initialization problem is solved by using compile time
checking on literals, and defining all "conversion" operators to return `Ret` types.

The next issue is doing something like `255_u8 + 1_u8`, which will overflow. The `Ret` type is not viable for all
operations, as this would add too much overhead to simple functions. Instead, the corresponding "infinity" value for the
type is returned. For example, `255_u8 + 1_u8` will return `U8::MAX`, which is `255_u8`. This will cause a panic, and
then the associated operator can be replaced with `checked_add` etc.
