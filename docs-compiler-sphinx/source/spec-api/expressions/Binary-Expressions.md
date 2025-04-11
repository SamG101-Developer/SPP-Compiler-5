# Binary Expressions

## Binary Expressions

Binary expressions are expressions that operate on two operands. Each operator has an associated `std::ops::XXX` class,
where the `Rhs` and `Out` types are specialized for the left-hand-side type. For example,
`std::ops::add::Add[Rhs=std::string::Str, Out=std::string::Str`] is implemented for the `std::string::Str` type:

```S++
sup std::Str ext std::ops::Add[Rhs=std::Str, Out=std::Str] {
    fun add(self, rhs: std::Str) -> std::Str {
        ...
    }
}
```

The only special binary operator that doesn't have an associated `std::ops::XXX` class is the `is` operator. The
right-hand-side isn't an expression, but a local variable declaration pattern. For example,
`case optional_type is std::option::Some(value) { ... }`.

## Operator Precedence

The following table shows the precedence of the binary operators, from highest to lowest:

| Operator token | Operation      | Associated type and method  | Precedence |
|----------------|----------------|-----------------------------|------------|
| `or`           | Logical OR     | `std::ops::ior::Ior::ior_`  | 1          |
| `and`          | Logical AND    | `std::ops::and_::And::and_` | 2          |
| `is`           | Type check     | `N/A`                       | 3          |
| `==`           | Equality       | `std::ops::eq::Eq::eq`      | 4          |
| `!=`           | Inequality     | `std::ops::ne::Ne::ne`      | 4          |
| `<`            | Less than      | `std::ops::lt::Lt::lt`      | 4          |
| `>`            | Greater than   | `std::ops::gt::Gt::gt`      | 4          |
| `<=`           | Less equal     | `std::ops::le::Le::le`      | 4          |
| `>=`           | Greater equal  | `std::ops::ge::Ge::ge`      | 4          |
| `+`            | Addition       | `std::ops::add::Add::add`   | 5          |
| `-`            | Subtraction    | `std::ops::sub::Sub::sub`   | 5          |
| `*`            | Multiplication | `std::ops::mul::Mul::mul`   | 6          |
| `/`            | Division       | `std::ops::div::Div::div`   | 6          |
| `%`            | Remainder      | `std::ops::rem::Rem::rem`   | 6          |
| `**`           | Exponent       | `std::ops::pow::Pow::pow`   | 6          |
| `%%`           | Modulo         | `std::ops::mod::Mod::mod`   | 6          |

There are several operator classes that don't have associated tokens:

| Candidate token | Operation    | Associated type and method          | Precedence |
|-----------------|--------------|-------------------------------------|------------|
| `\|`            | Bitwise OR   | `std::ops::bit_or::BitOr::bitor`    | 5.2        |
| `^`             | Bitwise XOR  | `std::ops::bit_xor::BitXor::bitxor` | 5.4        |
| `&`             | Bitwise AND  | `std::ops::bit_and::BitAnd::bitand` | 5.6        |
| `<<`            | Shift left   | `std::ops::bit_shl::Shl::shl`       | 5.8        |
| `>>`            | Shift right  | `std::ops::bit_shr::Shr::shr`       | 5.8        |
| `<<<`           | Rotate left  | `std::ops::bit_rol::Rol::rol`       | 5.8        |
| `>>>`           | Rotate right | `std::ops::bit_ror::Ror::ror`       | 5.8        |

