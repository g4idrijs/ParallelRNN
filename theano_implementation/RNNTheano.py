__author__ = 'Esha Uboweja'

# RNN Implementation in Theano

import numpy as np
import theano
import theano.tensor as TT

class RNNTheano:

    def __init__(self, nh, nin, nout):
        """
        RNN setup using Theano tensor data structures
        :param nh: number of hidden units
        :param nin: number of input units
        :param nout: number of output units
        """
        # Number of hidden units
        self.nh = nh
        # Number of input units
        self.nin = nin
        # Number of output units
        self.nout = nout
        # Input (first dimension is time)
        self.x = TT.matrix()
        # Target (first dimension is time)
        self.t = TT.matrix()
        # Initial hidden state of RNNs
        self.h0 = TT.vector()
        # Learning rate
        self.lr = TT.scalar()
        # Recurrent hidden node weights
        self.W_hh = theano.shared(np.random.uniform(size=(nh, nh),
                                                    low=-0.01,
                                                    high=0.01))
        # Input layer to hidden layer weights
        self.W_xh = theano.shared(np.random.uniform(size=(nin, nh),
                                                    low=-0.01,
                                                    high=0.01))
        # Hidden layer to output layer weights
        self.W_hy = theano.shared(np.random.uniform(size=(nh, nout),
                                                    low=-0.01,
                                                    high=0.01))

        # Compute hidden state and output for the entire input sequence
        # (first dimension is time)
        [self.h, self.y], _ = theano.scan(self.step,
                                          sequences = self.x,
                                          outputs_info=[self.h0, None],
                                          non_sequences=[self.W_hh, self.W_xh,
                                                         self.W_hy])

        # Error between output and target
        self.error = ((self.y - self.t) ** 2).sum()
        # BPTT (back-propagation through time)
        # Gradients
        self.gW_hh, self.gW_xh, self.gW_hy = TT.grad(self.error,
                                                     [self.W_hh, self.W_xh,
                                                      self.W_hy])
        # Training function
        self.train_fn = theano.function(
            [self.h0, self.x, self.t, self.lr],
            [self.error, self.y],
            updates={self.W_hh: self.W_hh - self.lr * self.gW_hh,
                     self.W_xh: self.W_xh - self.lr * self.gW_xh,
                     self.W_hy: self.W_hy - self.lr * self.gW_hy})

    def step(self, x_t, h_tm1, W_hh, W_xh, W_hy):
        """
        Forward step function (recurrent)
        Nonlinear activation function - one of tanh, sigmoid, ReLU
        :param x_t: input at time-step t
        :param h_tm1: hidden state at time-step (t-1)
        :return: h_t: updated hidden state at time-step t
                 y_t: updated output at time-step t
        """
        h_t = TT.tanh(TT.dot(x_t, W_xh) + TT.dot(h_tm1, W_hh))
        y_t = TT.dot(h_t, W_hy)
        return h_t, y_t

    def saveNetwork(self, paramFile):
        """
        Save network parameters, weights
        :return: (Nothing)
        """
        W_hh, W_xh, W_hy = self.W_hh.get_value(), self.W_xh.get_value(), \
                           self.W_hy.get_value()
        np.savez(paramFile, W_hh=W_hh, W_xh=W_xh, W_hy=W_hy)
