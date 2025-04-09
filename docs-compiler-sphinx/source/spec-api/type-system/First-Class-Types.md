# First Class Types

<primary-label ref="header-label"/>

<secondary-label ref="doc-complete"/>

Every type in S++ is first class. This includes arrays, tuples, variants, functions, numbers, booleans, void and
strings. This means that they can be passed as arguments, returned from functions, stored in variables, and so on. It
also means that there is no special behaviour for objects that use these types. This contrasts with languages like C++,
where objects are treated differently to primitive types.

This is a table of the first-class types in S++:

| S++ Type                 | C++ Equivalent       | Description                  |
|--------------------------|----------------------|------------------------------|
| `std::Arr[T, n]`         | T[]                  | Array of type T              |
| `std::Tup[T...]`         | `std::tuple<T...>`   | Tuple of types T             |
| `std::Var[T...]`         | `std::variant<T...>` | Variant of types T           |
| `std::FunRef[Args, Ret]` | `std::function`      | Function reference           |
| `std::FunMut[Args, Ret]` | `std::function`      | Mutable function reference   |
| `std::FunMov[Args, Ret]` | `std::function`      | Move-only function reference |
| `std::U8`                | `uint8_t`            | 8-bit unsigned integer       |
| `std::U16`               | `uint16_t`           | 16-bit unsigned integer      |
| `std::U32`               | `uint32_t`           | 32-bit unsigned integer      |
| `std::U64`               | `uint64_t`           | 64-bit unsigned integer      |
| `std::U128`              | `/`                  | 128-bit unsigned integer     |
| `std::U256`              | `/`                  | 256-bit unsigned integer     |
| `std::I8`                | `int8_t`             | 8-bit signed integer         |
| `std::I16`               | `int16_t`            | 16-bit signed integer        |
| `std::I32`               | `int32_t`            | 32-bit signed integer        |
| `std::I64`               | `int64_t`            | 64-bit signed integer        |
| `std::I128`              | `/`                  | 128-bit signed integer       |
| `std::I256`              | `/`                  | 256-bit signed integer       |
| `std::F8`                | `/`                  | 8-bit float                  |
| `std::F16`               | `/`                  | 16-bit float                 |
| `std::F32`               | `float`              | 32-bit float                 |
| `std::F64`               | `double`             | 64-bit float                 |
| `std::F128`              | `/`                  | 128-bit float                |
| `std::F256`              | `/`                  | 256-bit float                |
| `std::Bool`              | `bool`               | Boolean                      |
| `std::Void`              | `void`               | Void                         |
