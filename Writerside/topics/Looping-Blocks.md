# Looping Blocks

<primary-label ref="header-label"/>

<secondary-label ref="doc-complete"/>

S++ looping blocks can be either an iteration-based loop or a conditional loop. Both use the `loop` keyword, but
iteration loops require the `in` keyword to denote the generator that will be iterated over.

## Conditional Loop

<secondary-label ref="doc-sect-complete"/>

<secondary-label ref="feature-impl"/>

A conditional loop is the same as a traditional `while` loop. It requires a boolean condition that is evaluated every
iteration, with an optional `else` block for if the condition is `false` on the initial iteration.

```
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

<secondary-label ref="doc-sect-complete"/>

<secondary-label ref="feature-wip"/>

An iteration loop is syntactic sugar for easier use of generators. The following shows the transformation from an
iteration based loop to a boolean loop:

```
loop i in some_generator() {
    ...
}
```

```
loop some_generator().step() is T {
    # The compiler will create the "i" variable
    ...
}
```

The convention of the iteration variable, in this example `i`, is determined off of the iterator. In the simplest terms,
either `GenMov`, `GenMut` or `GenMut` are the coroutine return types; for a coroutine that returns `GenMut[Str]`, the
iterating type will be `&mut Str`.

Note that iteration syntax using `loop-in` requires the `Gen` type to use `Send=Void`, so that the `step` method doesn't
require an argument.
