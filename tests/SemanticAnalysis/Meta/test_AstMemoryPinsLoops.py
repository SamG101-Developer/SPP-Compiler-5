from tests._Utils import *


class TestAstMemoryPinsLoops(CustomTestCase):
    @should_pass_compilation()
    def test_mov_iterator_no_modifications(self):
        """
        use std::vector::Vec
        use std::string::Str
        use std::void::Void

        fun f(mut v: Vec[Str]) -> Void {
            loop x in v.iter_mut() { }
        }
        """

    @should_pass_compilation()
    def test_mut_iterator_no_modifications(self):
        """
        use std::vector::Vec
        use std::string::Str
        use std::void::Void

        fun f(mut v: Vec[Str]) -> Void {
            loop x in v.iter_mut() { }
        }
        """

    @should_pass_compilation()
    def test_ref_iterator_no_modifications(self):
        """
        use std::vector::Vec
        use std::string::Str
        use std::void::Void

        fun f(mut v: Vec[Str]) -> Void {
            loop x in v.iter_ref() { }
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryNotInitializedUsageError)
    def test_mov_iterator_modify_owned_object(self):
        """
        use std::vector::Vec
        use std::string::Str
        use std::void::Void

        fun f(mut v: Vec[Str]) -> Void {
            loop x in v.iter_mov() {
                v.push("hello")
            }
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_mut_iterator_mut_owned_object(self):
        """
        use std::vector::Vec
        use std::string::Str
        use std::void::Void

        fun f(mut v: Vec[Str]) -> Void {
            loop x in v.iter_mut() {
                v.push("hello")
            }
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_mut_iterator_ref_owned_object(self):
        """
        use std::vector::Vec
        use std::string::Str
        use std::void::Void

        fun f(mut v: Vec[Str]) -> Void {
            loop x in v.iter_mut() {
                v.push("hello")
            }
        }
        """

    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_ref_iterator_mut_owned_object(self):
        """
        use std::vector::Vec
        use std::string::Str
        use std::void::Void

        fun f(mut v: Vec[Str]) -> Void {
            loop x in v.iter_ref() {
                v.push("hello")
            }
        }
        """

    @should_pass_compilation()
    def test_mut_iterator_modify_owned_object_after_loop(self):
        """
        use std::vector::Vec
        use std::string::Str
        use std::void::Void

        fun f(mut v: Vec[Str]) -> Void {
            loop x in v.iter_mut() {
            }
            v.push("hello")
        }
        """

    @should_pass_compilation()
    def test_mut_iterator_modify_owned_object_clone(self):
        """
        use std::vector::Vec
        use std::string::Str
        use std::void::Void

        fun f(mut v: Vec[Str]) -> Void {
            loop x in v.clone().iter_mut() {
                v.push("hello world")
            }
        }
        """

    @should_pass_compilation()
    def test_ref_iterator_use_ref(self):
        """
        use std::vector::Vec
        use std::string::Str
        use std::void::Void

        fun f(mut v: Vec[Str]) -> Void {
            loop x in v.iter_ref() {
                let l = v.length()
            }
        }
        """
