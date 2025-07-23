# Keywords &amp; Identifiers

## Keywords

S++ uses a small set of keywords, to maintain simplicity. The keywords are not context dependant, and can therefore not
be used as identifiers in non-keyword contexts. This makes the language easier to learn and understand, and to make the
code more readable.

Most of the keywords are constrained to one use. This means that they are only seen in one context, and are not reused
in other contexts.

Annotations are the same as Rust's annotations, or C++ attributes. They are used to edit attributes of the AST nodes,
but don't introduce ASTs.

### Keywords List

- `cls`: define a class (state only)
- `sup`: define a superimposition
- `ext`: extend a superimposition
- `fun`: define a function (subroutine)
- `cor`: define a coroutine
- `use`: define a namespace reduction
- `type`: define a type alias
- `cmp`: define a compile-time constant of generic
- `let`: define a variable
- `mut`: mark a variable or borrow as mutable
- `case`: introduce a condition branch
- `else`: introduce an else block for branching or looping
- `loop`: introduce a loop
- `with`: introduce a context block
- `skip`: skip the current iteration of a loop
- `exit`: exit a loop
- `iter`: inspect a generated value
- `ret`: return a value from a function
- `gen`: yield a value from a coroutine
- `res`: advance a generator
- `async` <format color="yellow">?</format>: call a function asynchronously
- `where` <format color="yellow">?</format>: introduce type constraints on a generic
- `is`: introduce a type check & potential destructure
- `in`: used with `loop` for iteration based loops
- `of`: use patterns in a `case` expression
- `true`: boolean literal for true
- `false`: boolean literal for false
- `self`: reference to the current instance
- `Self`: reference to the type of the current instance
- `and`: logical and binary operator
- `or`: logical or binary operator
- `not`: logical not postfix operator
- `caps`: introduce captures for lambda functions

### Annotations List

- `@virtual_method`: mark a method as virtual
- `@abstract_method`: mark a method as abstract
- `@public`: mark a symbol as public
- `@protected`: mark a symbol as protected
- `@private`: mark a symbol as private
- `@cold`: mark a function as cold
- `@hot`: mark a function as hot
- `@inline`: prefer to inline a function
- `@alwaysinline`: always inline a function

####  Future
- `@noinline`: don't inline a function
- `@friend`: define a friend for the symbol
- `@deprecated/@obselete`: mark deprecation/obsolete
- `@likely/@unlikely/@fallthrough`: conditionals
- `@unroll/@allow_infinite`: loops
