'''
Tensorflow GRU-RNN Portfolio Manager
'''


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import tensorflow as tf


class GRU_Manager:

    def __init__(self, df, hidden_units=None, batch_size=256, epochs=200, buffer=10000):

        self.stocks = df.copy()

        #Define partition constants
        TRAIN_SIZE = int(0.80*len(self.stocks.index))
        VALID_SIZE = int(0.20*len(self.stocks.index))
        self.BATCH_SIZE = batch_size
        self.BUFFER_SIZE = buffer
        self.EPOCHS = epochs
        self.EPOCH_TRAIN_STEPS = TRAIN_SIZE/self.BATCH_SIZE
        self.EPOCH_VALID_STEPS = VALID_SIZE/self.BATCH_SIZE

        self.X_train, self.y_train = self._process_data(self.stocks,end_index=TRAIN_SIZE)
        self.X_val, self.y_val = self._process_data(self.stocks,start_index=TRAIN_SIZE)

        self.train_data = self._convert_to_tensor(self.X_train, self.y_train)
        self.val_data = self._convert_to_tensor(self.X_val, self.y_val, validation_data=True)

        if hidden_units == None:
            inpt = self.X_train.shape[-2:]
            hidden_units = int((2/3)*(inpt[0]*inpt[1]+self.y_val.shape[-1:][0]))

        self.model = self._build_model(hidden_units)

        self.history = self.model.fit(self.train_data, 
                                      epochs=self.EPOCHS,
                                      steps_per_epoch=self.EPOCH_TRAIN_STEPS,
                                      validation_data=self.val_data,
                                      validation_steps=self.EPOCH_VALID_STEPS
                                      )

    #-----------------------------------------------------#
    #                  Data Processing Funcs              #       
    #-----------------------------------------------------#

    def _process_data(self, df, start_index=1, end_index=None, history_size = 5,step = 1):
  
        if not isinstance(df, pd.DataFrame):
            raise ValueError("data must be of type pandas.DataFrame")

        x = []
        y = []

        #time t-history size 
        start_index = start_index+history_size
        if end_index is None:
            end_index = len(df.index)-1

        #window slices of data
        for i in range(start_index, end_index):
            indices = range(i-history_size, i, step)
            x.append(df.iloc[indices].to_numpy())
            y.append(df.iloc[i].to_numpy())

        return np.array(x), np.array(y)        

    def _convert_to_tensor(self, X, y, validation_data=False):

        if not isinstance(X, np.ndarray):
            raise ValueError("Error in data processing. Not of type numpy.ndArray")
        
        data = None

        if not validation_data:
            data = tf.data.Dataset.from_tensor_slices((X,y))
            data = data.cache().shuffle(self.BUFFER_SIZE).batch(self.BATCH_SIZE).repeat()
        else:
            data = tf.data.Dataset.from_tensor_slices((X, y))
            data = data.batch(self.BATCH_SIZE).repeat()
        return data

    #-----------------------------------------------------#
    #                  ML Model Functions                 #       
    #-----------------------------------------------------#

    def _build_model(self, units):
        model = tf.keras.models.Sequential()
        model.add(tf.keras.layers.GRU(units,
                                      input_shape=self.X_train.shape[-2:],
                                      activation='relu',
                                      return_sequences=True))
        model.add(tf.keras.layers.GRU(int(units/2),
                                      activation='relu'))
        model.add(tf.keras.layers.Dense(self.y_val.shape[-1:][0]))
        model.compile(optimizer=tf.keras.optimizers.RMSprop(), loss='mse', metrics=['accuracy'])
        model.summary()

        return model

    #-----------------------------------------------------#
    #                  Plotting Functions                 #       
    #-----------------------------------------------------#

    def plot_train_history(self):
        loss = self.history.history['loss']
        val_loss = self.history.history['val_loss']

        epochs = range(len(loss))

        plt.figure()

        plt.plot(epochs, loss, 'b', label='Training loss')
        plt.plot(epochs, val_loss, 'r', label='Validation loss')
        plt.title("GRU-RNN")
        plt.legend()

        plt.show()

    def plot_predicted(self):
        for x,y in self.val_data.take(1):
            true = y[:,-1]
            pred = self.model.predict(x)[:,-1]

        df = pd.DataFrame({'true':true,'predicted':pred})
        df.plot()
        plt.show()