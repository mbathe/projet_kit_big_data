
from keras import models, layers
from keras import optimizers

from keras import datasets, utils
NUM_CLASSES = 10

(x_train, y_train), (x_test, y_test) = datasets.cifar10.load_data()



x_train = x_train.astype('float32') / 255.0
x_test = x_test.astype('float32') / 255.0
y_train = utils.to_categorical(y_train, NUM_CLASSES)
y_test = utils.to_categorical(y_test, NUM_CLASSES)

input_layer = layers.Input(shape=(32, 32,3))
x= layers.Flatten()(input_layer)
x = layers.Dense(units=200, activation="relu")(x)
x = layers.Dense(units=150, activation="relu")(x)
x = layers.Dense(100, activation="relu")(x)

output_layer = layers.Dense(units=10, activation="softmax")(x)
model = models.Model(input_layer, output_layer)

opt = optimizers.Adam(learning_rate=0.0005)
model.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])

model.fit(x_train, y_train, epochs=10, batch_size=128, shuffle=True)

model.evaluate(x_test, y_test)