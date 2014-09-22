#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
from custommath import *
def TestWeightedMedian():
    data = [
        [7, 1, 2, 4, 10],
        [7, 1, 2, 4, 10],
        [7, 1, 2, 4, 10, 15],
        [1, 2, 4, 7, 10, 15],
        [0, 10, 20, 30],
        [1, 2, 3, 4, 5],
    ]
    weights = [
        [1, 1/3, 1/3, 1/3, 1],
        [1, 1, 1, 1, 1],
        [1, 1/3, 1/3, 1/3, 1, 1],
        [1/3, 1/3, 1/3, 1, 1, 1],
        [30, 191, 9, 0],
        [10, 1, 1, 1, 9],
    ]
    answers = [7, 4, 8.5, 8.5, 10, 2.5]
    for datum, weight, answer in zip(data, weights, answers):
        assert(WeightedMedian(datum, weight) == answer)
        try:
            assert(JackWeightedMedian(datum, weight) == answer)
        except:
            print('datum: ' +str(datum))
            print('weight: ' +str(weight))
            print('weighted_median: ' +str(WeightedMedian(datum, weight)))
            print('jack_weighted_median: ' +str(JackWeightedMedian(datum, weight)))
            
        #assert(weighted_median(datum, weight) == answer)

if __name__ == "__main__":
    TestWeightedMedian()
