# -*- coding: utf-8 -*-
"""ix project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16jvB-NAwB6BPeAfeayMo1Q2CdgVeB5es

# Set up
"""

pip install catboost

!pip install --upgrade fastcore -q
!pip install --upgrade fastai -q

from fastai.vision.all import * # Needs latest version, and sometimes a restart of the runtime after the pip installs

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
np.random.seed(123)
warnings.filterwarnings('ignore')
# %matplotlib inline

tr = pd.read_csv('Train (2).csv')

tr.shape

tr.head()

ts = pd.read_csv('Test (2).csv')

ts.shape

ts.head()

vdef = pd.read_csv('VariableDefinitions (1).csv')
vdef

"""# Data Understanding"""

tr.dtypes

ts.dtypes

tr.isna().sum()

# Visualize the missing values in train set
ax = tr.isna().sum().sort_values().plot(kind = 'barh', figsize = (9, 10))
plt.title('Percentage of Missing Values Per Column in Train Set', fontdict={'size':15})
for p in ax.patches:
    percentage ='{:,.0f}%'.format((p.get_width()/tr.shape[0])*100)
    width, height =p.get_width(),p.get_height()
    x=p.get_x()+width+0.02
    y=p.get_y()+height/2
    ax.annotate(percentage,(x,y))

ts.isna().sum()

# Visualize the missing values in test set
ax = ts.isna().sum().sort_values().plot(kind = 'barh', figsize = (9, 10))
plt.title('Percentage of Missing Values Per Column in Test Set', fontdict={'size':15})
for p in ax.patches:
    percentage ='{:,.0f}%'.format((p.get_width()/tr.shape[0])*100)
    width, height =p.get_width(),p.get_height()
    x=p.get_x()+width+0.02
    y=p.get_y()+height/2
    ax.annotate(percentage,(x,y))

#unique elements in our data:
cols = tr.columns.to_list()

for col in cols:
  print('COLUMN:', col)
  print('Number of unique variables:', tr[col].nunique())
  print(tr[col].unique())
  print()

tr.duplicated().any()

ts.duplicated().any()

"""# Data Cleaning

From here we'll work with a combination of the train and test to speed things up
"""

# Combine train and test set
ntr = tr.shape[0] # to be used to split train and test set from the combined dataframe

all_data = pd.concat((tr, ts)).reset_index(drop=True)
print(f'The shape of the combined dataframe is: {all_data.shape}')

# deleting some columns:
all_data = all_data.drop(['ID'], axis =1)

all_data.head()

all_data['age'].describe()

all_data['FQ19'].describe()

FQ19mode = all_data['FQ19'].mode()
print(FQ19mode)

"""**Missing values:**

Since the missing values are many, we'll seek to fill them withsomething else rather than drop the rows containing them
"""

#Filling age with mean
all_data["age"].fillna(all_data["age"].mean(), inplace=True)

#Filling F19(Sorce of money for F18 i.e Possibility of coming up with 0.05 per capita in a month) with the mode
all_data['FQ19'] = all_data['FQ19'].fillna(all_data['FQ19'].mode()[0])

#Filling the F columns with 4(refused to answer)
cols = [x for x in all_data.columns if x.startswith('FQ')]

#for col in cols:
#all_data[col].fillna(4)  
for col in all_data.columns:
  if col in cols:
    all_data[col] = all_data[col].fillna(4)

#Confirming the effect:
all_data.info()

# Separate the cleaned train and test data from the combined dataframe.
c_tr = all_data[:ntr]
c_ts = all_data[ntr:]

# Check the shapes of the split dataset
c_tr.shape, c_ts.shape

c_tr.head()

c_ts.head()

#LOADING THEM INTO NEW CSV FILES FOR THE ANALYSIS PROCESS:
c_tr.to_csv('cleantr.csv', index = False)
c_ts.to_csv('cleantn.csv', index = False)

"""# Data Preparation"""

# LabelBinarizer converts the string categorical variable to binary 
#from sklearn.preprocessing import LabelBinarizer
#lb= LabelBinarizer()
#all_data["Target"]= lb.fit_transform(["Target"])

sns.countplot('Target', data = all_data);

# Category columns
cat_cols = ['country_code',	'region'] + [x for x in all_data.columns if x.startswith('FQ')]
num_cols = ['age']

# Change columns to their respective datatypes
all_data[cat_cols] = all_data[cat_cols].astype('category')

# Confirm whether the changes have been successful
all_data.info()

# Use one hot encoding to turn categorical features to numerical features
# Encode categorical features
all_data = pd.get_dummies(data = all_data, columns = cat_cols)
all_data.head()

"""Numeric vars:"""

# performing binning on age
# we bin by defining the intervals and categories
interval = (15, 20, 35, 60, 100)
categories = ['student', 'youth', 'adult', 'senior']
all_data["age"] = pd.cut(all_data.age, interval, labels = categories)

# Separate train and test data from the combined dataframe
train = all_data[:ntr]
test = all_data[ntr:]

# Check the shapes of the split dataset
train.shape, test.shape

test = test.drop('Target', axis = 1)

test.shape

"""# Model"""

# Select main columns to be used in training
# main_cols = all_data.columns.difference([])
X = train.drop(['Target'], axis =1)
y = train.Target.astype(int)

X.head()

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, random_state=42, stratify=y)

