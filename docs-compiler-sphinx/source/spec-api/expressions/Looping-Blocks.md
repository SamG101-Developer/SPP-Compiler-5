# Looping Blocks

S++ looping blocks can be either an iteration-based loop or a conditional loop. Both use the `loop` keyword, but
iteration loops require the `in` keyword to denote the generator that will be iterated over.

## Conditional Loop

A conditional loop is the same as a traditional `while` loop. It requires a boolean condition that is evaluated every
iteration, with an optional `else` block for if the condition is `false` on the initial iteration.

```S++
loop some_boolean_condition() {
    ...
}
```

The optional `else` block is added to the end of the `loop` block. The code inside the `loop` and `else` blocks will
never both be executed; they are mutually exclusive.

```
loop some_boolean_condition() {
    ...
}
else {
    ...
}
```

## Iteration Loop

An iteration loop is syntactic sugar for easier use of generators. The following shows the transformation from an
iteration based loop to a boolean loop:

```
loop i in some_generator() {
    ...
}
```

The convention of the iteration variable, in this example `i`, is determined off of the iterator. The only values that
can be on the right hand side of the `in` keyword are expressions whose inferred type superimposes the `Gen` type.
Because of the special check that only 1 `Gen` type is ever superimposed on a type, the generated type is immediately
inferrable.

For example, the `std::vector::Vec[T]` type superimposes:

- `std::iterator::IterMov[T]`
- `std::iterator::IterMut[T]`
- `std::iterator::IterRef[T]`

Each of these types contain method that respectively return (and superimpose):

- `std::iterator::Iterator[T] -> std::generator::Gen[T]`
- `std::iterator::Iterator[&mut T] -> std::generator::Gen[&mut T]`
- `std::iterator::Iterator[&T] -> std::generator::Gen[&T]`

This allows the selection of the iterator's convention based on the iteration method chosen. For example, using
`loop x in vector.iter_mut()` means that `x` will be the `&mut T` type.

Note that iteration syntax using `loop-in` requires the `Gen` type to use `Send=Void`, so that the `resume` method
doesn't require an argument.
