from tests._Utils import *


class TestAstMemoryYieldedBorrowOverlap(CustomTestCase):
    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_use_mut_borrow_after_conflicting_ref_borrow_created_simple(self):
        """
        cor g(a: &mut std::string::Str) -> std::generator::Gen[std::string::Str] { }

        fun h(a: &std::string::Str) -> std::void::Void { }

        fun f() -> std::void::Void {
            let mut x = "hello world"
            let coroutine = g(&mut x)
            h(&x)
            coroutine.res()
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_use_ref_borrow_after_conflicting_mut_borrow_created_simple(self):
        """
        cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str] { }

        fun h(a: &mut std::string::Str) -> std::void::Void { }

        fun f() -> std::void::Void {
            let mut x = "hello world"
            let coroutine = g(&x)
            h(&mut x)
            coroutine.res()
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_use_mut_borrow_after_conflicting_mut_borrow_created_simple(self):
        """
        cor g(a: &mut std::string::Str) -> std::generator::Gen[std::string::Str] { }

        fun h(a: &mut std::string::Str) -> std::void::Void { }

        fun f() -> std::void::Void {
            let mut x = "hello world"
            let coroutine = g(&mut x)
            h(&mut x)
            coroutine.res()
        }
        """

    @should_pass_compilation()
    def test_valid_use_ref_borrow_after_conflicting_ref_borrow_created_simple(self):
        """
        cor g(a: &std::string::Str) -> std::generator::Gen[std::string::Str] { }

        fun h(a: &std::string::Str) -> std::void::Void { }

        fun f() -> std::void::Void {
            let x = "hello world"
            let mut coroutine = g(&x)
            h(&x)
            coroutine.res()
        }
        """

    @should_pass_compilation()
    def test_valid_define_conflicting_mut_borrow_after_mut_borrow_created(self):
        """
        cls MyType { }
        sup MyType {
            cor custom_iter_ref(&self) -> std::generator::Gen[&std::string::Str] { }
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut std::string::Str] { }
        }

        fun test() -> std::void::Void {
            let object = MyType()
            let generator_ref_1 = object.custom_iter_ref()
            let generator_ref_2 = object.custom_iter_ref()
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_use_mut_borrow_after_conflicting_ref_borrow_created(self):
        """
        cls MyType { }
        sup MyType {
            cor custom_iter_ref(&self) -> std::generator::Gen[&std::string::Str] { }
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut std::string::Str] { }
        }

        fun test() -> std::void::Void {
            let mut object = MyType()
            let generator_mut = object.custom_iter_mut()
            let generator_ref = object.custom_iter_ref()
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_use_ref_borrow_after_conflicting_mut_borrow_created(self):
        """
        cls MyType { }
        sup MyType {
            cor custom_iter_ref(&self) -> std::generator::Gen[&std::string::Str] { }
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut std::string::Str] { }
        }

        fun test() -> std::void::Void {
            let mut object = MyType()
            let generator_ref = object.custom_iter_ref()
            let generator_mut = object.custom_iter_mut()
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_use_mut_borrow_after_conflicting_mut_borrow_created(self):
        """
        cls MyType { }
        sup MyType {
            cor custom_iter_ref(&self) -> std::generator::Gen[&std::string::Str] { }
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut std::string::Str] { }
        }

        fun test() -> std::void::Void {
            let mut object = MyType()
            let generator_mut_1 = object.custom_iter_mut()
            let generator_mut_2 = object.custom_iter_mut()
        }
        """

    @should_pass_compilation()
    def test_valid_use_ref_borrow_after_conflicting_ref_borrow_created(self):
        """
        cls MyType { }
        sup MyType {
            cor custom_iter_ref(&self) -> std::generator::Gen[&std::string::Str] { }
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut std::string::Str] { }
        }

        fun test() -> std::void::Void {
            let mut object = MyType()
            let mut generator_ref_1 = object.custom_iter_ref()
            let generator_ref_2 = object.custom_iter_ref()
            generator_ref_1.res()
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_use_mut_borrow_after_conflicting_ref_borrow_created_with_scoping(self):
        """
        cls MyType { }
        sup MyType {
            cor custom_iter_ref(&self) -> std::generator::Gen[&std::string::Str, std::void::Void] { }
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut std::string::Str, std::void::Void] { }
        }

        fun test() -> std::void::Void {
            let mut object = MyType()
            let generator_mut: std::generator::Gen[&mut std::string::Str, std::void::Void]
            case true {
                generator_mut = object.custom_iter_mut()
            }
            let generator_ref = object.custom_iter_ref()
            generator_mut.res()
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_use_ref_borrow_after_conflicting_mut_borrow_created_with_scoping(self):
        """
        cls MyType { }
        sup MyType {
            cor custom_iter_ref(&self) -> std::generator::Gen[&std::string::Str, std::void::Void] { }
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut std::string::Str, std::void::Void] { }
        }

        fun test() -> std::void::Void {
            let mut object = MyType()
            let generator_ref: std::generator::Gen[&std::string::Str, std::void::Void]
            case true {
                generator_ref = object.custom_iter_ref()
            }
            let generator_mut = object.custom_iter_mut()
            generator_ref.res()
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_use_mut_borrow_after_conflicting_mut_borrow_created_with_scoping(self):
        """
        cls MyType { }
        sup MyType {
            cor custom_iter_ref(&self) -> std::generator::Gen[&std::string::Str, std::void::Void] { }
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut std::string::Str, std::void::Void] { }
        }

        fun test() -> std::void::Void {
            let mut object = MyType()
            let generator_mut_1: std::generator::Gen[&mut std::string::Str, std::void::Void]
            case true {
                generator_mut_1 = object.custom_iter_mut()
            }
            let generator_mut_2 = object.custom_iter_mut()
        }
        """

    @should_pass_compilation()
    def test_valid_use_ref_borrow_after_conflicting_ref_borrow_created_with_scoping(self):
        """
        cls MyType { }
        sup MyType {
            cor custom_iter_ref(&self) -> std::generator::Gen[&std::string::Str, std::void::Void] { }
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut std::string::Str, std::void::Void] { }
        }

        fun test() -> std::void::Void {
            let object = MyType()
            let mut generator_ref_1: std::generator::Gen[&std::string::Str, std::void::Void]
            case true {
                generator_ref_1 = object.custom_iter_ref()
            }
            let generator_ref_2 = object.custom_iter_ref()
            generator_ref_1.res()
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_invalid_use_mut_borrow_after_conflicting_mut_borrow_created_for_resume(self):
        """
        cls MyType { }
        sup MyType {
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut std::string::Str, std::void::Void] { }
        }

        fun test() -> std::void::Void {
            let mut object = MyType()
            let mut generator_mut = object.custom_iter_mut()
            let x = generator_mut.res()
            let y = generator_mut.res()
            let z = iter x of
                val { val.to_ascii_uppercase() }
                !! { "" }
        }
        """

    @should_pass_compilation()
    def test_valid_use_ref_borrow_after_conflicting_ref_borrow_created_for_resume(self):
        """
        cls MyType { }
        sup MyType {
            cor custom_iter_ref(&self) -> std::generator::Gen[&std::string::Str, std::void::Void] { }
        }

        fun test() -> std::void::Void {
            let mut object = MyType()
            let mut generator_ref = object.custom_iter_ref()
            let x = generator_ref.res()
            let y = generator_ref.res()
            let z = iter x of
                val { val.to_ascii_uppercase() }
                !! { "" }
        }
        """

    @should_pass_compilation()
    def test_valid_use_mut_borrow_after_conflicting_ref_borrow_created_with_scoping(self):
        """
        cls MyType { }
        sup MyType {
            cor custom_iter_ref(&self) -> std::generator::Gen[&std::string::Str, std::void::Void] { }
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut std::string::Str, std::void::Void] { }
        }

        fun test() -> std::void::Void {
            let mut object = MyType()
            loop true {
                let generator_mut = object.custom_iter_mut()
            }
            let mut generator_ref = object.custom_iter_ref()
            generator_ref.res()
        }
        """

    @should_pass_compilation()
    def test_valid_use_ref_borrow_after_conflicting_mut_borrow_created_with_scoping(self):
        """
        cls MyType { }
        sup MyType {
            cor custom_iter_ref(&self) -> std::generator::Gen[&std::string::Str, std::void::Void] { }
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut std::string::Str, std::void::Void] { }
        }

        fun test() -> std::void::Void {
            let mut object = MyType()
            loop true {
                let generator_ref = object.custom_iter_ref()
            }
            let mut generator_mut = object.custom_iter_mut()
            generator_mut.res()
        }
        """

    @should_pass_compilation()
    def test_valid_use_mut_borrow_after_conflicting_mut_borrow_created_with_scoping(self):
        """
        cls MyType { }
        sup MyType {
            cor custom_iter_ref(&self) -> std::generator::Gen[&std::string::Str, std::void::Void] { }
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut std::string::Str, std::void::Void] { }
        }

        fun test() -> std::void::Void {
            let mut object = MyType()
            loop true {
                let generator_mut_1 = object.custom_iter_mut()
            }
            let mut generator_mut_1 = object.custom_iter_mut()
            generator_mut_1.res()
        }
        """

    @should_pass_compilation()
    def test_valid_use_ref_borrow_after_conflicting_ref_borrow_created_with_scoping_2(self):
        """
        cls MyType { }
        sup MyType {
            cor custom_iter_ref(&self) -> std::generator::Gen[&std::string::Str, std::void::Void] { }
            cor custom_iter_mut(&mut self) -> std::generator::Gen[&mut std::string::Str, std::void::Void] { }
        }

        fun test() -> std::void::Void {
            let object = MyType()
            loop true {
                let generator_ref_1 = object.custom_iter_ref()
            }
            let mut generator_ref_2 = object.custom_iter_ref()
            generator_ref_2.res()
        }
        """
