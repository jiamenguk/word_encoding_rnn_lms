# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Example / benchmark for building a PTB LSTM model.

Trains the model described in:
(Zaremba, et. al.) Recurrent Neural Network Regularization
http://arxiv.org/abs/1409.2329

There are 3 supported model configurations:
===========================================
| config | epochs | train | valid  | test
===========================================
| small  | 13     | 37.99 | 121.39 | 115.91
| medium | 39     | 48.45 |  86.16 |  82.07
| large  | 55     | 37.87 |  82.62 |  78.29
The exact results may vary depending on the random initialization.

The hyperparameters used in the model:
- init_scale - the initial scale of the weights
- learning_rate - the initial value of the learning rate
- max_grad_norm - the maximum permissible norm of the gradient
- num_layers - the number of LSTM layers
- num_steps - the number of unrolled steps of LSTM
- hidden_size - the number of LSTM units
- max_epoch - the number of epochs trained with the initial learning rate
- max_max_epoch - the total number of epochs for training
- keep_prob - the probability of keeping weights in the dropout layer
- lr_decay - the decay of the learning rate for each epoch after "max_epoch"
- batch_size - the batch size

The data required for this example is in the data/ dir of the
PTB dataset from Tomas Mikolov's webpage:

$ wget http://www.fit.vutbr.cz/~imikolov/rnnlm/simple-examples.tgz
$ tar xvf simple-examples.tgz

To run:

$ python ptb_word_lm.py --data_path=simple-examples/data/

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from random import shuffle

import time, os, json

import numpy as np
import math
import tensorflow as tf

# from tensorflow.models.rnn.ptb import reader
import reader

flags = tf.flags
logging = tf.logging

flags.DEFINE_string("data_path", None, "data_path")
flags.DEFINE_string("train_path", "/tmp", "Training directory.")
flags.DEFINE_string("wmap_path", None, "Word mapping path.")
flags.DEFINE_string("outfile", None, "Output file path.")
flags.DEFINE_boolean("decode", False, "Set to True for interactive decoding.")
flags.DEFINE_boolean("perpcal", False, "Set to True for interactive decoding.")

FLAGS = flags.FLAGS

