from tests._Utils import *
import sys


BIT_LEN = sys.maxsize.bit_length() + 1


class TestIntegerLiteralAst(CustomTestCase):
    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_u8_lower_bound(self):
        """
        fun f() -> std::void::Void {
            let x = -1_u8
        }
        """
        
    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_u8_upper_bound(self):
        """
        fun f() -> std::void::Void {
            let x = 256_u8
        }
        """
        
    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_i8_lower_bound(self):
        """
        fun f() -> std::void::Void {
            let x = -129_i8
        }
        """
        
    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_i8_upper_bound(self):
        """
        fun f() -> std::void::Void {
            let x = 128_i8
        }
        """
        
    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_u16_lower_bound(self):
        """
        fun f() -> std::void::Void {
            let x = -1_u16
        }
        """
        
    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_u16_upper_bound(self):
        """
        fun f() -> std::void::Void {
            let x = 65536_u16
        }
        """
        
    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_i16_lower_bound(self):
        """
        fun f() -> std::void::Void {
            let x = -32769_i16
        }
        """
        
    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_i16_upper_bound(self):
        """
        fun f() -> std::void::Void {
            let x = 32768_i16
        }
        """
        
    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_u32_lower_bound(self):
        """
        fun f() -> std::void::Void {
            let x = -1_u32
        }
        """
        
    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_u32_upper_bound(self):
        """
        fun f() -> std::void::Void {
            let x = 4294967296_u32
        }
        """
        
    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_i32_lower_bound(self):
        """
        fun f() -> std::void::Void {
            let x = -2147483649_i32
        }
        """
        
    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_i32_upper_bound(self):
        """
        fun f() -> std::void::Void {
            let x = 2147483648_i32
        }
        """
        
    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_u64_lower_bound(self):
        """
        fun f() -> std::void::Void {
            let x = -1_u64
        }
        """
        
    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_u64_upper_bound(self):
        """
        fun f() -> std::void::Void {
            let x = 18446744073709551616_u64
        }
        """

    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_usize_lower_bound(self):
        """
        fun f() -> std::void::Void {
            let x = -1_uz
        }
        """

    if BIT_LEN == 64:
        @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
        def test_invalid_usize_upper_bound(self):
            """
            fun f() -> std::void::Void {{
                let x = 18446744073709551616_uz
            }}
            """

    elif BIT_LEN == 32:
        @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
        def test_invalid_usize_upper_bound(self):
            """
            fun f() -> std::void::Void {
                let x = 4294967296_uz
            }
            """
        
    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_i64_lower_bound(self):
        """
        fun f() -> std::void::Void {
            let x = -9223372036854775809_i64
        }
        """
        
    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_i64_upper_bound(self):
        """
        fun f() -> std::void::Void {
            let x = 9223372036854775808_i64
        }
        """
        
    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_u128_lower_bound(self):
        """
        fun f() -> std::void::Void {
            let x = -1_u128
        }
        """
        
    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_u128_upper_bound(self):
        """
        fun f() -> std::void::Void {
            let x = 340282366920938463463374607431768211456_u128
        }
        """
        
    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_i128_lower_bound(self):
        """
        fun f() -> std::void::Void {
            let x = -170141183460469231731687303715884105729_i128
        }
        """
        
    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_i128_upper_bound(self):
        """
        fun f() -> std::void::Void {
            let x = 170141183460469231731687303715884105728_i128
        }
        """
        
    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_u256_lower_bound(self):
        """
        fun f() -> std::void::Void {
            let x = -1_u256
        }
        """
        
    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_u256_upper_bound(self):
        """
        fun f() -> std::void::Void {
            let x = 115792089237316195423570985008687907853269984665640564039457584007913129639936_u256
        }
        """
        
    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_i256_lower_bound(self):
        """
        fun f() -> std::void::Void {
            let x = -57896044618658097711785492504343953926634992332820282019728792003956564819969_i256
        }
        """
        
    @should_fail_compilation(SemanticErrors.NumberOutOfBoundsError)
    def test_invalid_i256_upper_bound(self):
        """
        fun f() -> std::void::Void {
            let x = 57896044618658097711785492504343953926634992332820282019728792003956564819968_i256
        }
        """
        
    @should_pass_compilation()
    def test_valid_u8(self):
        """
        fun f() -> std::void::Void {
            let x = 0_u8
        }
        """
        
    @should_pass_compilation()
    def test_valid_i8(self):
        """
        fun f() -> std::void::Void {
            let x = -128_i8
        }
        """
        
    @should_pass_compilation()
    def test_valid_u16(self):
        """
        fun f() -> std::void::Void {
            let x = 65535_u16
        }
        """
        
    @should_pass_compilation()
    def test_valid_i16(self):
        """
        fun f() -> std::void::Void {
            let x = -32768_i16
        }
        """
        
    @should_pass_compilation()
    def test_valid_u32(self):
        """
        fun f() -> std::void::Void {
            let x = 4294967295_u32
        }
        """
        
    @should_pass_compilation()
    def test_valid_i32(self):
        """
        fun f() -> std::void::Void {
            let x = -2147483648_i32
        }
        """
        
    @should_pass_compilation()
    def test_valid_u64(self):
        """
        fun f() -> std::void::Void {
            let x = 18446744073709551615_u64
        }
        """

    if BIT_LEN == 64:
        @should_pass_compilation()
        def test_valid_usize(self):
            """
            fun f() -> std::void::Void {
                let x = 18446744073709551615_uz
            }
            """

    elif BIT_LEN == 32:
        @should_pass_compilation()
        def test_valid_usize(self):
            """
            fun f() -> std::void::Void {
                let x = 4294967295_uz
            }
            """
        
    @should_pass_compilation()
    def test_valid_i64(self):
        """
        fun f() -> std::void::Void {
            let x = -9223372036854775808_i64
        }
        """
        
    @should_pass_compilation()
    def test_valid_u128(self):
        """
        fun f() -> std::void::Void {
            let x = 340282366920938463463374607431768211455_u128
        }
        """
        
    @should_pass_compilation()
    def test_valid_i128(self):
        """
        fun f() -> std::void::Void {
            let x = -170141183460469231731687303715884105728_i128
        }
        """
        
    @should_pass_compilation()
    def test_valid_u256(self):
        """
        fun f() -> std::void::Void {
            let x = 115792089237316195423570985008687907853269984665640564039457584007913129639935_u256
        }
        """
        
    @should_pass_compilation()
    def test_valid_i256(self):
        """
        fun f() -> std::void::Void {
            let x = -57896044618658097711785492504343953926634992332820282019728792003956564819968_i256
        }
        """
