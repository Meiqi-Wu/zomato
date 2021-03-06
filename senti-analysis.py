#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
In this script, I conducted sensiment analysis of reviews based on a LSTM model.

Created on Mon Sep 18 21:15:12 2019

@author: wumeiqi
"""

#%% Import the packages
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense, Embedding, LSTM, SpatialDropout1D
from nltk import word_tokenize
from tqdm import tqdm # Instantly make loops show a smart progress meter
import re
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
import random
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
#%% prepare the data
## Extract reviews and ratings of each restaurant and create a dataframe with it
#ratings = []
#for name, reviews in tqdm(zip(df['name'], df['reviews_list'])):
#    for score, doc in reviews:
#        if isinstance(score, str) and isinstance(doc, str):
#            score = score.strip('Rated').strip()
#            doc = doc.strip('RATED').strip()
#            score = float(score)
#            ratings.append([name, score, doc])
#del name, reviews, score, doc
#
#ratings_df = pd.DataFrame(ratings, columns=['name', 'score', 'review'])
#ratings_df.head()
## clear each review text
#ratings_df['review'] = ratings_df['review'].apply(lambda x: re.sub('[^a-zA-Z0-9\s]', '', x))
#ratings_df.to_csv('./DATA/Ratings.csv')
#%% Read the Rating data
ratings_df = pd.read_csv('./DATA/Ratings.csv').drop('Unnamed: 0', axis=1)
ratings_df.review = ratings_df.review.astype(str)


#%%
# divide reviews as negative and positive based on scores
ratings_df['senti'] = ratings_df['score'].apply(lambda x: 1 if int(x)>2.5 else 0)
# tokenize the data and vectorize the reviews
max_features = 1000 # The maximu number of words to keep
# create a tokenizer
tokenizer = Tokenizer(num_words = max_features, split=' ')
# fit the tokenizer on the review text
tokenizer.fit_on_texts(ratings_df['review'].values)
X = tokenizer.texts_to_sequences(ratings_df['review'].values)
X = pad_sequences(X)

#%% Build the model
embed_dim = 32
lstm_out = 32

model = Sequential()
# input_dim: len(o), output_dim=len(e), E=len(e)*len(o)
model.add(Embedding(input_dim=max_features, output_dim=embed_dim, input_length=X.shape[1]))
model.add(LSTM(units=lstm_out, dropout=0.2, recurrent_dropout=0.2))
model.add(Dense(2, activation='softmax'))

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
print(model.summary())

#%% Train the model
# convert senti(0/1) to one-hot vectors
Y = pd.get_dummies(ratings_df['senti'].astype(int)).values
# split the training and test set
random.seed(9000)
test_id = np.random.choice(X.shape[0], size=round(0.3*X.shape[0]), replace=False)
train_id = ~np.isin(np.array(range(X.shape[0])), test_id)
Xtrain, Xtest, Ytrain, Ytest = X[train_id], X[test_id], Y[train_id], Y[test_id]

#Xtrain, Xtest, Ytrain, Ytest = train_test_split(X, Y, test_size=0.3)
print(Xtrain.shape, Ytrain.shape)
print(Xtest.shape, Ytest.shape)

#%% 
batch_size=1024
model.fit(Xtrain, Ytrain, epochs=5, batch_size=batch_size)


#%% Evaluation
loss, acc = model.evaluate(Xtest, Ytest, batch_size=batch_size)
print('Test set loss: {}'.format(loss))
print('Test set accuracy: {}'.format(acc)) # 0.95356


#%% Intepretation

# what are the strongly predictive features
words = list(tokenizer.word_index.keys())[:max_features] # bag of words
x = np.concatenate((np.zeros((max_features-1, X.shape[1]-1), dtype=np.int8),
                    np.array([[int(i)] for i in range(1, max_features)])), axis=1)
probs = model.predict(x)[:,1]
ind = np.argsort(probs)

bad_words = [words[ind[i]] for i in range(10)]
good_words = [words[ind[-i]] for i in range(1,11)]

bad_probs = probs[ind[:10]]
good_probs = probs[ind[-10:]]

print('Good words\t    P(satisfactory|word)')
for w, p in zip(good_words, good_probs):
    print('   {}  {}'.format(w, p))
    
print('Bad words\t    P(satisfactory|word)')
for w, p in zip(bad_words, bad_probs):
    print('   {}  {}'.format(w, p))

#%% check the mis-predictions
Y_hat = model.predict(Xtest)
prob = Y_hat[:, 1]
pred_senti = (prob >=0.5)*1

ratings_df_test = ratings_df.loc[test_id, ['score','senti', 'review']]
ratings_df_test['pred_senti']=pred_senti

true_pos = np.array(ratings_df_test.query('senti==1 & pred_senti==1').index)
true_neg = np.array(ratings_df_test.query('senti==0 & pred_senti==0').index)
false_neg = np.array(ratings_df_test.query('senti==1 & pred_senti==0').index)
false_pos = np.array(ratings_df_test.query('senti==0 & pred_senti==1').index)
#%%
print('Confusion Matrix')
print('          y=1      y=0 ')
print('y_hat=1  ',true_pos.shape[0], false_pos.shape[0])
print('y_hat=0  ',false_neg.shape[0],' ', true_neg.shape[0])

recall = true_pos.shape[0]/(true_pos.shape[0]+false_neg.shape[0])
print('Recall: ', recall)

precision = true_pos.shape[0]/(true_pos.shape[0]+false_pos.shape[0])
print('precision: ', precision)
#%%
print('True negative reviews')
print('\n')
random.seed(12)
for row in np.random.choice(true_neg, 10, replace=False):
    print(ratings_df_test.loc[row, 'score'])
    print(ratings_df_test.loc[row, 'pred_senti'])
    
    print(ratings_df_test.loc[row, 'review'])
    print('\n')


print('False negative reviews')
print('\n')
random.seed(1)
for row in np.random.choice(false_neg, 10, replace=False):
    print(ratings_df_test.loc[row, 'score'])
    print(ratings_df_test.loc[row, 'pred_senti'])
    
    print(ratings_df_test.loc[row, 'review'])
    print('\n')

print('False positive reviews')
print('\n')
random.seed(2)
for row in np.random.choice(false_pos, 10, replace=False):
    print(ratings_df_test.loc[row, 'score'])
    print(ratings_df_test.loc[row, 'pred_senti'])
    
    print(ratings_df_test.loc[row, 'review'])
    print('\n')










