# New Typesystem Upgrades (Specialization)

New type system (generics upgrade)

- [x] Needs to support specialization
- [x] Needs to support generics with different names
- [ ] Needs to support constraints

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
- [x] Do this inside a function on the `ScopeManager` that runs after `load_super_scopes`

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

- [x] Check the name part only is a match (symbolic)
- [x] Check each argument matches (symbolically)
- [x] If a target type is "generic" then auto-match it
- [x] Filter for all "sup" blocks with matching types

Redo standard symbolic matching:

- [x] Alter the standard symbolic equality
- [x] Check the non-generic names are symbolically equal
- [x] Then check all the arguments recursively
- [x] Should allow variants in tuples to match now too

Aliases (TODO)
- The alias symbol doesn't have the sup scopes attached to it?

Blanket superimpositions

- [x] Then like Rust `impl <T> Borrow<T> for T { }` we can do `sup [T] T ext Borrow[T] { }` etc.
- [ ] Start with `BorrowRef`, `BorrowMut`, `ToString`
