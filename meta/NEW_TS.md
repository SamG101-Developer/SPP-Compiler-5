# New Typesystem Upgrades (Specialization)

New type system (generics upgrade)

- Needs to support specialization
- Needs to support generics with different names
- Needs to support constraints

Example

- `cls A [T, U] { }`
- `sup [B: Copy] A[std::string::Str, B] { }`
- `sup [C: Copy & Clone] A[C, std::boolean::Bool] { }`
- `sup [X, Y] A[X, Y] { }`
- `sup [T] T { }`

Description

- When a generic implementation is created: `A[std::string::Str, std::number::bigint::BigInt]`
- Search for all superimposition and superimposition-extension blocks (without generic match)
- Then check for a generic match with a "relaxed equality" (symbolic_eq + generic check)
- Instead of filtering for non-generic matches on the type first, try match ANY type
- This allows for `sup[T] T { }` to get matched (by the relaxed symbol equality checker)

Relaxed symbolic equality idea:

- Source type: `A[std::string::Str, std::number::bigint::BigInt]`
- Target type: every existing superimposition in scope
- Comparison:

Example relaxed matching for `A[std::string::Str, std::number::bigint::BigInt]`:

- `A[std::string::Str, std::number::bigint::BigInt]`
- `[Y] A[std::string::Str, Y]`
- `[X] A[X, std::number::bigint::BigInt]`
- `[P, Q] A[P, Q]`
- `[T] T`

Relaxed matching:

- Check the name part only is a match (symbolic)
- Check each argument matches (symbolically)
- If a target type is "generic" then auto-match it
- Filter for all "sup" blocks with matching types

Redo standard symbolic matching:

- [x] Alter the standard symbolic equality
- [x] Check the non-generic names are symbolically equal
- [x] Then check all the arguments recursively
- [ ] Should allow variants in tuples to match now too

Aliases (TODO)
- The alias symbol doesn't have the sup scopes attached to it

Blanket superimpositions

- Then like Rust `impl <T> Borrow<T> for T { }` we can do `sup [T] T ext Borrow[T] { }` etc.
- Start with BorrowRef, BorrowMut, ToString

**CURRENT**

after `generate_top_level_scopes`, every cls and sup block has had their associated scopes created. no super scopes are
attached to type scopes.

after `load_super_scopes`, base type symbols have their super scopes attached. generic types don't, because their base
type may not have finished attaching super scopes.

**NEW SOLUTION**

when a sup/sup-ext block is processed under `load_super_scopes`, it doesn't attach to its base type. this is because for
things like `sup [T] T`, it can't attach to everything / know that it should.

add a scope-manager based function that runs after `load_super_scopes` (like relink_generics does). this method will go
type by type, and add link the super-scopes to their associated types.

**EXAMPLE**

loop through the scope manager, from the global scope. let's say the first type is `std::string::Str`. it will then
check every single scope that has a parent scope that is a module. if the scope is a designated "sup" scope with a
matching name, then attach it.

let's say the next scope is `Vec[T]`. this scope has a "non_generic_scope" as itself, so no substitution will take
place, meaning that is acts the same (ish) as `std::string::Str`. in the type-comparison, any matches, ie `Vec[A]`,
`Vec[B]`etc will match, because its the right-hand-side that can be generic like `Vec[A]` etc. but specializations like
`Vec[Str]` won't match, because T vs Str is a fail.

next we might have `Vec[Str]`. this will match `Vec[T]`, because whilst T vs Str is a fail, Str vs T is valid. so all
the sup blocks over `Vec[T]` will match, as will the sup blocks over `Vec[Str]`.

note that all types will match generics like `sup [T] T`, because anything vs T will pass.