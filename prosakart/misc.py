from typing import List


def linspace(
        start: float, stop: float, n: int, rounded: bool = False
) -> List[float]:
    """
    An alternative to numpy.linspace to avoid relying on non-stdlib
    libraries.
    :param start: float
        The starting position.
    :param stop: float
        The stopping position.
    :param n: int
        The number of points.
    :param rounded: bool
        Whether or not to return integer values.
    :return: List[float]
        A list of points.
    """
    assert start < stop and n > 2
    return list(map(
        int if rounded else float,
        (start + (stop - start) / (n - 1) * i for i in range(n))
    ))
