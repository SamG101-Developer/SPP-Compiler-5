# Exception Handling

Exception handling in S++ follows Rust's model, using a result-type for error handling, and a `?` postfix operator for
error propagation. The `std::result::Res[T, E]` type is used to represent a result that can either be a value of type
`T` or an error of type `E`. The `Pass[T]` and `Fail[E]` types are used to wrap values inside `Res[T, E]`, where
`Pass[T]` represents a successful result with a value of type `T`, and `Fail[E]` represents an error with a value of
type `E`.
