# -*- coding: utf-8 -*-
#
import mpmath
from mpmath import mp


# def tanh_sinh_singular(
#         f_left=None,
#         f_right=None,
#         ab=None,
#         eps=None,
#         max_steps=10
#         ):
#     '''Tanh-sinh quadrature for integrands with singularities at the
#     endpoints.
#
#     Background:
#     Since tanh-sinh places its nodes very close to the interval boundaries,
#     it is important to evaluate them with some accuracy. This may become a
#     problem if there are singularities at the boundaries, i.e., if the values
#     change very rapidly. To avoid round-off errors, the user must provide the
#     integrand in terms of distance the left or right hade boundary,
#     respectively. For example, if your integrand is f(t) = sqrt(t / (1-t^2))
#     between 0 and 1, you'll have to provide g(s) = sqrt((1-s) / (2*s - s^2))
#     (where s varies between 0 and 1).
#     If there are singularities on both sides, you can provide both f_left and
#     f_right and it will split the integral in two.
#     '''
#     if f_left and not f_right:
#         value, error = _tanh_sinh(f_left, eps, max_steps=max_steps)
#     elif f_right and not f_left:
#         value, error = _tanh_sinh(f_right, eps, max_steps=max_steps)
#     else:
#         assert f_left and f_right
#         value0, error0 = \
#             _tanh_sinh(f_left, 0, ab/2, eps, max_steps=max_steps)
#         value1, error1 = \
#             _tanh_sinh(f_right, 0, ab/2, eps, max_steps=max_steps)
#         value = value0 + value1
#         error = error0 + error1
#     return value, error


def tanh_sinh_regular(f, a, b, eps, max_steps=10, f_derivatives=None):
    if f_derivatives is None:
        f_derivatives = {}

    def f_left(s):
        return f(a + s*(b-a)/mp.mpf(2))

    def f_right(s):
        return f(b + s*(a-b)/mp.mpf(2))

    f_left_derivatives = {
        k: lambda s: ((b-a)/2)**k * fd(a + s*(b-a)/2)
        for k, fd in f_derivatives.items()
        }
    f_right_derivatives = {
        k: lambda s: ((a-b)/2)**k * fd(a + s*(a-b)/2)
        for k, fd in f_derivatives.items()
        }

    value_estimate, error_estimate = _tanh_sinh(
        f_left, f_right, eps,
        max_steps=max_steps,
        f_left_derivatives=f_left_derivatives,
        f_right_derivatives=f_right_derivatives,
        )
    return value_estimate * (b-a)/2, error_estimate * (b-a)/2


