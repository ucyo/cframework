#!/usr/bin/env python
# coding: utf-8

from cframe.backend.predictormod import MixedPredictor


class MostRight(MixedPredictor):

    name = 'Most Right'

    def __init__(self, predictors, *args, **kwargs):
        self.predictors = {i: x(*args, **kwargs) for i,x in enumerate(predictors)}
        self.counter = {k: 0 for k in self.predictors.keys()}
        self.lastbest = 0
        self.overallbest = self.lastbest

    def predict(self):
        return self.predictors[self.overallbest].predict()

    def update(self, val):
        # everyone makes their predictions
        predictions = {k: v.predict() for k, v in self.predictors.items()}

        # calculate error, sort by decreasing errors
        errors = {k: (val - v) if val>v else (v-val) for k, v in predictions.items()}
        self.lastbest = sorted(
            errors.items(), key=lambda x: x[1], reverse=False)[0][0]

        # update overall best
        self.counter[self.lastbest] += 1
        self.overallbest = sorted(
            self.counter.items(), key=lambda x: x[1], reverse=True)[0][0]

        # update predictors
        for _, pred in self.predictors.items():
            pred.update(val)


class LastBest(MixedPredictor):

    name = 'LastBest'

    def __init__(self, predictors, *args, **kwargs):
        self.predictors = {i: x(*args, **kwargs) for i,x in enumerate(predictors)}
        self.counter = {k: 0 for k in self.predictors.keys()}
        self.lastbest = 0

    def predict(self):
        return self.predictors[self.lastbest].predict()

    def update(self, val):
        # everyone makes their predictions
        predictions = {k: v.predict() for k, v in self.predictors.items()}

        # calculate error, sort by decreasing errors
        errors = {k: (val - v) if val>v else (v-val) for k, v in predictions.items()}
        self.lastbest = sorted(
            errors.items(), key=lambda x: x[1], reverse=False)[0][0]

        # update predictors
        for _, pred in self.predictors.items():
            pred.update(val)
