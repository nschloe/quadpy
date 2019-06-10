# -*- coding: utf-8 -*-
#
from __future__ import division

import numpy
import sympy

from ..helpers import untangle


class KubatkoYeagerMaggi(object):
    """
    Ethan J. Kubatko, Benjamin A. Yeager, Ashley L. Maggi,
    New computationally efficient quadrature formulas for triangular prism elements,
    Computers & Fluids 73 (2013) 187–201,
    <https://doi.org/10.1016/j.compfluid.2013.01.002>.
    """

    def __init__(self, index):
        symbolic = False
        frac = sympy.Rational if symbolic else lambda x, y: x / y
        sqrt = numpy.vectorize(sympy.sqrt) if symbolic else numpy.sqrt

        if index == "1":
            self.degree = 1
            data = [(4, [[-frac(1, 3), -frac(1, 3), 0]])]
        elif index == "2a":
            self.degree = 2
            data = [
                (1, [[0.483163247594393, -0.741581623797196, 0]]),
                (1, [[-0.605498860309242, 0.469416096821288, 0]]),
                (
                    1,
                    _zeta_pm(-0.605498860309242, -0.530583903178712, 0.816496580927726),
                ),
            ]
        elif index == "2b":
            self.degree = 2
            data = [
                (frac(1, 3), _s21(-1)),
                (frac(3, 2), _s3_z(frac(2, 3), symbolic)),
            ]
        elif index == "3a":
            self.degree = 3
            data = [
                (
                    0.742534890852309,
                    [[0.240692796349625, -0.771991660873412, 0.614747128207527]],
                ),
                (
                    0.375143463443327,
                    [[-0.968326281451138, -0.568046512457875, 0.676689529541421]],
                ),
                (
                    0.495419047908462,
                    [[0.467917833640195, -0.549342790168347, -0.599905857322635]],
                ),
                (
                    0.523999970843238,
                    [[-0.786144119530819, 0.362655041695561, -0.677609795694786]],
                ),
                (
                    0.980905839025611,
                    [[-0.484844897886675, -0.707931130717342, -0.502482717716373]],
                ),
                (
                    0.881996787927053,
                    [[-0.559053711932125, 0.260243325246813, 0.493010512161538]],
                ),
            ]
        elif index == "3b":
            self.degree = 3
            data = [
                (-frac(43, 12), _s3(symbolic)),
                (frac(25, 12), _s21(-frac(3, 5))),
                (frac(2, 3), _s3_z(1, symbolic)),
            ]
        elif index == "3c":
            self.degree = 3
            alpha = 4 * sqrt(3) / 15
            data = [
                (-frac(9, 4), _s3(symbolic)),
                (frac(25, 24), _s21_z(-frac(3, 5), alpha)),
            ]
        elif index == "3d":
            self.degree = 3
            alpha = 0.525248027124695
            beta = 0.924672547414225
            gamma = 0.449920574538920
            data = [
                (frac(4, 9), [[-alpha, -beta, 0]]),
                (frac(4, 9), [[gamma, -beta, 0]]),
                (frac(4, 9), [[gamma, -alpha, 0]]),
                (frac(4, 9), [[-alpha, gamma, 0]]),
                (frac(4, 9), [[-beta, gamma, 0]]),
                (frac(4, 9), [[-beta, -alpha, 0]]),
                (frac(2, 3), _s3_z(1, symbolic)),
            ]
        elif index == "4a":
            self.degree = 4
            data = [
                (0.111155943811228, [[0.812075900047562, -0.986242751499303, 0.850716248413834]]),
                (0.309060899887509, [[-0.792166223585545, 0.687201105597868, -0.115214772515700]]),
                (0.516646862442958, [[-0.756726179789306, -0.731311840596107, -0.451491675441927]]),
                (0.567975205132714, [[-0.552495167978340, 0.015073398439985, -0.824457000064439]]),
                (0.382742555939017, [[-0.357230019521233, 0.126888850505978, 0.855349689995606]]),
                (0.355960928492268, [[-0.987225392999058, 0.082647545710800, 0.452976444667786]]),
                (0.108183228294342, [[-0.816603728785918, -0.915066171481315, 0.997939285245240]]),
                (0.126355242780924, [[0.423489172633859, -1.112801167237130, -0.963298774205756]]),
                (0.587370828592853, [[0.363041084609230, -0.499011410082669, -0.299892769705443]]),
                (0.934548304626188, [[-0.175780343149613, -0.654971142379686, 0.367947041936472]]),
            ]
        elif index == "4b":
            self.degree = 4
            data = [
                (0.545658450421913, _s21(-0.062688380276010)),
                (0.431647899262139, _s3_z(0.866861974009030, symbolic)),
                (0.249954808368331, _s21_z(-0.798519188402179, 0.675639823682265)),
            ]
        else:
            assert False

        self.points, self.weights = untangle(data)
        # quadpy's reference wedge is 0 <= X, 0 <= Y, X + Y <= 1, -1 <= Z <= 1.
        self.weights = self.weights / 4
        self.points[:, :2] += 1
        self.points[:, :2] /= 2
        return


def _zeta_pm(xi, eta, zeta):
    return [[xi, eta, +zeta], [xi, eta, -zeta]]


def _s3(symbolic):
    frac = sympy.Rational if symbolic else lambda x, y: x / y
    return [[-frac(1, 3), -frac(1, 3), 0]]


def _s3_z(z, symbolic):
    frac = sympy.Rational if symbolic else lambda x, y: x / y
    return [[-frac(1, 3), -frac(1, 3), +z], [-frac(1, 3), -frac(1, 3), -z]]


def _s21(a):
    b = -(1 + 2 * a)
    return [[a, b, 0], [b, a, 0], [a, a, 0]]


def _s21_z(a, z):
    b = -(1 + 2 * a)
    return [[a, b, +z], [b, a, +z], [a, a, +z], [a, b, -z], [b, a, -z], [a, a, -z]]


def _s111_z(a, b, z):
    c = 1 - a - b
    return [
        [b, c, +z],
        [a, b, +z],
        [c, a, +z],
        [c, b, +z],
        [a, c, +z],
        [b, a, +z],
        [b, c, -z],
        [a, b, -z],
        [c, a, -z],
        [c, b, -z],
        [a, c, -z],
        [b, a, -z],
    ]