# pylint: disable=too-many-arguments, too-many-locals
def _tanh_sinh(
        f_left, f_right, eps, max_steps=10,
        f_left_derivatives=None,
        f_right_derivatives=None,
        ):
    '''Integrate a function `f` between `a` and `b` with accuracy `eps`. The
    function `f` is given in terms of two functions `f_left` and `f_right`
    where `f_left(s) = f(a - s*(a-b)/2)`, i.e., `f` linearly scaled such that
    `f_left(0) = a`, `f_left(2) = b` (`f_right` likewise).

    Mori, Masatake
    Discovery of the double exponential transformation and its developments,
    Publications of the Research Institute for Mathematical Sciences,
    41 (4): 897–935, ISSN 0034-5318,
    doi:10.2977/prims/1145474600,
    <http://www.kurims.kyoto-u.ac.jp/~okamoto/paper/Publ_RIMS_DE/41-4-38.pdf>.
    '''
    # David H. Bailey, Karthik Jeyabalan, and Xiaoye S. Li,
    # Error function quadrature,
    # Experiment. Math., Volume 14, Issue 3 (2005), 317-329,
    # <https://projecteuclid.org/euclid.em/1128371757>.
    #
    # David H. Bailey,
    # Tanh-Sinh High-Precision Quadrature,
    # 2006,
    # <http://www.davidhbailey.com/dhbpapers/dhb-tanh-sinh.pdf>.

    # assert a < b

    # ab2 = (mp.mpf(b) - a) / 2

    # def fun(t):
    #     return f(a + ab2 * (t+1))

    # fun_derivatives = None
    # if f_derivatives:
    #     fun_derivatives = {
    #         1: (lambda t: ab2**1 * f_derivatives[1](a + ab2*(t+1))),
    #         2: (lambda t: ab2**2 * f_derivatives[2](a + ab2*(t+1))),
    #         }

    num_digits = int(-mp.log10(eps) + 1)
    mpmath.mp.dps = num_digits

    value_estimates = []
    h = mp.mpf(1)
    success = False
    for level in range(max_steps):
        # For h=1, the error estimate is too optimistic. Hence, start with
        # h=1/2 right away.
        h /= 2

        # We would like to calculate the weights until they are smaller than
        # tau = eps**2, i.e.,
        #
        #     h * pi/2 * cosh(h*j) / cosh(pi/2 * sinh(h*j))**2 < tau.
        #
        # To streamline the computation, j is estimated in advance. The only
        # assumption we're making is that h*j>>1 such that exp(-h*j) can be
        # neglected. With this, the above becomes
        #
        #     tau > h * pi/2 * exp(h*j)/2 / cosh(pi/2 * exp(h*j)/2)**2
        #
        # and further
        #
        #     tau > h * pi * exp(h*j) / exp(pi/2 * exp(h*j)).
        #
        # Calling z = - pi/2 * exp(h*j), one gets
        #
        #     tau > -2*h*z / exp(-z)
        #
        # This inequality is fulfilled exactly if z < W(-tau/h/2) with W being
        # the (-1)-branch of the Lambert-W function IF 2*exp(1)*tau < h (which
        # we can assume since `tau` will generally be small). We finally get
        #
        #     j > ln(-W(-tau/h/2) * 2 / pi) / h.
        #
        assert 2*mp.exp(1)*eps**2 < h
        j = int(mp.ln(-mp.lambertw(-eps**2/h/2, -1) * 2 / mp.pi) / h) + 1

        u2 = [mp.pi/2 * mp.sinh(h*jj) for jj in range(j+1)]
        cosh_u2 = [mp.cosh(v) for v in u2]
        weights = [
            h * mp.pi/2 * mp.cosh(h*jj) / v**2
            for jj, v in zip(range(j+1), cosh_u2)
            ]

        # y = 1 - x
        # x = [mp.tanh(v) for v in u2]
        y = [1 / (mp.exp(v) * c) for v, c in zip(u2, cosh_u2)]

        # Perform the integration.
        # The summands are listed such that the points are in ascending order.
        # (The slice expression [-1:0:-1] cuts the first entry and reverses the
        # array.)
        summands = (
            [f_left(yy) * w for yy, w in zip(y[-1:0:-1], weights[-1:0:-1])]
            + [f_right(yy) * w for yy, w in zip(y, weights)]
            )
        value_estimates.append(mp.fsum(summands))

        # error estimation
        # TODO
        if f_left_derivatives:
            assert f_right_derivatives is not None
            error_estimate = _error_estimate1(
                    h, j, f_left, f_right,
                    f_left_derivatives, f_right_derivatives
                    )
        else:
            error_estimate = _error_estimate2(
                level, value_estimates, summands, eps
                )

        # exact = (mp.exp(mp.pi/2) - 1)/2
        exact = mp.mpf(1) / 3
        print(value_estimates[-1] * 0.5, exact)
        print(value_estimates[-1] * 0.5 - exact, error_estimate * 0.5)
        print
        if level == 2:
            exit(1)

        if abs(error_estimate) < eps:
            success = True
            break

    assert success
    return value_estimates[-1], error_estimate


