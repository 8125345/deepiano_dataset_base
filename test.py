import numpy as np
import collections

data = np.arange(0, 20).reshape(4, 5)
print(data)
print(data.shape)
data_reshape = data[:, 1]
print(data_reshape)
# count = collections.Counter(data.flatten())
# print(count)

