from tests._Utils import *


class CoroutineYielding(CustomTestCase):
    @should_fail_compilation(SemanticErrors.IterExpressionBranchMissingError)
    def test_invalid_gen_opt_missing_opt_branch(self):
        """
        use std::generator::GenOpt
        use std::string::Str
        use std::void::Void

        cor g() -> GenOpt[Str] {
            gen "hello"
            gen
        }

        fun f() -> Void {
            let generator = g()
            let value = generator.res()

            let x = iter value of
                internal { 1 }
                !! { 2 }
        }
        """

    @should_fail_compilation(SemanticErrors.IterExpressionBranchMissingError)
    def test_invalid_gen_res_missing_res_branch(self):
        """
        use std::generator::GenRes
        use std::string::Str
        use std::void::Void

        cls Error { }

        cor g() -> GenRes[Str, Error] {
            gen "hello"
            gen Error()
        }

        fun f() -> Void {
            let generator = g()
            let value = generator.res()

            let x = iter value of
                internal { 1 }
                !! { 2 }
        }
        """

    @should_fail_compilation(SemanticErrors.IterExpressionBranchMissingError)
    def test_invalid_gen_missing_val_branch(self):
        """
        use std::generator::Gen
        use std::string::Str
        use std::void::Void

        cor g() -> Gen[Str] {
            gen "hello"
        }

        fun f() -> Void {
            let generator = g()
            let value = generator.res()

            let x = iter value of
                internal { 1 }
        }
        """

    @should_fail_compilation(SemanticErrors.IterExpressionBranchIncompatibleError)
    def test_invalid_iter_pattern_incompatible_type_gen_opt(self):
        """
        use std::generator::GenOpt
        use std::string::Str
        use std::void::Void

        cor g() -> GenOpt[Str] {
            gen "hello"
            gen
        }

        fun f() -> Void {
            let generator = g()
            let value = generator.res()

            let x = iter value of
                !error { 1 }
        }
        """

    @should_fail_compilation(SemanticErrors.IterExpressionBranchIncompatibleError)
    def test_invalid_iter_pattern_incompatible_type_gen_res(self):
        """
        use std::generator::GenRes
        use std::string::Str
        use std::void::Void

        cls Error { }

        cor g() -> GenRes[Str, Error] {
            gen "hello"
            gen Error()
        }

        fun f() -> Void {
            let generator = g()
            let value = generator.res()

            let x = iter value of
                _ { 1 }
        }
        """

    @should_fail_compilation(SemanticErrors.IterExpressionBranchIncompatibleError)
    def test_invalid_iter_pattern_incompatible_type_gen_1(self):
        """
        use std::generator::Gen
        use std::string::Str
        use std::void::Void

        cor g() -> Gen[Str] {
            gen "hello"
        }

        fun f() -> Void {
            let generator = g()
            let value = generator.res()

            let x = iter value of
                !error { 1 }
        }
        """

    @should_fail_compilation(SemanticErrors.IterExpressionBranchIncompatibleError)
    def test_invalid_iter_pattern_incompatible_type_gen_2(self):
        """
        use std::generator::Gen
        use std::string::Str
        use std::void::Void

        cor g() -> Gen[Str] {
            gen "hello"
        }

        fun f() -> Void {
            let generator = g()
            let value = generator.res()

            let x = iter value of
                _ { 1 }
        }
        """

    @should_fail_compilation(SemanticErrors.IterExpressionBranchTypeDuplicateError)
    def test_invalid_iter_pattern_duplicate_type(self):
        """
        use std::generator::Gen
        use std::string::Str
        use std::void::Void

        cor g() -> Gen[Str] {
            gen "hello"
        }

        fun f() -> Void {
            let generator = g()
            let value = generator.res()

            let x = iter value of
                internal { 1 }
                internal { 2 }
        }
        """

    @should_pass_compilation()
    def test_valid_iter_opt(self):
        """
        use std::generator::GenOpt
        use std::string::Str
        use std::void::Void

        cor g() -> GenOpt[Str] {
            gen "hello"
            gen
        }

        fun f() -> Void {
            let mut generator = g()
            let value = generator.res()

            iter value of
                internal { 1 }
                _ { 2 }
        }
        """

    @should_pass_compilation()
    def test_valid_iter_res(self):
        """
        use std::generator::GenRes
        use std::string::Str
        use std::void::Void

        cls Error { }

        cor g() -> GenRes[Str, Error] {
            gen "hello"
            gen Error()
        }

        fun f() -> Void {
            let mut generator = g()
            let value = generator.res()

            iter value of
                internal { 1 }
                !error { 2 }
        }
        """

    @should_pass_compilation()
    def test_valid_iter_gen(self):
        """
        use std::generator::Gen
        use std::string::Str
        use std::void::Void

        cor g() -> Gen[Str] {
            gen "hello"
        }

        fun f() -> Void {
            let mut generator = g()
            let value = generator.res()

            iter value of
                internal { 1 }
        }
        """
