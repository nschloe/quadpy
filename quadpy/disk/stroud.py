# -*- coding: utf-8 -*-
#
from __future__ import division

import numpy
import sympy

from .albrecht import Albrecht
from .albrecht_collatz import AlbrechtCollatz
from .hammer_stroud import HammerStroud
from .mysovskih import Mysovskih
from .peirce1956 import Peirce1956
from .rabinowitz_richter import RabinowitzRichter
from .radon import Radon

from ..helpers import z, fsd, pm, untangle


class Stroud(object):
    """
    Arthur Stroud,
    Approximate Calculation of Multiple Integrals,
    Prentice Hall, 1971.
    """

    def __init__(self, index, symbolic=False):
        self.name = "Stroud({})".format(index)

        d = {
            "S2 3-1": (HammerStroud, ["11-2", symbolic]),
            "S2 3-2": (AlbrechtCollatz, [symbolic]),
            "S2 4-1": (Mysovskih, [1, symbolic]),
            "S2 5-1": (Radon, [0, symbolic]),
            "S2 5-2": (StroudS252, [symbolic]),
            "S2 7-1": (Peirce1956, [1, symbolic]),
            "S2 7-2": (SphericalProductGauss, [7, symbolic]),
            "S2 9-1": (Albrecht, [4, symbolic]),
            "S2 9-2": (RabinowitzRichter, [1]),
            "S2 9-3": (SphericalProductGauss, [9, symbolic]),
            "S2 9-4": (RabinowitzRichter, [2]),
            "S2 9-5": (Peirce1956, [2, symbolic]),
            "S2 11-1": (Mysovskih, [2, symbolic]),
            "S2 11-2": (Albrecht, [5, symbolic]),
            "S2 11-3": (RabinowitzRichter, [4]),
            "S2 11-4": (Peirce1956, [3, symbolic]),
            "S2 13-1": (RabinowitzRichter, [5]),
            "S2 13-2": (Albrecht, [6, symbolic]),
            "S2 15-1": (Mysovskih, [3, symbolic]),
            "S2 15-2": (Albrecht, [7, symbolic]),
            "S2 17-1": (Albrecht, [8, symbolic]),
        }

        fun, args = d[index]
        scheme = fun(*args)

        self.degree = scheme.degree
        self.weights = scheme.weights
        self.points = scheme.points
        return


class StroudS252(object):
    def __init__(self, symbolic):
        frac = sympy.Rational if symbolic else lambda x, y: x / y
        pi = sympy.pi if symbolic else numpy.pi
        sqrt = numpy.vectorize(sympy.sqrt) if symbolic else numpy.sqrt

        self.degree = 5
        r = sqrt(frac(1, 2))
        data = [
            (frac(1, 6), z(2)),
            (frac(1, 6), fsd(2, (r, 1))),
            (frac(1, 24), pm(2, r)),
        ]
        self.points, self.weights = untangle(data)
        self.weights *= pi
        return


class SphericalProductGauss(object):
    def __init__(self, degree, symbolic):
        sqrt = numpy.vectorize(sympy.sqrt) if symbolic else numpy.sqrt
        pm_ = numpy.array([+1, -1])
        cos = numpy.vectorize(sympy.cos) if symbolic else numpy.cos
        sin = numpy.vectorize(sympy.sin) if symbolic else numpy.sin
        frac = sympy.Rational if symbolic else lambda x, y: x / y
        pi = sympy.pi if symbolic else numpy.pi

        self.degree = degree

        if degree == 7:
            r1, r2 = sqrt((3 - pm_ * sqrt(3)) / 6)

            a = (2 * numpy.arange(8) + 1) * pi / 8
            x = numpy.array([cos(a), sin(a)]).T

            data = [(frac(1, 16), r1 * x), (frac(1, 16), r2 * x)]
            self.points, self.weights = untangle(data)
        else:
            assert degree == 9
            r1, r2 = sqrt((6 - pm_ * sqrt(6)) / 10)

            a = (numpy.arange(10) + 1) * pi / 5
            x = numpy.array([cos(a), sin(a)]).T

            B0 = frac(1, 9)
            B1, B2 = (16 + pm_ * sqrt(6)) / 360

            data = [(B0, z(2)), (B1, r1 * x), (B2, r2 * x)]
            self.points, self.weights = untangle(data)
            self.weights *= pi

        self.weights *= pi
        return
