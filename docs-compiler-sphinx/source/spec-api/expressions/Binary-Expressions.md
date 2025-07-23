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

| Operator token | Operation                 | Associated type and method                        | Precedence |
|----------------|---------------------------|---------------------------------------------------|------------|
| `\|=`          | Bitwise OR Assignment     | `std::ops::bit_ior::BitIorAssign::bit_ior_assign` | 0          |
| `^=`           | Bitwise XOR Assignment    | `std::ops::bit_xor::BitXorAssign::bit_xor_assign` | 0          |
| `&=`           | Bitwise AND Assignment    | `std::ops::bit_and::BitAndAssign::bit_and_assign` | 0          |
| `<<=`          | Shift left Assignment     | `std::ops::bit_shl::BitShlAssign::bit_shl_assign` | 0          |
| `>>=`          | Shift right Assignment    | `std::ops::bit_shr::BitShrAssign::bit_shr_assign` | 0          |
| `+=`           | Addition Assignment       | `std::ops::add::AddAssign::add_assign`            | 0          |
| `-=`           | Subtraction Assignment    | `std::ops::sub::SubAssign::sub_assign`            | 0          |
| `*=`           | Multiplication Assignment | `std::ops::mul::MulAssign::mul_assign`            | 0          |
| `/=`           | Division Assignment       | `std::ops::div::DivAssign::div_assign`            | 0          |
| `%=`           | Remainder Assignment      | `std::ops::rem::RemAssign::rem_assign`            | 0          |
| `**=`          | Power Assignment          | `std::ops::pow::PowAssign::pow_assign`            | 0          |
| `or`           | Logical OR                | `std::ops::ior::Ior::ior_`                        | 1          |
| `and`          | Logical AND               | `std::ops::and_::And::and_`                       | 2          |
| `is`           | Type check                | `N/A`                                             | 3          |
| `==`           | Equality                  | `std::ops::eq::Eq::eq`                            | 4          |
| `!=`           | Inequality                | `std::ops::ne::Ne::ne`                            | 4          |
| `<`            | Less than                 | `std::ops::lt::Lt::lt`                            | 4          |
| `>`            | Greater than              | `std::ops::gt::Gt::gt`                            | 4          |
| `<=`           | Less equal                | `std::ops::le::Le::le`                            | 4          |
| `>=`           | Greater equal             | `std::ops::ge::Ge::ge`                            | 4          |
| `\|`           | Bitwise OR                | `std::ops::bit_ior::BitIir::bit_ior`              | 5          |
| `^`            | Bitwise XOR               | `std::ops::bit_xor::BitXor::bit_xor`              | 6          |
| `&`            | Bitwise AND               | `std::ops::bit_and::BitAnd::bit_and`              | 7          |
| `<<`           | Shift left                | `std::ops::bit_shl::BitShl::bit_shl`              | 8          |
| `>>`           | Shift right               | `std::ops::bit_shr::BitShr::bit_shr`              | 8          |
| `+`            | Addition                  | `std::ops::add::Add::add`                         | 9          |
| `-`            | Subtraction               | `std::ops::sub::Sub::sub`                         | 9          |
| `*`            | Multiplication            | `std::ops::mul::Mul::mul`                         | 10         |
| `/`            | Division                  | `std::ops::div::Div::div`                         | 10         |
| `%`            | Remainder                 | `std::ops::rem::Rem::rem`                         | 10         |
| `**`           | Power                     | `std::ops::pow::Pow::pow`                         | 10         |
