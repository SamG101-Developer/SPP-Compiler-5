# Let Statement

The `let` statement is used to define a variable, introducing a new symbol into the current scope's symbol table. The
`let` statement can introduce an initialized or non-initialized variable. If the variable is non-initialized, then is
must be given a type annotation, as there is no value to infer from. As an initialized variable's value can always be
fully type-inferred, a type annotation is not syntactically allowed, as it introduces redundancy and extra noise.

All variable declarations create [immutable](../language-basics/Terms-Definitions.md#immutable) variables by default.
The section on [](#mutability) explains how to make variables mutable, and how value mutability and borrow mutability
work together.

## Non-initialized Variables

A [non-initialized](../language-basics/Terms-Definitions.md#non-initialized) variable can be defined, but cannot be used
until it has been assigned a value (changing its state
to [fully-initialized](../language-basics/Terms-Definitions.md#fully-initialized)).
The [ownership tracking](../memory/Memory-Model.md#ownership-tracking) part of the
memory model marks the symbol as non-initialized at creation, allowing the compiler to know the symbol is unusable.

Because the compiler requires all types to be known at symbol declaration (there is no deferred or backwards inference),
non-initialized variables must be given a type; this is syntactically required. Syntax:

```S++
let non_initialized_variable: std::string::Str
```

## Initialized Variables

A [fully-initialized](../language-basics/Terms-Definitions.md#fully-initialized) variable can be defined by providing a
value on the right-hand side of the `let` statement. The left-hand side of the `let` statement doesn't have to be a
single identifier; destructuring is supported. The following destructuring techniques are supported:

- Single variable name
- Array destructuring
- Tuple destructuring
- Object destructuring
- Any combination of nesting the above together.

It is not syntactically valid to provide type annotations to initialized variables, because the type can always be
inferred from the value, and the type is never required before the value is analysed (this is unlike global constants,
which require a type annotation as their type may be required knowledge before the value is analysed).

### Single Variable Name

The simplest form of creating an initialized variable is to provide a left-hand side identifier, and a right-hand side
value:

```S++
let new_variable = old_variable
```

This takes the [value](../language-basics/Terms-Definitions.md#values) from inside `old_variable`, and
either [moves or copies](../memory/Memory-Model.md#moving-vs-copying) it into `new_variable`. The variable
`new_variable` is guaranteed to be in the [fully-initialized](../language-basics/Terms-Definitions.md#fully-initialized)
state, because memory guarantees for the right-hand side must be met, ensuring `old_variable` was fully-initialized
before being moved or copied into `new_variable`.

### Array Destructuring

Arrays can be destructured into their element parts, because the array size is known, there will never be a runtime
error by comparing more elements than there are in the array:

```S++
let array_variable = [1, 2]
let [elem1, elem2] = array_variable
# elem1 = 1, elem2 = 2
```

Argument skipping can be used to explicitly ignore unwanted elements:

```S++
let array_variable = [1, 2, 3, 4, 5]
let [elem_head, .., elem_tail] = array_variable
# elem_head = 1, elem_tail = 5
```

Nested is supported too:

```S++
let array_variable = [("a", 1), ("b", 2), ("c", 3), ("d", 4)]
let [(c1, n1), _, (c2, n2), _] = array_variable
# c1 = "a", n1 = 1, c2 = "c", n2 = 3
```

### Tuple destructuring

Tuple destructuring is similar to array destructuring, with the only difference being that `()` tokens are used instead
of `[]`. Because the constructs are similar, the same rules are followed for destructuring:

```S++
let tuple_variable = (1, 2)
let (elem1, elem2) = tuple_variable
# elem1 = 1, elem2 = 2
```

### Object destructuring

Object destructuring works similarly to array and tuple destructuring, but attribute names must be provided too.
Unwanted attributes can be skipped with the `..` token, but the single skip token `_` is not valid in this destructure,
because it makes no sense to include it; attributes are "unordered" ie they are accessed by name so there is no need to
provide individual skips.

The attributes being accessed can be on the type or any other type that the destructed type superimposes. This is the
same as object initializers being able to pass a value for any attribute, including superimposed type's attributes:

```S++
let point = Point(x=0, y=0, z=0)
let Point(x, y, z) = point
# x = 0, y = 0, z = 0
```

Skipping the rest is the same as for tuples, with the exception that the `..` skip cannot be bound to a variable:

```S++
let point = Point(x=0, y=0, z=0)
let Point(z, ..) = point
# z = 0
```

Aliasing attribute names is useful for simplification and to prevent conflicts:

```S++
# x already exists as a variable
let point = Point(x=0, y=0, z=0)
let Point(x as new_x, ..) = point
# new_x = 0
```

Nested destructuring works in the same was as described before:

```S++
let point = Type(a=[1, 2, 3], b=(4, 5, 6), c=Point(x=1, y=2, z=3))
let Type(a=[v1, ..], b=(_, v2, _), c=Point(y as v3, ..)) = point
# v1 = 1, v2 = 5, v3 = 2
```

### Binding to Skipped Values

The `..` token has been shown to mark the rest of the values in a destructure as explicitly skipped, but it can also be
bound to a variable, for arrays and tuples. The usage is:

```S++
let array_variable = [1, 2, 3, 4, 5]
let [first, ..middle, last] = array_variable
# middle = [2, 3, 4]
```

```S++
let tuple_variable = (1, 2, 3, 4, 5)
let (first, ..middle, last) = tuple_variable
# middle = (2, 3, 4)
```

## Mutability

By default, all variables are [immutable](../language-basics/Terms-Definitions.md#immutable). To make a variable
mutable, the `mut` keyword must be added to the `let` statement. Mutability isn't tied to a type in S++, but the symbol
representing the value. For destructuring, individual parts must be marked with `mut`:

```S++
let mut i = 1
let (mut a, b, ..) = (1, 2, 3, 4, 5)
let Point(mut x, y, z) = Point(x=1, y=2, z=3)
```

For function parameters, the `let` is implicit (before the parameter name), so following consistency for the `mut`
keyword, it also comes before the parameter name, to mark it as mutable:

```S++
fun function(mut a: std::string::String, Point(mut x, ..): Point) -> std::void::Void {
    ...
}
```
