# Tokens &amp; Operators

<primary-label ref="header-label"/>

<secondary-label ref="doc-complete"/>

## Tokens

<secondary-label ref="doc-sect-complete"/>

<secondary-label ref="feature-impl"/>

S++ uses a number of tokens, with each being used in a minimal amount of contexts. The following list includes all
tokens used in S++:

| Token name    | Token  | Primary Use                      | Secondary Use                              |
|---------------|--------|----------------------------------|--------------------------------------------|
| `TkNe`        | `!=`   | Binary inequality                |                                            |
| `TkGt`        | `>`    | Binary greater than              |                                            |
| `TkLt`        | `<`    | Binary less than                 |                                            |
| `TkGe`        | `>=`   | Binary greater than or equal to  |                                            |
| `TkLe`        | `<=`   | Binary less than or equal to     |                                            |
| `TkSs`        | `<=> ` | Spaceship 3-way comparison       |                                            |
| `TkAdd`       | `+`    | Binary addition                  | Positive number prefix                     |
| `TkSub`       | `-`    | Binary subtraction               | Negative number prefix                     |
| `TkMul`       | `*`    | Binary multiplication            |                                            |
| `TkDiv`       | `/`    | Binary division                  |                                            |
| `TkMod`       | `%`    | Binary remainder                 |                                            |
| `TkPow`       | `**`   | Binary exponentiation            |                                            |
| `TkMod`       | `%%`   | Binary modulo                    |                                            |
| `TkAddAssign` | `+=`   | Binary addition assignment       |                                            |
| `TkSubAssign` | `-=`   | Binary subtraction assignment    |                                            |
| `TkMulAssign` | `*=`   | Binary multiplication assignment |                                            |
| `TkDivAssign` | `/=`   | Binary division assignment       |                                            |
| `TkModAssign` | `%=`   | Binary remainder assignment      |                                            |
| `TkPowAssign` | `**=`  | Binary exponentiation assignment |                                            |
| `TkModAssign` | `%%=`  | Binary modulo assignment         |                                            |
| `TkParenL`    | `(`    | Func/object/destructure arg list | Parenthesized expression, tuple value/type |
| `TkParenR`    | `)`    | Func/object/destructure arg list | Parenthesized expression, tuple value/type |
| `TkBrackL`    | `[`    | Generic/Where arg list           | Array literal/destructure                  |
| `TkBrackR`    | `]`    | Generic/Where arg list           | Array literal/destructure                  |
| `TkBraceL`    | `{`    | Block start                      |                                            |
| `TkBraceR`    | `}`    | Block end                        |                                            |
| `TkQst`       | `?`    | Propagate error                  | Optional type                              |
| `TkVariadic`  | `..`   | Variadic parameter/arg-skip      | Tuple unpack/fold                          |
| `TkColon`     | `:`    | Type/constraint annotation       |                                            |
| `TkBorrow`    | `&`    | Borrow operation                 |                                            |
| `TkUnion`     | `\|`   | Union type                       |                                            |
| `TkDot`       | `.`    | Runtime member access            | Decimal point                              |
| `TkDblColon`  | `::`   | Static member access             |                                            |
| `TkComma`     | `,`    | Item separator                   |                                            |
| `TkAssign`    | `=`    | Assignment                       |                                            |
| `TkArrow`     | `->`   | Function return type             |                                            |
| `TkAt`        | `@`    | Annotation                       |                                            |

## Operators

<secondary-label ref="doc-sect-complete"/>

<secondary-label ref="feature-impl"/>

A number of the above tokens are used as operators, and are overridable using operator classes, like in Rust. The
following table shows the operator classes, and their operator method that can be overloaded.

| Operator Token | Operator Class        | Operator Method |
|----------------|-----------------------|-----------------|
| `==`           | `std::ops::Eq`        | `eq`            |
| `!=`           | `std::ops::Ne`        | `ne`            |
| `>`            | `std::ops::Gt`        | `gt`            |
| `<`            | `std::ops::Lt`        | `lt`            |
| `>=`           | `std::ops::Ge`        | `ge`            |
| `<=`           | `std::ops::Le`        | `le`            |
| `<=>`          | `std::ops::Cmp`       | `cmp`           |
| `+`            | `std::ops::Add`       | `add`           |
| `-`            | `std::ops::Sub`       | `sub`           |
| `*`            | `std::ops::Mul`       | `mul`           |
| `/`            | `std::ops::Div`       | `div`           |
| `%`            | `std::ops::Rem`       | `rem`           |
| `**`           | `std::ops::Pow`       | `pow`           |
| `%%`           | `std::ops::Mod`       | `mod`           |
| `+=`           | `std::ops::AddAssign` | `add_assign`    |
| `-=`           | `std::ops::SubAssign` | `sub_assign`    |
| `*=`           | `std::ops::MulAssign` | `mul_assign`    |
| `/=`           | `std::ops::DivAssign` | `div_assign`    |
| `%=`           | `std::ops::RemAssign` | `rem_assign`    |
| `**=`          | `std::ops::PowAssign` | `pow_assign`    |
| `%%=`          | `std::ops::ModAssign` | `mod_assign`    |
| `or`           | `std::ops::Ior`       | `ior`           |
| `and`          | `std::ops::And`       | `and`           |
| `not`          | `std::ops::Not`       | `not`           |

### Non-Token Operators

<secondary-label ref="doc-sect-complete"/>

<secondary-label ref="feature-not-impl-yet"/>

There are additional operator classes that don't have specific operator tokens, to maintain the simplicity of the
language. These operators are part of the operators section of the standard library:

| Operator Class     | Operator Method |
|--------------------|-----------------|
| `std::ops::BitIor` | `bitor`         |
| `std::ops::BitAnd` | `bitand`        |
| `std::ops::BitXor` | `bitxor`        |
| `std::ops::BitNot` | `bitnot`        |
| `std::ops::BitShl` | `shl`           |
| `std::ops::BitShr` | `shr`           |
| `std::ops::BitRol` | `rol`           |
| `std::ops::BitRor` | `ror`           |

### Comparison operator RHS

<secondary-label ref="doc-sect-complete"/>

<secondary-label ref="feature-not-impl-yet"/>

Due to the second-class nature of borrows, the `&` operator can only be specified in function calls. This means it
cannot be specified in binary operators. However, for comparisons, the RHS needs to be borrowed, to support chaining
comparison operators. This means the object is automatically borrowed, without the need for the `&` operator.

### Operator Chaining

<secondary-label ref="doc-sect-complete"/>

<secondary-label ref="feature-impl"/>

Comparison operators, except `<=>` and `is`, can be chained together, similar to Python. For example, `1 < 2 < 3` is
automatically expanded to `1 < 2 and 2 < 3`. Because the `Eq` type only borrows its argument, the rhs of the equality
checks don't get consumed, so don't require the `Copy` type to be superimposed.

### Equality

<secondary-label ref="doc-sect-complete"/>

<secondary-label ref="feature-wip"/>

The equality operator between two owned types uses the `Eq::eq` method. An equality between two borrowed types uses
reference equality, checking whether the two borrows are borrowing the same object or not. Because of the law of
exclusivity, a mutable borrow cannot exist simultaneously with any other borrow of the same object, so a comparison
would always return `false`. Therefore, it is not needed to have an `&mut` in a comparison.
