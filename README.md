# S++ Compiler

[![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-blue?logo=github)](https://samg101-developer.github.io/SPP-Compiler-5/)
[![Tests](https://img.shields.io/badge/Tests-802-green?logo=pytest&logoColor=ffffff)]()
[![Coverage Status](https://img.shields.io/badge/Test%20Coverage-98.88%25%20(793/802)-cactus?logo=pytest&logoColor=ffffff)]()
[![License](https://img.shields.io/badge/Liscence-MIT-orange)](https://github.com/SamG101-Developer/SPP-Compiler-5/blob/master/LICENSE.txt)
[![security: bandit](https://img.shields.io/badge/Security-Bandit-yellow)](https://github.com/PyCQA/bandit)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=SamG101-Developer_SPP-Compiler-5&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=SamG101-Developer_SPP-Compiler-5)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=SamG101-Developer_SPP-Compiler-5&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=SamG101-Developer_SPP-Compiler-5)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=SamG101-Developer_SPP-Compiler-5&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=SamG101-Developer_SPP-Compiler-5)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=SamG101-Developer_SPP-Compiler-5&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=SamG101-Developer_SPP-Compiler-5)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=SamG101-Developer_SPP-Compiler-5&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=SamG101-Developer_SPP-Compiler-5)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=SamG101-Developer_SPP-Compiler-5&metric=bugs)](https://sonarcloud.io/summary/new_code?id=SamG101-Developer_SPP-Compiler-5)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=SamG101-Developer_SPP-Compiler-5&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=SamG101-Developer_SPP-Compiler-5)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=SamG101-Developer_SPP-Compiler-5&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=SamG101-Developer_SPP-Compiler-5)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=SamG101-Developer_SPP-Compiler-5&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=SamG101-Developer_SPP-Compiler-5)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=SamG101-Developer_SPP-Compiler-5&metric=coverage)](https://sonarcloud.io/summary/new_code?id=SamG101-Developer_SPP-Compiler-5)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=SamG101-Developer_SPP-Compiler-5&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=SamG101-Developer_SPP-Compiler-5)

**Structure**

- `src`: S++ compiler implementation.
- `tests`: S++ compiler unit tests.
- `spp_cli.py`: S++ tool for building and running code.

**S++ Features**

- Memory safe: ownership tracking, second class borrows, law of exclusivity, no raw pointers, default move semantics.
- Type system: strong & static typing, full one-way type inference, generic types, variant types, residual types, first
  class tuples/arrays/functions, aliases, flow typing.
- Object-oriented: classes, superimposition based extension, separation of state and behavior, full specialization.
- Functional: first class functions, higher order functions, lambdas with explicit environment capture.
- Pattern matching: comparison or destructure, object/tuple/array destructure, variant/generic destructure, destructure
  with bindings and wildcards, multiple patterns, pattern guards.
- Concurrency and parallelism: explicit coroutine definitions, generator return types, async at function call site for
  future type returns, standard threading primitives.
