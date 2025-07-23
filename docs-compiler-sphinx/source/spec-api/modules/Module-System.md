# Module System

The module system in S++ is designed to provide a way to organize code into reusable components, allowing for better
code management and modularity. Modules can contain classes, functions, superimpositions, type aliases and constants.

Module naming, namespaces and folder/file structure are all identical, providing a consistent way to organize code.
Every module is available in its fully qualified form, whether this is part of the current codebase, an `ffi` module, or
a `vcs` module. The [use statement](./statements/Use-Statement.md) can be used to reduce the verbosity of the code,
allowing for easier access to types from modules.

# Order of Member Definition

The order of member definition in a module, (and the order of the modules), is completely irrelevant. The compiler
performs multiple passes, loading parts of modules into the scopes and symbol table, such that when analysis semantic
analysis is performed, all symbols from all modules are available.