from operator import mul


def dot(cord, matrix):
    """
    Perform dot production.
    :param matrix: affine matrix
    :param cord: origin coordinate
    :return: destination coordinate
    """
    return [sum(map(mul, row, cord)) for row in matrix]
