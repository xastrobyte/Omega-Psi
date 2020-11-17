from .matrix import Matrix

class Span:
    """
    """

    def __init__(self, matrix: Matrix=None, *, vectors: list=None):
        if matrix is None and vectors is None:
            raise AttributeError("Matrix or Vector parameter must be specified")
        elif matrix is None:
            matrix = Matrix(vectors)
        self.__matrix = matrix
        self.__size = len(matrix)
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    def __str__(self) -> str:
        matrix_split = str(self.__matrix).split("\n")
        return "\n".join([
            ("span " if i == 0 else "".center(len("span "))) +
            matrix_split[i]
            for i in range(len(matrix_split))
        ])
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    def simplify(self) -> 'Span':
        """Returns a simpler spanning set, if possible
        by getting the Linearly Independent vectors from
        a RREF Matrix of the Vectors in this Spanning set
        """

        li_vectors = self.__matrix.get_li_vectors()
        return Span(vectors = [
            self.__matrix[i]
            for i in li_vectors
        ])
    