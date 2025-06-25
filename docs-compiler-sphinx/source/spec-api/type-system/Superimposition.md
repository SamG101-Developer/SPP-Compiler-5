# Superimposition

Superimposition is a concept defined for S++. It is a way to add behaviour to a type, in a clear and non-convoluted way.
It also allows for types to extend other types, in separate extension blocks. The two variations of superimpositions
are:

- Superimposition-functions: adding methods/typedefs/comptime-constants to a type.
- Superimposition-extension: extending a type with another type, allowing for inheritance-like behaviour.

## Superimposition Functions

Any number of superimposition-function blocks can be defined for a type, allowing for simpler separation of groups of
methods. It also allows for the customization of types from other libraries, specific to the current project. For
example, an ANSI color library could extend the `std::string::Str` type with methods to colorize the string:

```S++
# Assume this is in a file called `ansi/color.spp`

use std::string::Str


sup Str {
    fun red(self) -> Str {
        ret "\033[31m" + self + "\033[0m"
    }
    
    fun green(self) -> Str {
        ret "\033[32m" + self + "\033[0m"
    }
}


sup Str {
    fun bold(self) -> Str {
        ret "\033[1m" + self + "\033[0m"
    }
    
    fun underline(self) -> Str {
        ret "\033[4m" + self + "\033[0m"
    }
}
```

This example shows how the `Str` type can be extended with methods to colorize the string. The first block adds methods
to colorize the string in red and green, while the second block adds methods to make the string bold and underlined. The
methods can then be used like:

```S++
fun main() -> Void {
    let my_str = "Hello, World!".red().bold()
    std::io::print(&my_str)
}
```

## Superimposition Extension

Extensions are defined by modifying the `sup A` syntax slightly, to include the `ext` keyword: `sup A ext B { }`.

## Using generic types

Classes in S++ can have generic parameters, such as the `Vec[T, A]` type. When superimposing over a type, the full type
must be provided. For a simple type such as `A[T]`, this can be done by telling the `sup` block what the generic
parameters are:

```S++
sup [T] A[T] {
    fun f(&self, other: T) -> Void { ... }
}
```

This will add the `f` method to all specializations of the `A[T]` type, such as `A[Str]` or `A[U64]`. This can be
generalized even further by the valid syntax:

```S++
sup [T] T {
    fun f(&self) -> Void { ... }
}
```

This acts as a blanket implementation over every type that exists in the S++ code being compiled. This is useful for
adding methods to all types, such as a `to_string` method that converts the type to a string representation.

## Specialization

The previous examples showed how to add method to a type with generic parameters, to match all specializations of the
type. Specific specializations can also be added, by specifying concrete generic arguments to the type:

```S++
sup A[Str] {
    fun g(&self) -> U64 { ... }
}
```

This will add the `g` method to the `A[Str]` type, but not to any other specializations of the `A[T]` type. This is
useful for adding methods like `clone`, only when a generic argument itself superimposes the `Clone` type:

```S++
sup [T: Clone] A[T] ext Clone {
    fun clone(&self) -> A[T] { ... }
}
```

Only when the generic argument to `A` superimposes the `Clone` type, will the `clone` method be added to the `A`
variation. As `Str` superimposes `Clone`, the `A[Str]` type will have the `clone` method, but `A[MyOtherType]` will not,
as `MyOtherType` does not superimpose `Clone`.
