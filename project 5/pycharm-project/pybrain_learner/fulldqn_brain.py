from keras.models import Sequential
from keras.layers import *
from keras.optimizers import *

import random, numpy, math, gym, sys

def hubert_loss(y_true, y_pred):    # sqrt(1+a^2)-1
    err = y_pred - y_true
    return K.mean( K.sqrt(1+K.square(err))-1, axis=-1 )

class FullDqnBrain:
    def __init__(self, stateCnt, actionCnt):
        self.stateCnt = stateCnt
        self.actionCnt = actionCnt

        self.model = self._createModel()
        self.model_ = self._createModel()

    def _createModel(self):
        model = Sequential()

        model.add(Dense(output_dim=64, activation='relu', input_dim=self.stateCnt))
        model.add(Dense(output_dim=self.actionCnt, activation='linear'))

        opt = RMSprop(lr=0.00025)
        model.compile(loss=hubert_loss, optimizer=opt)

        return model

    def train(self, x, y, epoch=1, verbose=0):
        self.model.fit(x, y, batch_size=64, nb_epoch=epoch, verbose=verbose)

    def predict(self, s, target=False):
        if target:
            return self.model_.predict(s)
        else:
            return self.model.predict(s)

    def predictOne(self, s, target=False):
        return self.predict(s.reshape(1, self.stateCnt), target=target).flatten()

    def updateTargetModel(self):
        self.model_.set_weights(self.model.get_weights())