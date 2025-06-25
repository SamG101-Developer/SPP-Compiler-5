# Classes

S++ inherits the Java philosophy of "everything is an object". Every type is first class, and has a corresponding class
definition, even if it just for the compiler to know a type exists. For example, under the stl `boolean.spp` file, there
is the `Bool` class definition. It has no members, but does have behaviour defined using superimposition blocks, and
`@compiler_builtin` methods. The point of this is to create a uniform type system, where every type is treated the same,
and there are no types and behaviour definitions hidden under LLVM translation (such as bools, numbers and voids).

For inheritance, S++ uses the _superimposition_ model. This was inspired by a combination of Rust, and Python. In
Python, a type is represented by a class. There is no such thing as a "trait" or "interface". Rust allows for a struct
to extend a trait, but does not allow types to extend each other.

In S++, types are only definable via the class definition, and can extend from eah other in separate blocks per
extension. This allows for shared behaviour via "inheritance", or "extension" as it is called in S++, whilst keeping the
links to each super-class explicit. That is, if `A` superimposes `B`, then methods from `B` can only be overridden in
the `sup A ext B { }` block.

Non extension behaviour is added by superimposing methods over a class, with the simpler `sup A { }` syntax. Any number
of superimposition-function blocks can be defined for a type, allowing for simpler separation of groups of methods, as
Rust allows too. See the [superimposition](./Superimposition.md) section for more information on this.