class PTBModel(object):
  """The PTB model."""

  def __init__(self, is_training, is_testing, config):
    self.batch_size = batch_size = config.batch_size
    self.num_steps = num_steps = config.num_steps
    size = config.hidden_size
    # size = [size[0]]+size
    vocab_size = config.vocab_size

    self._input_data = tf.placeholder(tf.int32, [batch_size, num_steps])
    self._targets = tf.placeholder(tf.int32, [batch_size, num_steps])
    # self._input_data = tf.placeholder(tf.int32, [batch_size, num_steps])
    # self._targets = tf.placeholder(tf.int32, [batch_size, num_steps])

    # Slightly better results can be obtained with forget gate biases
    # initialized to 1 but the hyperparameters of the model would need to be
    # different than reported in the paper.
    # lstm_cell = [tf.nn.rnn_cell.BasicLSTMCell(n, input_size=size[i-1], forget_bias=0.0) for i,n in enumerate(size[1:])]
    lstm_cell = tf.nn.rnn_cell.BasicLSTMCell(size, forget_bias=1.0)
    # lstm_cell = tf.nn.rnn_cell.BasicLSTMCell(size, forget_bias=0.0)
    if is_training and config.keep_prob < 1:
      lstm_cell = tf.nn.rnn_cell.DropoutWrapper(
          lstm_cell, output_keep_prob=config.keep_prob)
    cell = tf.nn.rnn_cell.MultiRNNCell([lstm_cell] * config.num_layers)
    # cell = tf.nn.rnn_cell.MultiRNNCell(lstm_cell)

    self._initial_state = cell.zero_state(batch_size, tf.float32)
    # self._initial_state = cell.zero_state(batch_size, tf.float16)

    with tf.device("/cpu:0"):
      embedding = tf.get_variable("embedding", [vocab_size, size])
      inputs = tf.nn.embedding_lookup(embedding, self._input_data)

    if is_training and config.keep_prob < 1:
      inputs = tf.nn.dropout(inputs, config.keep_prob)

    # Simplified version of tensorflow.models.rnn.rnn.py's rnn().
    # This builds an unrolled LSTM for tutorial purposes only.
    # In general, use the rnn() or state_saving_rnn() from rnn.py.
    #
    # The alternative version of the code below is:
    #
    # from tensorflow.models.rnn import rnn
    # inputs = [tf.squeeze(input_, [1])
    #           for input_ in tf.split(1, num_steps, inputs)]
    # outputs, state = rnn.rnn(cell, inputs, initial_state=self._initial_state)
    outputs = []
    state = self._initial_state
    self.init_state = self._initial_state
    with tf.variable_scope("RNN"):
      for time_step in range(num_steps):
        if time_step > 0: tf.get_variable_scope().reuse_variables()
        (cell_output, state) = cell(inputs[:, time_step, :], state)
        outputs.append(cell_output)

    output = tf.reshape(tf.concat(1, outputs), [-1, size])
    softmax_w = tf.get_variable("softmax_w", [size, vocab_size])
    softmax_b = tf.get_variable("softmax_b", [vocab_size])
    logits = tf.matmul(output, softmax_w) + softmax_b
    self._outputlayer = tf.nn.softmax(logits)
    self._loss = loss = tf.nn.seq2seq.sequence_loss_by_example(
        [logits],
        [tf.reshape(self._targets, [-1])],
        [tf.ones([batch_size * num_steps])])
    self._cost = cost = tf.reduce_sum(loss) / batch_size
    self._final_state = state
    self.saver = tf.train.Saver(tf.all_variables())

    if not is_training:
      return

    self._lr = tf.Variable(0.0, trainable=False)
    tvars = tf.trainable_variables()
    grads, _ = tf.clip_by_global_norm(tf.gradients(cost, tvars),
                                      config.max_grad_norm)
    # optimizer = tf.train.AdadeltaOptimizer(self.lr)
    optimizer = tf.train.AdagradOptimizer(self.lr)
    self._train_op = optimizer.apply_gradients(zip(grads, tvars))

  def assign_lr(self, session, lr_value):
    session.run(tf.assign(self.lr, lr_value))

  @property
  def input_data(self):
    return self._input_data

  @property
  def targets(self):
    return self._targets

  @property
  def initial_state(self):
    return self._initial_state

  @property
  def cost(self):
    return self._cost

  @property
  def loss(self):
    return self._loss

  @property
  def final_state(self):
    return self._final_state

  @property
  def outputlayer(self):
    return self._outputlayer

  @property
  def lr(self):
    return self._lr

  @property
  def train_op(self):
    return self._train_op

class MediumConfig(object):
  """Medium config."""
  init_scale = 0.05
  learning_rate = 0.2
  max_grad_norm = 1
  num_layers = 3
  num_steps = 20
  hidden_size = 1024
  max_epoch = 10
  max_max_epoch = 40
  keep_prob = 0.5
  lr_decay = 0.8
  batch_size = 256
  vocab_size = 30500


class TestConfig(object):
  """Tiny config, for testing."""
  init_scale = 0.1
  learning_rate = 1.0
  max_grad_norm = 1
  num_layers = 1
  num_steps = 2
  hidden_size = 2
  max_epoch = 1
  max_max_epoch = 1
  keep_prob = 1.0
  lr_decay = 0.5
  batch_size = 20
  vocab_size = 10000



