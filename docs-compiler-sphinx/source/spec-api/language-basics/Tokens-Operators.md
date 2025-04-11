# Tokens &amp; Operators

## Tokens

S++ uses a number of tokens, with each being used in a minimal amount of contexts. The following list includes all
tokens used in S++:

| Token name    | Token | Primary Use                      | Secondary Use                              |
|---------------|-------|----------------------------------|--------------------------------------------|
| `TkEq`        | `==`  | Binary equality                  |                                            |
| `TkNe`        | `!=`  | Binary inequality                |                                            |
| `TkGt`        | `>`   | Binary greater than              |                                            |
| `TkLt`        | `<`   | Binary less than                 |                                            |
| `TkGe`        | `>=`  | Binary greater than or equal to  |                                            |
| `TkLe`        | `<=`  | Binary less than or equal to     |                                            |
| `TkAdd`       | `+`   | Binary addition                  | Positive number prefix                     |
| `TkSub`       | `-`   | Binary subtraction               | Negative number prefix                     |
| `TkMul`       | `*`   | Binary multiplication            |                                            |
| `TkDiv`       | `/`   | Binary division                  |                                            |
| `TkRem`       | `%`   | Binary remainder                 |                                            |
| `TkPow`       | `**`  | Binary exponentiation            |                                            |
| `TkMod`       | `%%`  | Binary modulo                    |                                            |
| `TkAddAssign` | `+=`  | Binary addition assignment       |                                            |
| `TkSubAssign` | `-=`  | Binary subtraction assignment    |                                            |
| `TkMulAssign` | `*=`  | Binary multiplication assignment |                                            |
| `TkDivAssign` | `/=`  | Binary division assignment       |                                            |
| `TkModAssign` | `%=`  | Binary remainder assignment      |                                            |
| `TkPowAssign` | `**=` | Binary exponentiation assignment |                                            |
| `TkModAssign` | `%%=` | Binary modulo assignment         |                                            |
| `TkParenL`    | `(`   | Func/object/destructure arg list | Parenthesized expression, tuple value/type |
| `TkParenR`    | `)`   | Func/object/destructure arg list | Parenthesized expression, tuple value/type |
| `TkBrackL`    | `[`   | Generic/Where arg list           | Array literal/destructure                  |
| `TkBrackR`    | `]`   | Generic/Where arg list           | Array literal/destructure                  |
| `TkBraceL`    | `{`   | Block start                      |                                            |
| `TkBraceR`    | `}`   | Block end                        |                                            |
| `TkQst`       | `?`   | Propagate error                  | Optional type                              |
| `TkVariadic`  | `..`  | Variadic parameter/arg-skip      | Tuple unpack/fold                          |
| `TkColon`     | `:`   | Type/constraint annotation       |                                            |
| `TkBorrow`    | `&`   | Borrow operation                 |                                            |
| `TkUnion`     | `\|`  | Union type                       |                                            |
| `TkDot`       | `.`   | Runtime member access            | Decimal point                              |
| `TkDblColon`  | `::`  | Static member access             |                                            |
| `TkComma`     | `,`   | Item separator                   |                                            |
| `TkAssign`    | `=`   | Assignment                       |                                            |
| `TkArrow`     | `->`  | Function return type             |                                            |
| `TkAt`        | `@`   | Annotation                       |                                            |

## Operators

A number of the above tokens are used as operators, and are overridable using operator classes, like in Rust. The
following table shows the operator classes, and their operator method that can be overloaded.

| Operator Token | Operator Class                    | Operator Method |
|----------------|-----------------------------------|-----------------|
| `==`           | `std::ops::eq::Eq`                | `eq`            |
| `!=`           | `std::ops::ne::Ne`                | `ne`            |
| `>`            | `std::ops::gt::Gt`                | `gt`            |
| `<`            | `std::ops::lt::Lt`                | `lt`            |
| `>=`           | `std::ops::ge::Ge`                | `ge`            |
| `<=`           | `std::ops::le::Le`                | `le`            |
| `+`            | `std::ops::add::Add`              | `add`           |
| `-`            | `std::ops::sub::Sub`              | `sub`           |
| `*`            | `std::ops::mul::Mul`              | `mul`           |
| `/`            | `std::ops::div::Div`              | `div`           |
| `%`            | `std::ops::rem::Rem`              | `rem`           |
| `**`           | `std::ops::pow::Pow`              | `pow`           |
| `%%`           | `std::ops::mod::Mod`              | `mod`           |
| `+=`           | `std::ops::add_assign::AddAssign` | `add_assign`    |
| `-=`           | `std::ops::sub_assign::SubAssign` | `sub_assign`    |
| `*=`           | `std::ops::mul_assign::MulAssign` | `mul_assign`    |
| `/=`           | `std::ops::div_assign::DivAssign` | `div_assign`    |
| `%=`           | `std::ops::rem_assign::RemAssign` | `rem_assign`    |
| `**=`          | `std::ops::pow_assign::PowAssign` | `pow_assign`    |
| `%%=`          | `std::ops::mod_assign::ModAssign` | `mod_assign`    |
| `or`           | `std::ops::ior::Ior`              | `ior`           |
| `and`          | `std::ops::and::And`              | `and`           |
| `not`          | `std::ops::not::Not`              | `not`           |

### Non-Token Operators

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

Due to the second-class nature of borrows, the `&` operator can only be specified in function calls. This means it
cannot be specified in binary operators. However, for comparisons, the RHS needs to be borrowed, to support chaining
comparison operators. This means the object is automatically borrowed, without the need for the `&` operator.

### Operator Chaining

Comparison operators, except `<=>` and `is`, can be chained together, similar to Python. For example, `1 < 2 < 3` is
automatically expanded to `1 < 2 and 2 < 3`. Because the `Eq` type only borrows its argument, the rhs of the equality
checks don't get consumed, so don't require the `Copy` type to be superimposed.

### Equality

The equality operator between two owned types uses the `Eq::eq` method. An equality between two borrowed types uses
reference equality, checking whether the two borrows are borrowing the same object or not. Because of the law of
exclusivity, a mutable borrow cannot exist simultaneously with any other borrow of the same object, so a comparison
would always return `false`. Therefore, it is not needed to have an `&mut` in a comparison.
