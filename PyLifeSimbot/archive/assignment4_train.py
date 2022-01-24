# 1. define scaling function
from typing import Tuple
def scale(data, from_interval: Tuple[float, float], to_interval: Tuple[float, float]=(0, 1)):
    from_min, from_max = from_interval
    to_min, to_max = to_interval
    scaled_data = to_min + (data - from_min) * (to_max - to_min) / (from_max - from_min)
    return scaled_data


# 2. read data
import pandas as pd
## use these lines to read Jet's data. (The raw data must be scaled)
dataframe = pd.read_csv('history_all.csv', sep=',')
dataframe.iloc[:, 0:8] = scale(dataframe.iloc[:, 0:8], from_interval=(0, 100), to_interval=(0,1))
dataframe.iloc[:, 8] = scale(dataframe.iloc[:, 8], from_interval=(-180, 180), to_interval=(0,1))
dataframe.iloc[:, 9:] = scale(dataframe.iloc[:, 9:], from_interval=(-5, 5), to_interval=(0,1))

## use this line to read Jumo's data.
# dataframe = pd.read_csv('Train-2.csv', sep=',', header=None)


# 3. select input and output of the ANN
x = dataframe.iloc[:, :9]
y = dataframe.iloc[:, 9:]


# 4. define ANN architecture, loss and optimizer
from keras.models import Sequential
from keras.layers import Dense
model = Sequential()
model.add(Dense(32, activation='relu', input_shape=(9,)))
model.add(Dense(16, activation='relu'))
model.add(Dense(2, activation='relu'))
model.compile(optimizer='adam', loss='mean_squared_error')


# 5. train ANN model
history = model.fit(x, y, batch_size=1000, epochs=500)


# 6. save model for later usage
model.save('assignment4_model.h5')


# 7. plot the loss value of the training
from matplotlib import pyplot as plt
plt.plot(history.history['loss'])
plt.show()