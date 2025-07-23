# Cmp Statement

Constants are compile time variables, and as such, are denoted using the `cmp` keyword. They can be defined at both the
module level (accessible from the module's namespace), or the superimposition level (accessible from the superimposed
type's scope). There are some important distinction from local variables:

1. Constants are always constant, and cannot be defined as mutable, or modified in any way.
2. Constants are always initialized, and must be defined with a value.
3. Constants can not be moved or partially moved in any way.
4. Constants must be defined with a type as well as a value.
5. Constants' type cannot be a variant type.

## Constant

Constants are values that will live the length of the program. They cannot be mutated, because this creates "global
variables" in the module namespace, and effectively "static mutable" variables at the superimposition level. This
encourages poor programming practices. Having mutable global variables adds complexity, introduces unexpected side
effects and creates difficult debugging problems.

Constants' types are not restricted to booleans and integers, but can be any type that can be instantiated (effectively
any type that isn't a variant type).

A constant expression is a non-function expression (until constant functions are supported), that itself only involves
constant expressions (arrays', tuples' and object initializations' inner values). For example:

- `cmp x: std::bignum::BigInt = 1`
- `cmp x: std::array::Arr[std::string::Str, 2] = ["hello", "world"]`
- `cmp x: Point = Point(x=0, y=0, z=0)`

Each of these expressions and their respective nested expressions are all "constant" (literals or object initializations
that only contain literals or object initializations). As with standard object initializations, not all attributes need
to be present in the initializer.

## Type & Value

Constants must be defined with both a type and a value. This is because the type of the constant may be required before
the value has been analysed, and the value cannot be pre-analysed because the scope may not be ready. This means that
the type is directly used for type inference, and the analysis stage ensures the type of the value matches the given
type exactly. This is how variant types are prevented, as the type/value match is done with a more strict set of
conditions, prevent variant matches.

This is unlike local variables, whose type is never required until that line of code is reached, in which case the
variable value can be analysed in place first.

## Examples

A simple use of constants is seen in the `std::constants` module:

```S++
# std::constants
cmp pi: F64 = 3.14159265358979323846
cmp e : F64 = 2.71828182845904523536
cmp r2: F64 = 1.41421356237309504880
```
