class CommonTypes:
    @staticmethod
    def Self(pos: int = -1):
        from SPPCompiler.SemanticAnalysis import GenericIdentifierAst, TypeAst
        return TypeAst(pos, [], [GenericIdentifierAst(pos, "Self", None)])
