from tests._Utils import *


class TestMultipleIndexing(CustomTestCase):
    @should_fail_compilation(SemanticErrors.MemoryOverlapUsageError)
    def test_indexing_same_value_twice(self):
        """
        fun f(mut v: std::vector::Vec[std::string::Str]) -> std::void::Void {
            let e0 = v[mut 0_uz]
            let e1 = v[mut 0_uz]
        }
        """
