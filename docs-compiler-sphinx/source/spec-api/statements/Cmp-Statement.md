# Global Constants

Global constants are compile time variables, and as such, are denoted using the `cmp` keyword. They are available at the
module level, and accessible from the module's namespace. There are some important distinction from local variables:

1. Global constants are always constant, and cannot be defined as mutable, or modified in any way.
2. Global constants are always initialized, and must be defined with a value.
3. Global constants can not be moved or partially moved in any way.
4. Global constants must be defined with a type as well as a value.

## Constant

Global constant are always constant, because having mutable global variables adds complexity, introduces unexpected side
effects and creates difficult debugging problems. Global constants aren't limited to certain types such as numbers and
booleans, but to "constant" expressions.

A constant expression is a non-function expression (until constant functions are supported), that itself only involves
constant expressions. For example:

- `cmp x: std::number::BigInt = 1`
- `cmp x: std::array::Arr[std::string::Str, 2] = ["hello", "world"]`
- `cmp x: Point = Point(x=0, y=0, z=0)`

Each of these expressions and their respective nested expressions are all "constant" (literals or object initialization
that only contains literals). For more information on object initialization and why not all attributes need to be
provided, see the section on [object initialization](../classes/Object-Initialization.md).

## Type & Value

Global constants must be defined with both a type and a value. This is because the type of the global variable may be
required before the value has been analysed, and the value cannot be pre-analysed because the scope may not be ready.
This means that the type is directly used for type inference, and the analysis stage ensures the type of the value
matches the given type exactly.

This is unlike local variables, whose type is never required until that line of code is reached, in which case the
variable value can be analysed in place first.

## Examples

A simple use of constants is seen in the `std::number` module:

```S++
# std::number
cmp pi: F64 = 3.14159265358979323846
cmp e : F64 = 2.71828182845904523536
cmp r2: F64 = 1.41421356237309504880
```
