# Binary Expressions

<primary-label ref="header-label"/>

<secondary-label ref="doc-complete"/>

## Binary Expressions

Binary expressions are expressions that operate on two operands. Each operator has an associated `std::ops::XXX` class,
where the `Rhs` and `Out` types are specialized for the left-hand-side type. For example,
`std::ops::Add[Rhs=Str, Out=Str`] is implemented for the `Str` type:

```
sup std::Str ext std::ops::Add[Rhs=std::Str, Out=std::Str] {
    fun add(self, rhs: std::Str) -> std::Str {
        ...
    }
}
```

Because there is no way to take references for binary expressions (where-as `"Hello".add(&"World")` is syntactically
valid), the `rhs` parameter always consumes the right-hand-side value. This can be avoided with the `.clone()` method,
or a `Copy`-enabled type.

The only special binary operator that doesn't have an associated `std::ops::XXX` class is the `is` operator. The
right-hand-side isn't an expression, but a local variable declaration pattern. For example,
`case optional_type is Some(value) { ... }`.

## Operator Precedence

The following table shows the precedence of the binary operators, from highest to lowest:

| Operator token | Operation      | Associated type and method | Precedence |
|----------------|----------------|----------------------------|------------|
| `or`           | Logical OR     | `std::ops::IOr::ior_`      | 1          |
| `and`          | Logical AND    | `std::ops::And::and_`      | 2          |
| `is`           | Type check     | `N/A`                      | 3          |
| `==`           | Equality       | `std::ops::Eq::eq`         | 4          |
| `!=`           | Inequality     | `std::ops::Ne::ne`         | 4          |
| `<`            | Less than      | `std::ops::Lt::lt`         | 4          |
| `>`            | Greater than   | `std::ops::Gt::gt`         | 4          |
| `<=`           | Less equal     | `std::ops::Le::le`         | 4          |
| `>=`           | Greater equal  | `std::ops::Ge::ge`         | 4          |
| `+`            | Addition       | `std::ops::Add::add`       | 5          |
| `-`            | Subtraction    | `std::ops::Sub::sub`       | 5          |
| `*`            | Multiplication | `std::ops::Mul::mul`       | 6          |
| `/`            | Division       | `std::ops::Div::div`       | 6          |
| `%`            | Remainder      | `std::ops::Rem::rem`       | 6          |
| `**`           | Exponent       | `std::ops::Pow::pow`       | 6          |
| `%%`           | Modulo         | `std::ops::Mod::mod`       | 6          |

There are several operator classes that don't have associated tokens:

| Candidate token | Operation    | Associated type and method | Precedence |
|-----------------|--------------|----------------------------|------------|
| `\|`            | Bitwise OR   | `std::ops::BitOr::bitor`   | 5.2        |
| `^`             | Bitwise XOR  | `std::ops::BitXor::bitxor` | 5.4        |
| `&`             | Bitwise AND  | `std::ops::BitAnd::bitand` | 5.6        |
| `<<`            | Shift left   | `std::ops::Shl::shl`       | 5.8        |
| `>>`            | Shift right  | `std::ops::Shr::shr`       | 5.8        |
| `<<<`           | Rotate left  | `std::ops::Rol::rol`       | 5.8        |
| `>>>`           | Rotate right | `std::ops::Ror::ror`       | 5.8        |