def run_epoch(session, model, data, eval_op, verbose=False):
  """Runs the model on the given data."""
  epoch_size = ((sum([len(i) for i in data]) // model.batch_size) - 1) // model.num_steps
  start_time = time.time()
  costs = 0.0
  iters = 0
  state = model.initial_state.eval()
  for step, (x, y) in enumerate(reader.ptb_iterator(data, model.batch_size,
                                                    model.num_steps)):
    cost, state, _ = session.run([model.cost, model.final_state, eval_op],
                                 {model.input_data: x,
                                  model.targets: y,
                                  model.initial_state: state})

    costs += cost
    iters += model.num_steps

    if verbose and step % (epoch_size // 100) == 100:
      print("%.3f perplexity: %.3f speed: %.0f wps" %
            (step * 1.0 / epoch_size, np.exp(costs / iters),
             iters * model.batch_size / (time.time() - start_time)))

  return np.exp(costs / iters)

class node():
  def __init__(self, costs, state, sntc):
    self.costs = costs
    self.state = state
    self.sntc = sntc

def rescore_old(session, model, data, word_to_id, rev_dict, verbose=False):
  """Runs the model on the given data."""
  epoch_size = ((sum([len(i) for i in data]) // model.batch_size) - 1) // model.num_steps
  start_time = time.time()
  iters = 0
  state = model.initial_state.eval()
  init_state = state
  text = []
  best = [0, 100000000, '']
  for i,line in enumerate(data):
    line = [word_to_id['</s>']] + line
    sntc = []
    costs = 0.0
    state = init_state
    for step, (x, y) in enumerate(reader.rescore_iterator(line, model.batch_size,
                                                      model.num_steps, word_to_id)):
      cost, state = session.run([model.cost, model.final_state],
                                   {model.input_data: x,
                                    model.targets: y,
                                    model.initial_state: state})
      costs += cost
      iters += model.num_steps
      sntc.append(rev_dict[int(y)])
      
    sntc = ' '.join(sntc)
    best[0] = i
    best[1] = costs
    best[2] = sntc
    text.append(' ||| '.join([str(i) for i in best]))
  return text

def rescore(session, model, data, word_to_id, rev_dict, verbose=False):
  """Runs the model on the given data."""
  start_time = time.time()
  iters = 0
  init_state = model.initial_state.eval()
  list_size = (int(math.ceil(len(data)/model.batch_size))* model.batch_size)
  best = [[0, 100000000] for i in range(list_size)]
  all_costs = []
  for i, line in enumerate(reader.rescore_process(data, model.batch_size, word_to_id)):
    state = init_state
    costs = [0.0]*model.batch_size
    sntc = []*model.batch_size
      
    for step, (x, y) in enumerate(reader.rescore_iterator(line, model.batch_size,
                                                      model.num_steps, word_to_id)):
      # print(x)
      # print(y)
      loss, state = session.run([model.loss, model.final_state],
                                   {model.input_data: x,
                                    model.targets: y,
                                    model.initial_state: state})
      costs += loss
      iters += model.num_steps

      sntc.append([rev_dict[int(j)] for j in y])
      for loc, j in enumerate(y):
        if j==word_to_id['</s>']:
          best[i*model.batch_size+loc][0] = i*model.batch_size+loc
          best[i*model.batch_size+loc][1] = costs[loc]
          best[i*model.batch_size+loc].append(' '.join([subsntc[loc] for subsntc in sntc]))
      # if i % 100 == 0:
      #   print(i)
  text = [' ||| '.join([str(line) for line in n]) for n in best]
  print("speed: %.0f wps" % (iters*model.batch_size/(time.time()- start_time)))
  return text

def get_config():
  return MediumConfig()

def train():
  if not FLAGS.data_path:
    raise ValueError("Must set --data_path to data directory")

  raw_data = reader.raw_data(FLAGS.data_path)
  train_data, valid_data, test_data, _, word_to_id = raw_data

  config = get_config()
  eval_config = get_config()
  eval_config.batch_size = 1
  eval_config.num_steps = 1

  with tf.Graph().as_default(), tf.Session() as session:
    initializer = tf.random_uniform_initializer(-config.init_scale,
                                                config.init_scale)
    with tf.variable_scope("model", reuse=None, initializer=initializer):
      m = PTBModel(is_training=True, is_testing=False, config=config)
    with tf.variable_scope("model", reuse=True, initializer=initializer):
      mvalid = PTBModel(is_training=False, is_testing=False, config=config)
      mtest = PTBModel(is_training=False, is_testing=True, config=eval_config)

    # tf.initialize_all_variables().run()
    if not os.path.exists(FLAGS.train_path):
      os.makedirs(FLAGS.train_path)
      
    session.run(tf.initialize_all_variables())
    ckpt = tf.train.get_checkpoint_state(FLAGS.train_path)
    if ckpt and tf.gfile.Exists(ckpt.model_checkpoint_path):
      print("Reading model parameters from %s" % ckpt.model_checkpoint_path)
      m.saver.restore(session, ckpt.model_checkpoint_path)
    else:
      print("Created model with fresh parameters.")
      session.run(tf.initialize_all_variables())

    valid_perplexity_old = 1000000000000000000

    for i in range(config.max_max_epoch):
      [train_data, valid_data, test_data] = reader.split_data(raw_data)

      lr_decay = config.lr_decay ** max(i - config.max_epoch, 0.0)
      m.assign_lr(session, config.learning_rate * lr_decay)

      print("Epoch: %d Learning rate: %.3f" % (i + 1, session.run(m.lr)))
      train_perplexity = run_epoch(session, m, train_data, m.train_op, verbose=True)
      print("Epoch: %d Train Perplexity: %.3f" % (i + 1, train_perplexity))
      valid_perplexity = run_epoch(session, mvalid, valid_data, tf.no_op())
      print("Epoch: %d Valid Perplexity: %.3f" % (i + 1, valid_perplexity))

      if valid_perplexity > valid_perplexity_old:
        break

      checkpoint_path = os.path.join(FLAGS.train_path, "translate.ckpt")
      m.saver.save(session, checkpoint_path, global_step=i)

      valid_perplexity_old = valid_perplexity

    test_perplexity = run_epoch(session, mtest, test_data, tf.no_op())
    print("Test Perplexity: %.3f" % test_perplexity)


def rescore_dat():
  if not FLAGS.data_path:
    raise ValueError("Must set --data_path to data directory")

  config = get_config()
  eval_config = get_config()
  eval_config.batch_size = 512
  eval_config.num_steps = 1

  best = []

  with tf.Graph().as_default(), tf.Session() as session:
    initializer = tf.random_uniform_initializer(-config.init_scale,
                                                config.init_scale)
    with tf.variable_scope("model", reuse=None, initializer=initializer):
      mtest = PTBModel(is_training=False, is_testing=True, config=eval_config)

    # tf.initialize_all_variables().run()
    if not os.path.exists(FLAGS.train_path):
      os.makedirs(FLAGS.train_path)

    session.run(tf.initialize_all_variables())
    ckpt = tf.train.get_checkpoint_state(FLAGS.train_path)
    if ckpt and tf.gfile.Exists(ckpt.model_checkpoint_path):
      print("Reading model parameters from %s" % ckpt.model_checkpoint_path)
      mtest.saver.restore(session, ckpt.model_checkpoint_path)
    else:
      print("Created model with fresh parameters.")

    word_to_id  = json.load(open(FLAGS.wmap_path, 'r'))
    rev_dict = dict()
    for key in word_to_id.keys():
      rev_dict[int(word_to_id[key])] = key
    for n in range(1,2738):
      raw_data = reader.get_nbest(FLAGS.data_path+str(n)+".txt", word_to_id)
      [test_data, _, word_to_id] = raw_data
      k = len(test_data)

      best_sntcs = rescore(session, mtest, test_data, word_to_id, rev_dict)

      with open(FLAGS.outfile+str(n)+".txt",'w') as bestfile:
        print("sentence ID "+str(n))
        for j in range(0,k):
          line = best_sntcs[j]
          bestfile.write(str(n)+" ||| "+line+"\n")


def perpcal_dat():
  if not FLAGS.data_path:
    raise ValueError("Must set --data_path to data directory")

  config = get_config()
  eval_config = get_config()
  eval_config.batch_size = 512
  eval_config.num_steps = 1

  best = []

  with tf.Graph().as_default(), tf.Session() as session:
    initializer = tf.random_uniform_initializer(-config.init_scale,
                                                config.init_scale)
    with tf.variable_scope("model", reuse=None, initializer=initializer):
      mtest = PTBModel(is_training=False, is_testing=True, config=eval_config)

    # tf.initialize_all_variables().run()
    if not os.path.exists(FLAGS.train_path):
      os.makedirs(FLAGS.train_path)

    session.run(tf.initialize_all_variables())
    ckpt = tf.train.get_checkpoint_state(FLAGS.train_path)
    if ckpt and tf.gfile.Exists(ckpt.model_checkpoint_path):
      print("Reading model parameters from %s" % ckpt.model_checkpoint_path)
      mtest.saver.restore(session, ckpt.model_checkpoint_path)
    else:
      print("Created model with fresh parameters.")

    word_to_id  = json.load(open(FLAGS.wmap_path, 'r'))
    rev_dict = dict()
    for key in word_to_id.keys():
      rev_dict[int(word_to_id[key])] = key
    for n in range(1,2738):
      raw_data = reader.get_nbest(FLAGS.data_path+str(n)+".txt", word_to_id)
      [test_data, _, word_to_id] = raw_data
      k = len(test_data)

      best_sntcs = rescore(session, mtest, test_data, word_to_id, rev_dict)

      with open(FLAGS.outfile+str(n)+".txt",'w') as bestfile:
        print("sentence ID "+str(n))
        for j in range(0,k):
          line = best_sntcs[j]
          bestfile.write(str(n)+" ||| "+line+"\n")

def main(_):
  if FLAGS.decode:
    rescore_dat()
  elif FLAGS.perpcal:
    perpcal_dat()
  else:
    train()

if __name__ == "__main__":
  tf.app.run()