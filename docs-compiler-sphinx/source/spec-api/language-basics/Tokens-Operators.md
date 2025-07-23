# Tokens &amp; Operators

## Tokens

S++ uses a number of tokens, with each being used in a minimal amount of contexts. The following list includes all
tokens used in S++:

| Token | Primary Use                           | Secondary Use                              |
|-------|---------------------------------------|--------------------------------------------|
| `==`  | Binary equality                       |                                            |
| `!=`  | Binary inequality                     |                                            |
| `>`   | Binary greater than                   |                                            |
| `<`   | Binary less than                      |                                            |
| `>=`  | Binary greater than or equal to       |                                            |
| `<=`  | Binary less than or equal to          |                                            |
| `+`   | Binary addition                       | Positive number prefix                     |
| `-`   | Binary subtraction                    | Negative number prefix                     |
| `*`   | Binary multiplication                 | Borrow deference                           |
| `/`   | Binary division                       |                                            |
| `%`   | Binary remainder                      |                                            |
| `**`  | Binary exponentiation                 |                                            |
| `\|`  | Binary bitwise OR                     |                                            |
| `&`   | Binary bitwise AND                    | Borrow creation                            |
| `^`   | Binary bitwise XOR                    |                                            |
| `<<`  | Binary bitwise left shift             |                                            |
| `>>`  | Binary bitwise right shift            |                                            |
| `+=`  | Binary addition assignment            |                                            |
| `-=`  | Binary subtraction assignment         |                                            |
| `*=`  | Binary multiplication assignment      |                                            |
| `/=`  | Binary division assignment            |                                            |
| `%=`  | Binary remainder assignment           |                                            |
| `**=` | Binary exponentiation assignment      |                                            |
| `\|=` | Binary bitwise OR assignment          |                                            |
| `&=`  | Binary bitwise AND assignment         |                                            |
| `^=`  | Binary bitwise XOR assignment         |                                            |
| `<<=` | Binary bitwise left shift assignment  |                                            |
| `>>=` | Binary bitwise right shift assignment |                                            |
| `(`   | Func/object/destructure arg list      | Parenthesized expression, tuple value/type |
| `)`   | Func/object/destructure arg list      | Parenthesized expression, tuple value/type |
| `[`   | Generic/Where arg list                | Array literal/destructure                  |
| `]`   | Generic/Where arg list                | Array literal/destructure                  |
| `{`   | Block start                           |                                            |
| `}`   | Block end                             |                                            |
| `?`   | Propagate error                       | Optional type                              |
| `..`  | Variadic marker/tuple ops             | Multi argument skip (& bind)               |
| `:`   | Type/constraint annotation            |                                            |
| `.`   | Runtime member access                 | Decimal point                              |
| `::`  | Static member access                  |                                            |
| `,`   | Item separator                        |                                            |
| `=`   | Assignment                            |                                            |
| `->`  | Function return type                  |                                            |
| `@`   | Annotation                            |                                            |
| `!`   | Fallible generator exception          | Never type                                 |
| `_`   | Optional generator no-value           | Placeholder for unused value               |
| `!!`  | exhausted generator                   |                                            |

## Operators

A number of the above tokens are used as operators, and are overridable using operator classes, like in Rust. The
following table shows the operator classes, and their operator method that can be overloaded.

| Operator Token | Operator Class                           | Operator Method  |
|----------------|------------------------------------------|------------------|
| `==`           | `std::ops::eq::Eq`                       | `eq`             |
| `!=`           | `std::ops::ne::Ne`                       | `ne`             |
| `>`            | `std::ops::gt::Gt`                       | `gt`             |
| `<`            | `std::ops::lt::Lt`                       | `lt`             |
| `>=`           | `std::ops::ge::Ge`                       | `ge`             |
| `<=`           | `std::ops::le::Le`                       | `le`             |
| `+`            | `std::ops::add::Add`                     | `add`            |
| `-`            | `std::ops::sub::Sub`                     | `sub`            |
| `*`            | `std::ops::mul::Mul`                     | `mul`            |
| `/`            | `std::ops::div::Div`                     | `div`            |
| `%`            | `std::ops::rem::Rem`                     | `rem`            |
| `**`           | `std::ops::pow::Pow`                     | `pow`            |
| `\|`           | `std::ops::bit_ior::BitIor`              | `bit_ior`        |
| `&`            | `std::ops::bit_and::BitAnd`              | `bit_and`        |
| `^`            | `std::ops::bit_xor::BitXor`              | `bit_xor`        |
| `<<`           | `std::ops::bit_shl::BitShl`              | `bit_shl`        |
| `>>`           | `std::ops::bit_shr::BitShr`              | `bit_shr`        |
| `+=`           | `std::ops::add_assign::AddAssign`        | `add_assign`     |
| `-=`           | `std::ops::sub_assign::SubAssign`        | `sub_assign`     |
| `*=`           | `std::ops::mul_assign::MulAssign`        | `mul_assign`     |
| `/=`           | `std::ops::div_assign::DivAssign`        | `div_assign`     |
| `%=`           | `std::ops::rem_assign::RemAssign`        | `rem_assign`     |
| `**=`          | `std::ops::pow_assign::PowAssign`        | `pow_assign`     |
| `\|=`          | `std::ops::bit_ior_assign::BitIorAssign` | `bit_ior_assign` |
| `&=`           | `std::ops::bit_and_assign::BitAndAssign` | `bit_and_assign` |
| `^=`           | `std::ops::bit_xor_assign::BitXorAssign` | `bit_xor_assign` |
| `<<=`          | `std::ops::bit_shl_assign::BitShlAssign` | `bit_shl_assign` |
| `>>=`          | `std::ops::bit_shr_assign::BitShrAssign` | `bit_shr_assign` |
| `or`           | `std::ops::ior::Ior`                     | `ior_`           |
| `and`          | `std::ops::and::And`                     | `and_`           |
| `not`          | `std::ops::not::Not`                     | `not`            |

### Non-Token Operators

There are additional operator classes that don't have specific operator tokens, to maintain the simplicity of the
language. These operators are part of the operators section of the standard library:

| Operator Class              | Operator Method | Usage           |
|-----------------------------|-----------------|-----------------|
| `std::ops::neg::Neg`        | `neg`           | `val.neg()`     |
| `std::ops::not::Not`        | `not_`          | `val.not`       |
| `std::ops::bit_not::BitNot` | `bit_not`       | `val.bit_not()` |

### Comparison operator RHS

Due to the second-class nature of borrows, the `&` operator can only be specified in function calls. This means it
cannot be specified in binary operators. However, for comparisons, the RHS needs to be borrowed, to support chaining
comparison operators. This means the object is automatically borrowed, without the need for manually applying the `&`
operator.

### Operator Chaining

Comparison operators, except `is`, can be chained together, similar to Python. For example, `1 < 2 < 3` is automatically
expanded to `1 < 2 and 2 < 3`. Because the `Eq` type only borrows its argument, the rhs of the equality checks don't get
consumed, so don't require the `Copy` type to be superimposed.

### Equality

The equality operator between two owned types uses the `Eq::eq` method. An equality between two borrowed types uses
reference equality, checking whether the two borrows are borrowing the same object or not. Because of the law of
exclusivity, a mutable borrow cannot exist simultaneously with any other borrow of the same object, so a comparison
would always return `false`. Therefore, it is not needed to have an `&mut` in a comparison.
