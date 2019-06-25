# -*- coding: utf-8 -*-
#
import numpy


class EnrScheme(object):
    def __init__(self, name, dim, weights, points, degree, citation):
        self.name = name
        self.dim = dim
        self.weights = weights
        self.points = points
        self.degree = degree
        self.citation = citation
        return

    def integrate(self, f, dot=numpy.dot):
        flt = numpy.vectorize(float)
        return dot(f(flt(self.points).T), flt(self.weights))