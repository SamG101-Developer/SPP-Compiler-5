# Volatile

S++ allows "volatile" variables to be declared. These variables are not optimized by the compiler, and their values are
always read from memory. This is useful for variables that are modified by hardware or other threads, and ensures that
the compiler does not optimize away accesses to these variables.

Unlike C++, `volatile` is not a keyword, because instead of editing the symbolic information of the variable, it is
simply declared as a wrapping type. This is more flexible for when other hardware types are added. The `Vol[T]` type is
known to the compiler, and has accessor methods for interacting with the underlying type.

## Example
```S++
fun f() {
    let x = Vol(val=0_uz)  # Vol[USize]
    let y = x.get()        # Opt[USize]
}
```