def _error_estimate1(
        h, j, f_left, f_right,
        f_left_derivatives, f_right_derivatives
        ):
    # Pretty accurate error estimation:
    #
    #   E(h) = h * (h/2/pi)**2 * sum_{-N}^{+N} F''(h*j)
    #
    # with
    #
    #   F(t) = f(g(t)) * g'(t),
    #   g(t) = tanh(pi/2 sinh(t)).
    #
    assert 1 in f_left_derivatives
    assert 2 in f_left_derivatives
    assert 1 in f_right_derivatives
    assert 2 in f_right_derivatives

    # TODO
    # # y = 1 - g(t)
    # def y(t):
    #     u2 = mp.pi/2 * mp.sinh(t)
    #     return 1 / (mp.exp(u2) * mp.cosh(u2))

    # def dy_dt(t):
    #     u2 = mp.pi/2 * mp.sinh(t)
    #     return (
    #         mp.pi/2 / mp.exp(u2) * mp.cosh(t) / mp.cosh(u2)
    #         * (mp.tanh(u2) - 1)
    #         )

    # def d2y_dt2(t):
    #     u2 = mp.pi/2 * mp.sinh(t)
    #     return (
    #         mp.pi/2 / mp.exp(u2) * (mp.tanh(u2) + 1) / mp.cosh(u2) * (
    #             mp.pi * mp.cosh(t)**2 * mp.tanh(u2) - mp.sinh(t)
    #             )

    def g(t):
        return mp.tanh(mp.pi/2 * mp.sinh(t))

    def dg_dt(t):
        return mp.pi/2 * mp.cosh(t) / mp.cosh(mp.pi/2 * mp.sinh(t))**2

    def d2g_dt2(t):
        return mp.pi/2 * (
            + mp.sinh(t)
            - mp.pi * mp.cosh(t)**2 * mp.tanh(mp.pi/2 * mp.sinh(t))
            ) / mp.cosh(mp.pi/2 * mp.sinh(t))**2

    def d3g_dt3(t):
        sinh_sinh = mp.sinh(mp.pi/2 * mp.sinh(t))
        cosh_sinh = mp.cosh(mp.pi/2 * mp.sinh(t))
        tanh_sinh = mp.tanh(mp.pi/2 * mp.sinh(t))
        return mp.pi/4 * mp.cosh(t) * (
            + 2 * cosh_sinh
            - 2 * mp.pi**2 * mp.cosh(t)**2 / cosh_sinh
            + mp.pi**2 * mp.cosh(t)**2 * cosh_sinh
            + mp.pi**2 * mp.cosh(t)**2 * tanh_sinh * sinh_sinh
            - 6 * mp.pi * mp.sinh(t) * sinh_sinh
            ) / cosh_sinh**3

    # TODO reuse g*
    def F2(f, fd, t):
        '''Second derivative of F(t) = f(g(t)) * g'(t).
        '''
        gt = g(t)
        g1 = dg_dt(t)
        g2 = d2g_dt2(t)
        g3 = d3g_dt3(t)
        return (
            - g1**3 * fd[2](1 - gt)
            - 3 * g1 * g2 * fd[1](1 - gt)
            - g3 * f(1 - gt)
            )

    t = [h * jj for jj in range(j+1)]
    # print(f_left(1))
    # print(f_right(1))
    summands = (
        [F2(f_left, f_left_derivatives, tt) for tt in t[1:]]
        + [F2(f_right, f_right_derivatives, tt) for tt in t]
        )

    return h * (h/2/mp.pi)**2 * mp.fsum(summands)


def _error_estimate2(level, value_estimates, summands, eps):
    # "less formal" error estimation after Bailey,
    # <http://www.davidhbailey.com/dhbpapers/dhb-tanh-sinh.pdf>
    if level <= 1:
        error_estimate = 1
    elif value_estimates[0] == value_estimates[-1]:
        error_estimate = 0
    else:
        # d1 = mp.log10(abs(value_estimates[-1] - value_estimates[-2]))
        # d2 = mp.log10(abs(value_estimates[-1] - value_estimates[-3]))
        # d3 = mp.log10(eps * max([abs(x) for x in summands]))
        # d4 = mp.log10(max(abs(summands[0]), abs(summands[-1])))
        # d = max(d1**2 / d2, 2*d1, d3, d4)
        # error_estimate = 10**d
        e1 = abs(value_estimates[-1] - value_estimates[-2])
        e2 = abs(value_estimates[-1] - value_estimates[-3])
        e3 = eps * max([abs(x) for x in summands])
        e4 = max(abs(summands[0]), abs(summands[-1]))
        error_estimate = max(e1**(mp.log(e1)/mp.log(e2)), e1**2, e3, e4)

    return error_estimate
