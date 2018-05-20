#! -*- coding: UTF-8 -*-
import tensorflow as tf
import numpy as np
import string, re

# All valid characters.
alphabet = string.ascii_uppercase + string.ascii_lowercase + "ĞÖÇİÜŞğöoçıüş"
alphabetSize = len(alphabet)

languages = ["English", "Turkish"]
languageCount = len(languages)

# Load data.
X = np.load("X.npy")
y = np.load("y.npy")

# General variables.
exampleCount = X.shape[0]
epochs = 10000
hiddenLayerSize = 256
learningRate = 0.01

# Word filter. Deletes unwanted char from given string.
def wordFilter(x):
	# String only can contain lowercase, uppercase letters, Turkish alphabet letters and spaces.
	x = re.sub(r"""[^A-Za-zĞÖÇİÜŞğöoçıüş]""", "", x)
	x = x.strip()
	return x

# Decodes sequence for given matrix. Parameter should have (Batch, Timestep, Features) shape.
def decodeSeq(x):
	x = x[0]
	text = ""

	# For each timstep.
	for t in range(0, x.shape[0]):
		# Find the highest value on vector, and give it's index.
		ind = np.argmax(x[t])

		# And take back the word from vocabulary.
		text += alphabet[ind]
	text = text.strip()
	return text

# xx_n has shape (Batch, Timestep)
# yy_n has shape (Batch)

# xx_n has integers for each timestep, which going to be converted to one-hot vector with xx tensor.
# yy_n has just an 1 integer for last timestep. (Many-to-One)
# Also this is going to be converted to one-hot vector with yy tensor.
xx_n = tf.placeholder(tf.int32, shape=(None, None))
yy_n = tf.placeholder(tf.int32, shape=(None))

xx = tf.one_hot(xx_n, alphabetSize)
yy = tf.one_hot(yy_n, languageCount)

# BasicLSTMCell used as RNN cell.
lstm_cell = tf.nn.rnn_cell.BasicLSTMCell(hiddenLayerSize)
out, state = tf.nn.dynamic_rnn(lstm_cell, xx, dtype=tf.float32)
logits = tf.layers.dense(out, units=languageCount)

# All we care about is last output of the network. (Many-to-One)
lastOutput = logits[0][-1]

# This loss function takes input, applies Softmax to it.
# And calculates loss from given target values.
loss = tf.losses.softmax_cross_entropy(logits=lastOutput, onehot_labels=yy)
optimizer = tf.train.AdamOptimizer(learningRate)
train = optimizer.minimize(loss)

# This tensor going to be used in testing.
# Softmax is already calculating by loss function during training.
prediction = tf.nn.softmax(lastOutput)

sess = tf.Session()
sess.run(tf.global_variables_initializer())

# Train!
dataIndex = 0
for e in range(0, epochs):
	batch_x = X[dataIndex]
	batch_y = y[dataIndex]

	# batch_x has shape (Timestep) right now.
	# We should reshape it to (Batch, Timestep) for matching placeholder's shape.
	batch_x = batch_x.reshape((1,) + batch_x.shape)
	batch_y = batch_y.reshape((1,) + batch_y.shape)

	# Next example.
	dataIndex += 1

	# We went through all the dataset? Reset it.
	if dataIndex >= exampleCount:
		dataIndex = 0

	feed = {
		xx_n:batch_x,
		yy_n:batch_y
	}

	sess.run(train, feed_dict=feed)

	# At every %1 progress, print loss and predict a random example.
	if e%(epochs/100) == 0:
		print("Epoch:", e)
		print("Current batch loss:", sess.run(loss, feed_dict=feed), "\n")

		batch_x_onehot, batch_y_onehot, pred = sess.run([xx, yy, prediction], feed_dict=feed)

		for i, lang in enumerate(languages):
			print(lang + ": %" + str(format(pred[i]*100, "3.3")))

		seqText = decodeSeq(batch_x_onehot)
		langText = languages[np.argmax(pred)]
		
		print(seqText, langText)
		print("-----------------------")

# Training done! Let's test our model by hand.
while True:
	inW = wordFilter(input(">> "))

	xx = []
	for inL in inW:
		xx.append(alphabet.index(inL))
	xx = np.array(xx)

	batch_x = xx
	batch_x = batch_x.reshape((1,) + batch_x.shape)

	feed = {
		xx_n:batch_x
	}

	pred = sess.run(prediction, feed_dict=feed)
	for i, lang in enumerate(languages):
		print(lang + ": %" + str(format(pred[i]*100, "3.3")))

	langText = languages[np.argmax(pred)]

	print(inW, langText)
	print("-----------------------")