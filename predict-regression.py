#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
In this script, I explored the correlation between different variables and used
 regression analysis to predict the rating of restaurants. 


Created on Thu Sep 17 21:40:39 2019

@author: wumeiqi
"""

import matplotlib.pyplot as plt # plotting library
import seaborn as sns           # data visulization library
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.preprocessing import scale
from sklearn.svm import SVR
#%% Encode the input variables (factorize the values of certain columns)
def Encode(data):
    '''
    Factorize: address, name, online_order, book_table, rest_type,cuisines,
               menu_item, type, city, review_text
    '''
    for column in data.columns[~data.columns.isin(['rate', 'average_cost', 'votes'])]:
        data[column] = data[column].factorize()[0]
        
    for column in ['average_cost', 'votes']:
        data[column] = scale(data[column])
        
    return data

df_temp = df.drop(['dish_liked', 'reviews_list', 'dish_reviewed'], axis=1)
df_en = Encode(df_temp)
del df_temp

#%% Check the correlation between different variables
# address, name, online_order, book_table, rate, votes, rest_type,cuisines, 
# average_cost, menu_item, type, city, review_text
corr = df_en.corr(method='kendall')
plt.figure(figsize=(10, 6))
sns.heatmap(corr, annot=True)

#%% Define the x and y for regression analysis
x = df_en.loc[:, ['online_order', 'book_table', 'votes', 'rest_type','cuisines',
                  'average_cost', 'menu_item', 'city']]
y = df_en['rate']

#%% Linear Regression
# Linear regression acts poorly because I didn't create the dummy variables for one-hot
# label the catogorical variables
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1)
reg = LinearRegression()
reg.fit(x_train, y_train)
y_hat = reg.predict(x_test)
print('R-squared score of the Linear model: ', r2_score(y_test, y_hat))
print('MSE of the Linear model: ', mean_squared_error(y_test, y_hat))


#%% SVM
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1)
SVM=SVR(kernel='rbf',gamma='auto')
#SVM=SVR(kernel='poly',gamma='auto', degree=3)
SVM.fit(x_train, y_train)
y_hat = SVM.predict(x_test)
print('R-squared score of the SVM model: ', r2_score(y_test, y_hat))
print('MSE of the SVM model: ', mean_squared_error(y_test, y_hat))

#%% Decision Tree Regression
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1)
DTree=DecisionTreeRegressor(min_samples_leaf=0.0001)
DTree.fit(x_train, y_train)
y_hat = DTree.predict(x_test)
print('R-squared score of the Decision Tree model: ', r2_score(y_test, y_hat))
print('MSE of the Decision Tree model: ', mean_squared_error(y_test, y_hat))

#%% Random Forest Regression
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1)
RForest=RandomForestRegressor(n_estimators=500, min_samples_leaf=0.0001)
RForest.fit(x_train, y_train)
y_hat = RForest.predict(x_test)
print('R-squared score of the Random Forest model: ', r2_score(y_test, y_hat))
print('MSE of the Random Forest model: ', mean_squared_error(y_test, y_hat))