#import classifier algorithm 
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import ExtraTreesClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

# create models
lg_model = LogisticRegression()
rf_model = RandomForestClassifier()
kn_model = KNeighborsClassifier()
et_model = ExtraTreesClassifier()
xg_model = XGBClassifier()
lgbm_model = LGBMClassifier()

#training the models
lg_model.fit(X_train,y_train)
rf_model.fit(X_train,y_train)
kn_model.fit(X_train,y_train)
et_model.fit(X_train,y_train)
xg_model.fit(X_train,y_train)
lgbm_model.fit(X_train, y_train)

#making predictions
lg_y_pred = lg_model.predict_proba(X_test)[:, 1]
rf_y_pred = rf_model.predict_proba(X_test)[:, 1]
kn_y_pred = kn_model.predict_proba(X_test)[:, 1]
et_y_pred = et_model.predict_proba(X_test)[:, 1]
xg_y_pred = xg_model.predict_proba(X_test)[:, 1]
lgbm_y_pred = lgbm_model.predict_proba(X_test)[:, 1]

"""**MORE** **MODELS**"""

# importing our machine learning algorithms  
from sklearn.tree import DecisionTreeClassifier 
from sklearn.ensemble import GradientBoostingClassifier

# create models
dst_model = DecisionTreeClassifier()
gbm_model = GradientBoostingClassifier()

#training the models
dst_model.fit(X_train,y_train)
gbm_model.fit(X_train,y_train)

#making predictions
dst_y_pred = dst_model.predict_proba(X_test)[:, 1]
gbm_y_pred = gbm_model.predict_proba(X_test)[:, 1]

"""## Model Evaluation
The error metric for this competition is the Area Under the Curve (AUC).
"""

# import evaluation metrics
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.metrics import roc_curve, roc_auc_score

# evaluate the model
# roc_auc_score
print("Logistic Regression classifier: ", roc_auc_score(y_test, lg_y_pred))
print("Random Forest classifier: ", roc_auc_score(y_test, rf_y_pred))
print("KNeighbors Classifier: ", roc_auc_score(y_test, kn_y_pred))
print("Extra Tree classifier: ", roc_auc_score(y_test, et_y_pred))
print("XGB classifier: ", roc_auc_score(y_test, xg_y_pred))
print('LGBM AUC score on the X_test is:', roc_auc_score(y_test, lgbm_y_pred))
print("DecisionTreeClassifier : ", roc_auc_score(y_test, dst_y_pred))
print("GradientBoostingClassifier: ", roc_auc_score(y_test, gbm_y_pred))

"""## Making model better"""

from sklearn.model_selection import GridSearchCV

# Optimize model paramaters 
param_grid = {'min_child_weight': [1, 5, 10],
        'gamma': [0, 1],
        'subsample': [0.6, 0.8, 1.0],
        'max_depth': [3,5]
        }
my_xg_model = GridSearchCV(xg_model, param_grid,n_jobs=-1,verbose=2,cv=5)
my_xg_model.fit(X_train, y_train)
print(my_xg_model.best_params_)

from sklearn.metrics import confusion_matrix, accuracy_score

# fit by setting best parameters and Evaluate model
xgb_model = XGBClassifier(min_child_weight=1, gamma=0.5, subsample=0.6, max_depth=3)

xgb_model.fit(X_train, y_train)
y_pred = xgb_model.predict_proba(X_test)[:, 1]

# Get error rate
print("New XGB classifier: ", roc_auc_score(y_test, y_pred))

"""### CATBST"""

from catboost import CatBoostClassifier

clf = CatBoostClassifier(
    iterations=5, 
    learning_rate=0.1, 
    #loss_function='CrossEntropy'
)


clf.fit(X_train, y_train, 
        #cat_features = cat_features, 
        eval_set=(X_test, y_test), 
        verbose=False
)

print('CatBoost model is fitted: ' + str(clf.is_fitted()))
print('CatBoost model parameters:')
print(clf.get_params())

from catboost import CatBoostClassifier
clf = CatBoostClassifier(
    iterations=5,
#     verbose=5,
)

clf.fit(
    X_train, y_train,
    #cat_features=cat_features,
    eval_set=(X_test, y_test),
)

#MAKING PREDICTION
clf_y_pred = clf.predict_proba(X_test)[:, 1]

print(clf.predict_proba(data=X_test)[:, 1])

#EVALUATING THE MODEL
print("CatBoostClassifier: ", roc_auc_score(y_test, clf_y_pred))

from catboost import CatBoostClassifier

clf = CatBoostClassifier(
    iterations=54,
    random_seed=42,
    learning_rate=0.6,
    custom_loss=['AUC', 'Accuracy']
)

clf.fit(
    X_train, y_train,
    # cat_features=cat_features,
    eval_set=(X_test, y_test),
    verbose=False,
    plot=True
)

"""# Submission"""

X_train[:4]

test[:4]

# Get the predicted result for the test Data with the model of choice
prediction = clf.predict_proba(test)[:, 1]

prediction

"""Making Submission:"""

ss = pd.read_csv('SampleSubmission (2).csv')
ss

sub_file = pd.DataFrame()
sub_file["ID"] = ts["ID"]
sub_file["target"] = prediction

sub_file.to_csv('clf.csv', index = False)
sub_file.head()