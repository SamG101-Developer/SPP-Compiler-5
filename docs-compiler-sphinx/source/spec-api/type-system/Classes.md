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

Non-extension behaviour is added by superimposing methods over a class, with the simpler `sup A { }` syntax. Any number
of superimposition-function blocks can be defined for a type, allowing for simpler separation of groups of methods, as
Rust allows too. See the [superimposition](./Superimposition.md) section for more information on this.

## Superimposition

Superimposition is a key concept in S++. It allows for behaviour to be defined iver a type. This comes in two forms:

- Adding behaviour directly top the type
- Extending another type into this type.

Adding behaviour onto a type looks like this:

```S++
sup [T] MyCustomType[T] {
    type InnerType = T
    cmp constant: U64 = 1_u64

    @virtual_method
    fun my_method(&self) -> Void {
        # method implementation
    }
    
    @virtual_method
    fun my_other_method(&self, arg: U64) -> Void {
        # another method implementation
    }
}
```

Extending another type looks like this:

```S++
sup [T] OtherType[T] ext MyCustomType[T] {
    fun my_method(&self) -> Void {
        # method override implementation
    }
    
    fun my_other_method(&self, arg: U64) -> Void {
        # another method override implementation
    }
}
```

## Simple superimposition

Extending the behaviour over a type includes 3 different types of ASTs nodes:

- Type statements: `type InnerType = T`
- Constant statements: `cmp constant: U64 = 1_u64`
- Methods: `fun my_method(&self) -> Void { ... }`

By default, all methods defined over a type are "final"; they cannot be overridden by a superimposition extension block.
Here are two different ways to mark a method as being allowed to be overridden:

- `@virtual_method`: this method _can_ be overridden in a superimposition extension block.
- `@abstract_method`: this method _must_ be overridden in a superimposition extension block.

Any number of simple superimposition blocks can be defined for a type, allowing for separation of concerns and grouping
of methods. For example, if a type has a number of methods that are related to file I/O, then a superimposition block
can be defined for file I/O methods, and another superimposition block can be defined for network methods. This allows
for a cleaner separation of methods, and makes it easier to find methods related to a specific area of the type's
behaviour.

Conflicting definition inside one `sup` block, or across multiple `sup` blocks are not allowed. For example, defining a
type statement in two `sup A` blocks with the same type name, or in the same block with the same type name, is
forbidden. This is the same for `cmp` statements, or conflicting method signatures. This is to ensure that the
superimposition blocks are clear and unambiguous, and that the type's behaviour is well-defined.

## Superimposition extension

Any type can extend any other type. Each type's extension is defined in an individual block, to keep each "inheritance"
isolated. For example, if `A` needs to extend `Base1` and `Base2`, then the following syntax is used:

```S++
sup A ext Base1 {
    # override methods for Base1
}

sup A ext Base2 {
    # override methods for Base2
}
```

Note that if a method is to be overridden in a class, then the first class that defined that method originally must be
superimposed again. For example, in the previous example `A` overrides the two base classes. If the following class `B`
is defined that extends `A`:

```S++
cls B { }

sup B ext A { }
```

Then to override any methods defined on say `Base1`, the `B` class must re-extend `Base1` to access its methods; when
`B` extends `A`, only methods _directly_ defined on `A` are accessible.

```S++
sup B ext Base1 {
    # override methods for Base1
}
```

This creates a looser coupling between classes.

It should be noted that if `A` extends `B`, then this `sup A ext B` block can only be defined once. Extending a type
cannot span multiple `sup-ext` blocks, unlike normal superimposition. This keeps the extension in one place, and is
clear to see exactly how the base type is being extended.

Constraints to superimposition extensions:

- Cyclic extension is not allowed. This means that if `A` extends `B`, then `B` cannot extend `A`.
- Double extension is not allowed. This means that if `A` extends `B`, then `A` cannot extend `B` again in a
  different `sup-ext` block.
- Self extension is not allowed. This means that a type cannot extend itself.

For these constraints, the checks are done using fully generically aware types. This means that `A` can extend both
`C[Str]` and`C[BigInt]`, as they are different types. However, attribute access and method resolution may become
ambiguous; this will be detected if attempted, but as type extension, this is allowed.

### What can be overridden?

When extending a type, the following can be overridden:

- Type statements: `type InnerType = T`
- Constant statements: `cmp constant: U64 = 1_u64`
- Methods: `fun my_method(&self) -> Void { ... }` (as long as they are marked as `@virtual_method` or
  `@abstract_method`).

## Generic superimposition

Generic types for superimposition must be declared before the type being superimposed. With the `cls` statement, the
generics following the typename are _generic parameters_, but for the `sup` blocks, they are generic parguments, because
the type now exists. Therefore, to differentiate the generic parameters from the arguments, they must be declared as "
existing" prior to the type being superimposed over.

## Specialization

Generic superimpositions provide all the behaviour they are given, to all the different generic instantiation of the
type:

```S++
sup [T] MyType[T] {
    fun my_method(&self) -> Void {
        # method implementation
    }
}
```

The types `MyType[Str]` and `MyType[BigInt]` etc will both have the `my_method` method available to them. Specialization
allows for behaviour to be added to specific generic instantiations of a type. This is done by simply specifying the
complete type in the `sup` block:

```S++
sup MyType[Str] {
    fun my_method(&self) -> Void {
        # specialized method implementation for Str
    }
}
```

Now, only the type `MyType[Str]` will have the `my_method` method available to it. This allows for more specific
behaviour to be added to specific types, without affecting the generic type itself. Specialization can be done by
generic constraints too. This is seen often in `Clone` and `Copy` superimpositions, where a type is defined as copyable
if an inner-used generic is copyable, sch as with `Vec[T]` or `Opt[T]`.

## Accessing types and constants

Whilst types and constants are defined in the `sup` blocks, they are accessed via the type name. For example, if a
`sup A` block contains `type Element = T`, then `A::Element` is the correct way to access the type. From inside the
`sup` block, `Self::Element` must be used, as the type is access through the type of being superimposed over. Constants
and methods are runtime accessible, not static accessible, and so are accessed using `self` and the `.` operator.
