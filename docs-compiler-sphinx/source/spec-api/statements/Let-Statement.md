# Let Statement

The `let` statement is used to define a variable, introducing a new symbol into the current scope's symbol table. The
`let` statement can introduce an initialized or non-initialized variable. If the variable is non-initialized, then is
must be given a type annotation, as there is no value to infer from. As an initialized variable's value can always be
fully type-inferred, a type annotation is not required, but can be added. This is especially useful for variant types,
to tell the symbol table that a symbol will hold a variant type, even though the value being assigned to it is not a
variant type value, ie `let x: Str or BigInt = "hello world"`.

All variable declarations create [immutable](../language-basics/Terms-Definitions.md#immutable) variables by default.
The section on [](#mutability) explains how to make variables mutable; how mutability works with destructuring; and how
value/borrow mutability work together.

## Non-initialized Variables

A [non-initialized](../language-basics/Terms-Definitions.md#non-initialized) variable can be defined, but cannot be used
until it has been assigned a value (changing its state
to [fully-initialized](../language-basics/Terms-Definitions.md#fully-initialized)).
The [ownership tracking](../memory/Memory-Model.md#ownership-tracking) part of the
memory model marks the symbol as non-initialized at creation, allowing the compiler to know the symbol is unusable.

Because the compiler requires all types to be known at symbol declaration (there is no deferred inference),
non-initialized variables must be given a type; this is syntactically required. Syntax:

```S++
let non_initialized_variable: std::string::Str
```

## Initialized Variables

A [fully-initialized](../language-basics/Terms-Definitions.md#fully-initialized) variable can be defined by providing a
value on the right-hand side of the `let` statement. The left-hand-side of the `let` statement doesn't have to be a
single identifier; destructuring is supported. The following destructuring techniques are supported:

- Single variable name (no destructuring)
- Array destructuring (elements of the array)
- Tuple destructuring (elements of the tuple)
- Object destructuring (attributes of the object)
- Any combination of nesting the above together.

A type annotation can be provided to the `let` statement, but most of the time this isn't required; the value's type can
always be inferred. The only time a type annotation is useful is for variant types; it allows for a composite type to be
placed into a variable whose type is variant:

```S++
let x: Str or BigInt = "hello world".
```

### Single Variable Name

The simplest form of creating an initialized variable is to provide a left-hand0side identifier, and a right-hand-side
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

Nested destructuring works in the same way as described before:

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

The type of the bound variable matches whatever is being destructured; binding to a multi-skip whilst destructuring a
tuple will always create a sub-tuple containing the skipped elements.

## Mutability

By default, all variables are [immutable](../language-basics/Terms-Definitions.md#immutable). To make a variable
mutable, the `mut` keyword must be added to the local variable that has been declared. Mutability isn't tied to a type
in S++, but the symbol representing the value. For destructuring, individual parts (the innermost single identifiers)
must be individually marked with `mut`, because each part of the destructure is a local variable in itself.:

```S++
let mut i = 1
let (mut a, b, ..) = (1, 2, 3, 4, 5)
let [mut x, _, mut y, ..] = [1, 2, 3, 4, 5]
let Point(mut x, y, z) = Point(x=1, y=2, z=3)
```

Function parameters are also local variables. It is valid to define a function signature like:

```S++
fun func(Point(x, y): Point) -> Void { }
```

This allows a `Point` argument to be given to the function and `x` and `y` to be received as the parameters. This means
that the `mut `keyword must also be prepended ot the parameter names being defined. Usually, parameters are single
identifiers, so `mut name: Type` is the common form of defining a mutable parameter. However, destructuring is also
supported, so the `mut` keyword can be used in the same way as with local variables.

### Attributes

The mutability of an attribute is always the same as the mutability of the outermost object that owns it. For example,
`a.b.c.d` is mutable if and only if `a` is mutable. An attribute alone cannot be specifically defined as constant. The
`cmp` statement can be used to define a behavioural constant of a superimposition of a type.

### Value vs Borrow

The mutability of a value doesn't always match the mutability of a borrow. For example, a variable might be a mutable
borrow, but the mutable borrow itself could be immutable, ie whilst the internals of the object can be mutated, the
variable itself cannot be re-assigned to. For more information and detail on the distinction between the two, see the
section on [borrow mutability](../memory/Memory-Model.md#mutable-borrows-vs-mutable-variables).

## Variable Semantics

### Variable Scope

S++ uses strict block-scoping to contain variables and prevent any scope-leak. This means that variables declared inside
a block are only accessible from inside that block, and nowhere else outside it. This is unlike Python, which can access
scope-leaked variables and throws errors if the variable happens to not exist in some context. Using strict scoping
rules provides a clear and predictable scope for variable, and prevents accidental variable shadowing.

Variables from outer blocks can be accessed from inner blocks, and can assign values to them (given they are mutable).
See the section on [variable shadowing](#variable-shadowing) for details on re-declaring variables in a nested scope.

### Variable Lifetime

The lifetime of a variable is tied to its scope (and therefore its block). The only way to extend the lifetime of a
variable is:

1. Return it as a value into the outer frame
2. Attach it as an attribute to the object being returned to the outer frame.
3. Attach it as an attribute to a mutable borrow that has been passed into the function as a parameter.

The [memory model](../memory/Memory-Model.md) ensures that lifetime errors are never possible.

### Variable Redeclaration

Variables can be re-declared in the same scope, with a different type or mutability. This allows for a variable name to
be re-used for a different purpose, or for a transformation to take place that produces a different value type.

```S++
let mut x = 123       # x is a mutable number
let x = Str::from(x)  # x is an immutable string
```

### Variable Shadowing

Variables can be shadowed in an inner scope. This creates a new symbol in the inner scope, which is used, but when
control returns to the outer scope, the original symbol is used again, the value the same as it was before the inner
scope was entered. To modify the outer symbol, assignment without re-declaration must be used:

```S++
fun main() -> std::void::Void {
    let x = 1
    {
        let x = 2
        std::io::print(x)  # prints "2"
    }
    std::io::print(x)  # prints "1"
}
```

```S++
fun main() -> std::void::Void {
    let mut x = 1
    {
        x = 2
        std::io::print(x)  # prints "2"
    }
    std::io::print(x)  # prints "2"
}
```

## Global Constants

See the section on [global constants](./Cmp-Statement) for more.
