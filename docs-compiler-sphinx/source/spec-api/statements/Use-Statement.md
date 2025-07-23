# Use Statement

The `use` statement is a convenience statement that allows for the namespace reduction of a fully qualified type,
allowing it ot be used directly by the type name. For example:

```S++
use std::string::Str
```

This will allow the `Str` type to be used directly, without the need to prefix it with `std::string::`. This is useful
for reducing the verbosity of code, especially when using types from the standard library or other modules.

## Comparisons with the `type` statement

There is some overlap between `use` and `type` statements. The statement `use std::string::Str` is equivalent to
`type Str = std::string::Str`, but the `use` statement is more convenient for reducing verbosity, where-as the `type`
statement is more useful for creating type aliases that can be used in place of the original type.
