# Memory Model

## Model

S++ uses a "partially automatic memory management" model. This means that the programmer never manually allocates or
frees memory, as "scope-bound resource management" is used to automatically manage memory, by tying the lifetime of
resources to the scope in which they are created; memory allocation is done with object initialization, and memory
freeing is done with object destruction.

While allocation and freeing are done automatically, borrows to variables must be manually created, using either the `&`
or `&mut` tokens. This tells the compiler whether an immutable or mutable borrow is being created. This is the same as
Rust, and different to C++'s references that are automatically created.

Three key techniques are used to ensure memory errors are always mitigated:

1. [Ownership Tracking](#ownership-tracking): this tracks the ownership of objects, and at any line of the program, the
   compiler knows if a variable is holding an initialized object, or contains no object. In the case no object is
   contained, the symbol is unusable except for assignment (re-allocation).
2. [Second-Class Borrows](#second-class-borrows): this is a way to borrow an object without moving it. This is useful
   for when a function needs to borrow an object, but the object must be used again after the function call. Borrows can
   only be taken at certain places, removing the need for lifetime analysis.
3. [The Law of Exclusivity](#the-law-of-exclusivity): this is a rule that states that only one mutable borrow xor any
   number of immutable borrows overlapping memory regions can exist at a time. This is enforced by the compiler, and if
   a mutable borrow is attempted while another borrow exists, the compiler will throw a compile time error.

## Ownership Tracking

Ownership tracking is a concept in the S++ memory model that ensures only fully-initialized objects are moved or
borrowed from. This mitigates the common memory [use-after-free](), [double-free](), and [uninitialized use]() errors.

Any variable (in either
the [fully-](Terms-Definitions.md#fully-initialized), [partially-](Terms-Definitions.md#partially-initialized),
or [non](Terms-Definitions.md#non-initialized)-initialized state) can have a fully-initialized value assigned to it.
This marks the variable as fully-initialized, and it can be moved or borrowed from. Attributes can be set or moved off
of a fully or partially initialized object, but they cannot be individually set to a non-initialized object.

The initialization state of a variable is tracked at the symbol level, and during semantic analysis, any violations of
the ownership tracking rules will result in a compile time error. [Move semantics](#moving-vs-copying) are used by
default, meaning a value is moved when assigned to a variable, passed as a function argument, or returned from a
function.

In the following example, the variable `x` is declared as initialized with the value `"hello"`. The value inside `x`is
then moved into the variable `y` on declaration. The variable `x` is now non-initialized, and cannot be used until it is
re-assigned a value (requiring it to be declared as `mut`):

```S++
let x = "hello"
let y = x
```

### Partial Moves

Partially-initialized variables are created when an attribute is moved off an object. This leaves the variable in a
restricted state; it cannot be moved of borrowed from, until all partial moved have been resolved.

A borrow can never be a partial move. This is because it is impossible to borrow a partially-initialized object, and is
impossible to move an attribute off an object that is borrowed from. Together, these rules ensure that borrows are
always completely valid, mitigating any unexpected behaviour.

In the following example, a partial move is created, when moving the `x` attribute off of the `point`:

```S++
let p = Point(x=0, y=0, z=0)
let x = p.x
```

### Moving vs Copying

By default, all values in S++ are moved when assigned to a variable, passed as a function argument, or returned from a
function. This means that the value is moved from the source to the destination, and the source is left in a
non-initialized state.

To copy a value, the `Copy` type must be superimposed on the type. This allows the value to be copied in all instances
where a move would have otherwise happened. This is superimposed on the numeric and boolean classes. As the `Copy` type
has no abstract methods, instead of using `sup T ext Copy { }`, it is fine to use `@inherit(Copy)`.

The `Copy` type doesn't require any attribute type's classes to also superimpose `Copy`. This is because the copy
behaviour duplicates the source part of the memory, and allows it to be accessible via the correct type, simplifying the
logic required for copying.

For a customized copying behaviour, the type can extend the `Clone` type. This allows the user to define their own
_cloning_ behaviour, by overriding the `Clone::clone` method. The `Clone` and `Copy` types are completely independent,
and don't require each other. Sometimes, `Clone` is superimposed for a more refined choice as to when a value should be
copied.

In the following example, the type `Point` is defined with the `Copy` type:

```S++
cls Point {
    x: U32
    y: U32
    z: U32
}

sup Point ext std::copy::Copy { }
```

### Rules

1. A value is moved out of a variable when its type doesn't superimpose `Copy`, and is used as an assignment value,
   move-convention function argument, object initialization argument, move-convention yield, or return value.
2. For an attribute to be movable off an object, the attribute must be fully-initialized. This means that the owner
   object must be either fully-initialized too, or partially-initialized with that attribute present.
3. Moving an attribute off an object will leave the object in a partially-initialized state, with that attribute
   removed, unless the attribute type superimposes the `Copy` type, in which case it is copied.
4. An attribute can be assigned to a fully-initialized or partially-initialized object, but not a non-initialized
   object.
5. A partially-initialized object cannot be moved or borrowed from, until all attributes have been resolved, thus making
   it a fully-initialized object.
6. An attribute can never be moved off a borrowed object.

## Second-Class Borrows

S++ uses second-class borrows. These are identical in functionality to Rust's borrows, but are not first-class types.
This means that the borrow status isn't stored with the type, but with the variable's symbol directly. There are a lot
of restrictions as to where a borrow can be taken. This eliminates the need for lifetime annotations, as the borrow
checker can infer the lifetime of a borrow from the code itself, by scoping rules.

Borrows can only be taken at two places:

1. Function call sites: `func(&var1, &mut var2)`
2. Yielding from a coroutine: `gen &var1`

### Function Call Sites

Taking a borrow at a function call site is guaranteed to be safe, because the lifetime of the borrow will always be less
than the lifetime of the owned object. This is because the owned object must exist in the current scope, and the borrow
is passed into the function call (a new inner scope). Scopes represent frames on the stack, meaning that the lifetime of
inner scopes must be less than the lifetime of the current scope.

An additional bonus to this model is that borrows themselves can be stored on the stack, as the borrow cannot escape the
frame that it's created in at the function call site. They are automatically dropped when the frame is popped off the
stack, meaning that borrows are automatically released.

### Yielding from a Coroutine

Taking a borrow at a `gen` expression (coroutine yield) is guaranteed to be safe, because control will always return to
the coroutine when it is resumed again. This means that the owned object (which is in the coroutine scope) can never be
used until the coroutine is resumed, and the borrow is released.

This is a critical feature for iteration, which is solely based on coroutines. For example, the `iter_ref`
and `iter_mut` method both yield borrows with the `GenRef[T]` and `GenMut[T]` types respectively.

### Lifetime Analysis

The use of second-class borrows means that lifetime analysis becomes trivial. All function call site borrows move into
an inner frame, meaning they can never outlive their owned object. Yielding borrows can never outlive their owned
objects, because control cannot be returned to the coroutine (where the owned object exists), until the coroutine is
resumed, and the borrow is therefore released.

### Stacking Borrows

Borrows can be stacked, by using the `&` operator on a variable that is already borrowed, but are automatically reduced
to 1-layer borrows. This means that a borrow of a borrow can be taken, increasing the number of active borrows, but both
are direct borrows of the corresponding owned object. That is, both borrows are `&T` types, not `&T` and `&&T` types.
This differs from `C++`, where stacking pointers for example can create `T**` types.

Taking a mutable borrow of an immutable borrow is not allowed, ie `&T` can never become `&mut T`. Mutable borrows are
allowed to "decay" into immutable borrows, allowing the borrow to either be moved or borrowed into a method (if the `&`
operator had to be applied to convert a mutable borrow into an immutable borrow, then there would be no way to move a
mutable borrow into a method expecting an immutable borrow, it would always be re-borrowed in).

### Mutable Borrows vs Mutable Variables

The mutability of a variable and its borrow can be different. The difference revolves around the mutability of the
symbol, ie can the value inside it be replaced, and the mutability of the value itself, ie can the existing value be
mutated:

| Borrow? | Example                        | Value Mutability           | Borrow Mutability      |
|---------|--------------------------------|----------------------------|------------------------|
| `N`     | `fun f(x: T) -> Void`          | `x` can not be re-assigned | `x` can not be mutated |
| `N`     | `fun f(mut x: T) -> Void`      | `x` can be re-assigned     | `x` can be mutated     |
| `Y`     | `fun f(x: &T) -> Void`         | `x` can not be re-assigned | `x` can not be mutated |
| `Y`     | `fun f(mut x: &T) -> Void`     | `x` can be re-assigned     | `x` can not be mutated |
| `Y`     | `fun f(x: &mut T) -> Void`     | `x` can not be re-assigned | `x` can be mutated     |
| `Y`     | `fun f(mut x: &mut T) -> Void` | `x` can be re-assigned     | `x` can be mutated     |

### Destructuring Borrows

The destructuring variable syntax allows for owned objects to be destructured into their attributes. This cannot happen
with borrows, because attributes cannot be moved off of a borrow. Further to this, the type checker would fail,
because `f(Point(x, y): &Point)` has `Point` being compared to `&Point`, which are different types.

## The Law of Exclusivity

The Law of Exclusivity prevents overlapping mutable borrows to the same owned object, which can lead to data races and
inconsistent memory reads. In short, 1 mutable borrow xor any number of immutable borrows can exist at one time. The Law
of Exclusivity is enforced by the compiler at compile time.

There laws, in detail, are as follows:

1. No more than 1 overlapping mutable borrow can be made at any given time.
2. Any number of overlapping immutable borrows can be made at any given time.
3. Law 1 xor Law 2 must be followed at all times.

Fundamentally, whilst a mutable borrow exists to some memory location, no part of that memory location, however small,
can be borrowed in any way. If the existing borrow is immutable, however, than any number of immutable borrows to any
part of that section of memory can be borrowed immutable.

### Overlapping Borrows

These laws apply to **overlapping** borrows. An overlapping borrow is where one borrow inclusively contains another
borrow. That is, the memory location that the second borrow points to, is within the memory location that the first
borrow points to, or vice versa.

For example, `x.a` overlaps `x`, because `x` contains `x.a`. Therefore, if `x.a` is borrowed mutably, then `x` cannot
be borrowed in any way, and vice versa. However, `x.a` and `x.b` do not overlap, because they are separate memory
locations and do not contain each other. As such, `x.a` and `x.b` can be borrowed in any way simultaneously.

| Memory Region (X) | Memory Region of Attributes | Part  |
|-------------------|-----------------------------|-------|
|                   | `1000 -> 1008`              | `x`   |
|                   | `1000 -> 1004`              | `x.a` |
|                   | `1004 -> 1008`              | `x.b` |

Design Decisions
:

1. Borrows could be taken automatically, without the requirement that the `&` tokens appear at call sites. This was not
   implemented, because manual borrows makes it easier for the programmer to reason about
   the [law of exclusivity](#the-law-of-exclusivity) as they can see where borrows are made without having to look at
   the function signature. The same logic was applied to the `gen` expression.
2. **Second class borrows** are used instead of first class borrows like in Rust, because it allows lifetime analysis to
   be eliminated; the borrow is guaranteed to be in a inner frame, and therefore automatically have a shorter lifetime
   than the owned object its borrowing from.
3. The **default semantic is to move values**, as this is the most efficient way to handle memory. This feature was
   inspired by Rust.
4. **Copying a type is enabled by superimposing the `Copy` type** on the type. This was also inspired by Rust, as are
   the
   entire operations suit - superimpose special compiler-known classes over a type to add or override functionality.
5. **Partial moves are allowed**, as they are a useful feature in a method that consumes the `self` object, or during
   destructure operations.
6. **Partial moves cannot be taken from borrowed object**, and borrows cannot be taken from partially-initialized
   objects.