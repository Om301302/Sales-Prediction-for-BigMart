# -*- coding: utf-8 -*-
"""Sales Prediction Starter.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1B4t_ZqgIuBdibwcCagIvLjrSZ6b2DZcI

# BigMart Sales Prediction

![](https://www.analyticsvidhya.com/wp-content/uploads/2016/02/Comp-4.jpg)

## Objective

The data scientists at BigMart have collected sales data for 1559 products across 10 stores in different cities. Also, certain attributes of each product and store have been defined. The aim is to build a predictive model and find out the sales of each product at a particular store (each row of data).

__So the idea is to find out the features (properties) of a product, and store which impacts the sales of a product.__

## Dataset Details

![](https://i.imgur.com/WlgNuFs.png)

## Get the Dataset

You can download the dataset manually from [this link](https://drive.google.com/file/d/1xFDvCOLa_gu34CosX8kSCIqqhD-E2te8/view?usp=sharing) or use the following code snippet to load in in google colab directly.
"""

!gdown --id 1xFDvCOLa_gu34CosX8kSCIqqhD-E2te8

import pandas as pd

df = pd.read_csv('sales_prediction.csv')

df.head()

"""### New *Section*

#**Prepare Trainig and test DataSets **

Here i will split 70% Train and 30% test dataset to make a model.
seed = 42 for reproductibility
"""

X = df.drop(columns=['Item_Outlet_Sales'])
y = df['Item_Outlet_Sales']

SEED = 42

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=SEED)

X_train.shape, X_test.shape

X_train.head()

y_train.head()

"""#Data Wrangling

Making a copy of train data so we do not loose or we can exprement
"""

X_train_c = X_train.copy()

X_train_c.info()

X_train_c.isnull().sum()

"""Now we know that in out data we have many null or missing values we do not want to train that in model

"""

num_data = X_train_c.select_dtypes(exclude=['object'])
num_data.head()

"""to check for the negavite values i will do quick describe where it shows the min aand max values

"""

num_data.describe()

num_data.isnull().sum()

import seaborn as sns
import matplotlib.pyplot as plt

fig, ax = plt.subplots(1, 2, figsize=(12, 5))

sns.histplot(data=X_train_c, x='Item_Weight', ax=ax[0])
sns.boxplot(data=X_train_c, x='Item_Weight', ax=ax[1])

# prompt: create a visualize_numeric_feature function

def visualize_numeric_feature(df, col_name):
  """
  This function visualizes a numeric feature from a dataframe.

  Args:
      df: The dataframe containing the col_name.
      col_name: The name of the col_name to visualize.
  """

  fig, ax = plt.subplots(1, 2, figsize=(12, 5))

  sns.histplot(data=df, x=col_name, ax=ax[0])
  sns.boxplot(data=df, x=col_name, ax=ax[1])

  plt.show()

visualize_numeric_feature(X_train_c, 'Item_Weight')

visualize_numeric_feature(X_train_c, 'Item_Visibility')

visualize_numeric_feature(X_train_c, 'Item_MRP')

visualize_numeric_feature(X_train_c, 'Outlet_Establishment_Year')

sns.countplot(data=X_train_c, x='Outlet_Establishment_Year')

cat_feature=X_train_c.select_dtypes(include=['object'])
cat_feature.head()

cat_feature.isnull().sum()

cat_feature['Item_Identifier'].value_counts()

cat_feature['Item_Fat_Content'].value_counts()

"""there are differant names for low fat so we nned to change it to same to train our model"""

cat_feature['Item_Type'].value_counts()

cat_feature['Outlet_Identifier'].value_counts()

cat_feature['Outlet_Size'].value_counts()

cat_feature['Outlet_Location_Type'].value_counts()

cat_feature['Outlet_Type'].value_counts()

"""#now since we know the data it is time to do the DATA Wrangling + feature Enginerring

means we will go over each column and do a data cleaning

#Step- 1 Crete high level item Types
"""

X_train_c['Item_Identifier'].apply(lambda x:x[:2]).value_counts()

X_train_c['Item_Identifier'].str[:2].value_counts()

#step1 Map items IDS to Item Types

def create_item_type(data_frame):
    data_frame['Item_Type'] = data_frame['Item_Identifier'].str[:2]
    data_frame['Item_Type'] = data_frame['Item_Type'].map({
                                                 'FD': 'Food',
                                                 'NC':'Non_Consumables',
                                                 'DR':'Drink'
    })
    return data_frame

X_train_c = create_item_type(X_train_c)
X_train_c.head()

X_train_c[['Item_Type', 'Item_Weight']]

"""#Step-2: Fill in missing values for Item_Weight"""

X_train_c.isnull().sum()

X_train_c[['Item_Identifier', 'Item_Weight']].drop_duplicates().sort_values(by=['Item_Identifier'])

X_train_c[['Item_Type', 'Item_Weight']].drop_duplicates().sort_values(by=['Item_Type'])

#step;2 Fill in missing values for item_weight
#logic
#1-use mapping from itemid - weight and fill in missing values
#2- if completely new item
# i.e = item ID not in test \ live data use item type - median(weight) and fill in missing values

ITEM_ID_WEIGHT_PIVOT = X_train_c.pivot_table(values='Item_Weight', index='Item_Identifier').reset_index()
ITEM_ID_WEIGHT_MAPPING= dict(zip(ITEM_ID_WEIGHT_PIVOT['Item_Identifier'], ITEM_ID_WEIGHT_PIVOT['Item_Weight']))
list(ITEM_ID_WEIGHT_MAPPING.items())[:10]

ITEM_TYPE_WEIGHT_PIVOT = X_train_c.pivot_table(values='Item_Weight', index='Item_Type', aggfunc='median').reset_index()

ITEM_TYPE_WEIGHT_MAPPING= dict(zip(ITEM_TYPE_WEIGHT_PIVOT['Item_Type'], ITEM_TYPE_WEIGHT_PIVOT['Item_Weight']))
ITEM_TYPE_WEIGHT_MAPPING.items()

# prompt: # prompt: create a function "impute_item_weight(data_frame); which would first go with id-weight and then type-weight

def impute_item_weight(data_frame):
  # First, use the item ID-weight mapping to fill in missing values
  data_frame['Item_Weight'].fillna(data_frame['Item_Identifier'].map(ITEM_ID_WEIGHT_MAPPING), inplace=True)

  # Then, use the item type-weight mapping to fill in any remaining missing values
  data_frame['Item_Weight'].fillna(data_frame['Item_Type'].map(ITEM_TYPE_WEIGHT_MAPPING), inplace=True)

  return data_frame

# # prompt: create a function "impute_item_weight(data_frame); which would first go with id-weight and then type-weight

# def impute_item_weight(data_frame):
#     data_frame.loc[:,'Item_Weight'] = data_frame.loc[:,'Item_Weight'].fillna(data_frame.loc[:,'Item_Identifier']).map(ITEM_ID_WEIGHT_MAPPING)
#     data_frame.loc[:,'Item_Weight'] = data_frame.loc[:,'Item_Weight'].fillna(data_frame.loc[:,'Item_Type']).map(ITEM_TYPE_WEIGHT_MAPPING)

#     return data_frame

X_train_c = impute_item_weight(X_train_c)
X_train_c.isnull().sum()



"""# fill in for outlet size"""

X_train_c.groupby(by=['Outlet_Type', 'Outlet_Size']).size()

from scipy.stats import mode

OUTLET_TYPE_SIZE_PIVOT = X_train.groupby('Outlet_Type')['Outlet_Size'].apply(lambda x: x.mode().iloc[0]).reset_index()
OUTLET_TYPE_SIZE_MAPPING = dict(zip(OUTLET_TYPE_SIZE_PIVOT['Outlet_Type'], OUTLET_TYPE_SIZE_PIVOT['Outlet_Size']))

OUTLET_TYPE_SIZE_MAPPING

# prompt: create a impute function

def impute_outlet_size(data_frame):
  data_frame.loc[:,'Outlet_Size'] = data_frame.loc[:,'Outlet_Size'].fillna(data_frame.loc[:,'Outlet_Type'].map(OUTLET_TYPE_SIZE_MAPPING))
  return data_frame

X_train_c = impute_outlet_size(X_train_c)
X_train_c.isnull().sum()

"""#Step-4 Standerdize item fat categories"""

X_train_c['Item_Fat_Content'].value_counts()

#step-4 make item fat content to consitent

def standerdize_item_fat_content(date_frame):
  date_frame['Item_Fat_Content'] = date_frame['Item_Fat_Content'].replace({
                                                      'Low Fat' : 'Low_Fat',
                                                      'LF' : 'Low_Fat',
                                                      'low fat' : 'Low_Fat',
                                                      'reg'     : 'Regular'
  })
  return date_frame

X_train_c = standerdize_item_fat_content(X_train_c)
X_train_c['Item_Fat_Content'].value_counts()

X_train_c.groupby(by=['Item_Type', 'Item_Fat_Content']).size()

# Step 5: correct item fat content for non consumables

def correct_item_fat_content(data_frame):
  # Replace their fat content with "Non_Edible"
  data_frame.loc[data_frame['Item_Type'] == 'Non_Consumables', 'Item_Fat_Content'] = 'Non_Edible'

  return data_frame

X_train_c = correct_item_fat_content(X_train_c)
X_train_c.groupby(by=['Item_Type', 'Item_Fat_Content']).size()

X_train_c.info()

"""#Prepare Database for ML"""

def prepare_dataset(data_frame):
  # Step 1: Create high-level item types
  data_frame = create_item_type(data_frame)

  # Step 2: Fill in missing values for Item_Weight
  data_frame = impute_item_weight(data_frame)

  # Step 3: Fill in missing values for Outlet_Size
  data_frame = impute_outlet_size(data_frame)

  # Step 4: Standardize item fat categories
  data_frame = standerdize_item_fat_content(data_frame)

  # Step 5: Correct item fat content for non-consumables
  data_frame = correct_item_fat_content(data_frame)


  return data_frame

X_train.isnull().sum()

X_train = prepare_dataset(X_train)
X_train.isnull().sum()

X_test.isnull().sum()

X_test = prepare_dataset(X_train)
X_test.isnull().sum()

"""#Handling Categorical Data - EXPT1


1.   Expt-1 All categorical columns - one hot encoded

*   List item
*   List item





"""

cat_feats = X_train_c.select_dtypes(include=['object'])
cat_feats.head()

from sklearn.preprocessing import OneHotEncoder

ohe = OneHotEncoder(handle_unknown = 'ignore')
ohe.fit(cat_feats)

ohe_feature_names = ohe.get_feature_names_out(input_features = cat_feats.columns)
ohe_feature_names

num_feats_train = X_train.select_dtypes(exclude=['object']).reset_index(drop=True)
num_feats_train.head()

cat_feats_train = X_train.select_dtypes(include=['object'])
X_train_cat_ohe = pd.DataFrame(ohe.transform(cat_feats_train).toarray(), columns=ohe_feature_names)
X_train_cat_ohe.head()

X_train_final = pd.concat([num_feats_train, X_train_cat_ohe], axis=1)
X_train_final.head()

final_columns = X_train_final.columns.values
final_columns

# prompt: transofm using one hard encoder for num_feast and cat-feast

num_feats_test = X_test.select_dtypes(exclude=['object']).reset_index(drop=True)
num_feats_test.head()
cat_feats_test = X_test.select_dtypes(include=['object'])
X_test_cat_ohe = pd.DataFrame(ohe.transform(cat_feats_test).toarray(), columns=ohe_feature_names)
X_test_cat_ohe.head()
X_test_final = pd.concat([num_feats_test, X_test_cat_ohe], axis=1)
X_test_final.head()

"""#Modeling"""

sns.histplot(y_train)

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, HistGradientBoostingRegressor
import xgboost as xgb
from lightgbm import LGBMRegressor
from sklearn.model_selection import cross_validate
import numpy as np

# prompt: create a resuable function train_andeval_model(model, X_train, y_train, cv=5)

def train_and_eval_model(model, X_train, y_train, cv=5):

  cv_results = cross_validate(model, X_train, y_train, cv=cv, scoring=('r2', 'neg_root_mean_squared_error'),)
  print('Model:', model)
  r2_scores = cv_results['test_r2']
  print('R2 CV scores:', r2_scores)
  print('R2 CV scores mean / stdev:' , np.mean(r2_scores), '/', np.std(r2_scores))

  rmse_scores = cv_results['test_neg_root_mean_squared_error']
  rmse_scores = [-1*score for score in rmse_scores]
  print('RMSE CV scores:', rmse_scores)
  print('RMSE CV scores mean / stdev:', np.mean(rmse_scores), '/', np.std(rmse_scores))

rf = RandomForestRegressor(random_state=SEED)
train_and_eval_model(model=rf, X_train=X_train_final, y_train=y_train)

gb = GradientBoostingRegressor(random_state=SEED)
train_and_eval_model(model=gb, X_train=X_train_final, y_train=y_train)

hgb = HistGradientBoostingRegressor(random_state=SEED)
train_and_eval_model(model=hgb, X_train=X_train_final, y_train=y_train)

xgr = xgb.XGBRegressor(objective='reg:squarederror', random_state=SEED)
train_and_eval_model(model=xgr, X_train=X_train_final, y_train=y_train)

lgbr = LGBMRegressor(random_state=SEED)
train_and_eval_model(model=lgbr, X_train=X_train_final, y_train=y_train)



"""#Handling Categorical Data - EXPT2

Expt-2 All categorial columns - native handling
"""

X_train_copy = X_train.copy().drop(columns='Item_Identifier')

cat_cols = X_train_copy.select_dtypes(include=['object']).columns.tolist()
num_cols = cal_cols = X_train_copy.select_dtypes(exclude=['object']).columns.tolist()
cat_cols, num_cols

X_train_copy [cat_cols] = X_train_copy[cat_cols].astype('category')
n_categorical_features = len(cat_cols)
n_numerical_features = len(num_cols)
X_train_copy = X_train_copy[cat_cols+num_cols]

X_train_copy.info()

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OrdinalEncoder
from sklearn.compose import make_column_transformer
from sklearn.compose import make_column_selector

categorical_mask = [True] * n_categorical_features + [False] * n_numerical_features
ordinal_encoder = make_column_transformer (
        (
        OrdinalEncoder (handle_unknown="use_encoded_value", unknown_value=np.nan),
        make_column_selector (dtype_include="category"),
        ),
        remainder="passthrough",
)

hgb = make_pipeline(
    ordinal_encoder,
    HistGradientBoostingRegressor(
          random_state=42, categorical_features=categorical_mask
              ) ,
)

train_and_eval_model(model=hgb, X_train=X_train_copy, y_train=y_train)

lgbr = LGBMRegressor(random_state=SEED)
train_and_eval_model(model=lgbr, X_train=X_train_copy, y_train=y_train)

"""#Handling Categorical Data-EXPT 3

Expt-3: No Item Identifier - one hot encoded
"""

cat_feats = X_train.select_dtypes(include=['object']).drop(columns=['Item_Identifier'])
ohe = OneHotEncoder(handle_unknown='ignore')
ohe.fit(cat_feats)
ohe_feature_names = ohe.get_feature_names_out(input_features=cat_feats.columns)

num_feats_train = X_test.select_dtypes(exclude=['object']).reset_index(drop=True)
cat_feats_train = X_test.select_dtypes(include=['object']).drop(columns=['Item_Identifier'])
X_train_cat_ohe = pd.DataFrame(ohe.transform(cat_feats_train).toarray(), columns=ohe_feature_names)

X_train_final = pd.concat([num_feats_train, X_train_cat_ohe], axis=1)
X_train_final.head()

X_train_final.shape

gb = GradientBoostingRegressor(random_state=SEED)
train_and_eval_model(model=gb, X_train=X_train_final, y_train=y_train)

hgb = HistGradientBoostingRegressor(random_state=SEED)
train_and_eval_model(model=hgb, X_train=X_train_final, y_train=y_train)

xgr = xgb.XGBRegressor(objective='reg:squarederror', random_state=SEED)
train_and_eval_model(model=xgr, X_train=X_train_final, y_train=y_train)

lgbr = LGBMRegressor(random_state=SEED)
train_and_eval_model(model=lgbr, X_train=X_train_final, y_train=y_train)

"""We can see from the upper model what is the r*2 and rmsv(root mean square error) and error jhase decreased and r2 is increased which gives acurasy to  the model.

#Handling categorical Data EXPT-4

Expt-4: Item identifier - feature, rest categorical - one hot encoded.
"""

from sklearn.feature_extraction import FeatureHasher

hash_vector_size = 50
fh = FeatureHasher(n_features=hash_vector_size, input_type='string')

# Convert the single column 'Item_Identifier' into an iterable over iterables of strings
# You can achieve this by passing a list of lists where each inner list contains one string
X_train_item_identifier = [[item] for item in X_train['Item_Identifier']]

# Now, pass the converted iterable to the transform method
hashed_df = pd.DataFrame(fh.transform(X_train_item_identifier).toarray(),
                         columns=['H'+str(i) for i in range(hash_vector_size)])
hashed_df.head()

cat_feats = X_train.select_dtypes(include=['object']).drop(columns=['Item_Identifier'])
ohe = OneHotEncoder(handle_unknown='ignore')
ohe.fit(cat_feats)
ohe_feature_names = ohe.get_feature_names_out(input_features=cat_feats.columns)

num_feats_train = X_test.select_dtypes(exclude=['object']).reset_index(drop=True)
cat_feats_train = X_test.select_dtypes(include=['object']).drop(columns=['Item_Identifier'])
X_train_cat_ohe = pd.DataFrame(ohe.transform(cat_feats_train).toarray(), columns=ohe_feature_names)

X_train_final = pd.concat([num_feats_train, hashed_df, X_train_cat_ohe], axis=1)
X_train_final.head()

X_train_final.shape

gb = GradientBoostingRegressor(random_state=SEED)
train_and_eval_model(model=gb, X_train=X_train_final, y_train=y_train)

xgr = xgb.XGBRegressor(objective='reg:squarederror', random_state=SEED)
train_and_eval_model(model=xgr, X_train=X_train_final, y_train=y_train)

X_test.shape

X_train_item_identifier = [[item] for item in X_test['Item_Identifier']]

hashed_test_df = pd.DataFrame(fh.transform(X_train_item_identifier).toarray(),
                         columns=['H'+str(i) for i in range(hash_vector_size)])
num_feats_test = X_test.select_dtypes(exclude=['object']).reset_index(drop=True)
cat_feats_test = X_test.select_dtypes(include=['object']).drop(columns=['Item_Identifier'])
X_test_cat_ohe = pd.DataFrame (ohe.transform(cat_feats_test).toarray(), columns=ohe_feature_names)
X_test_final = pd.concat ([num_feats_test, hashed_test_df, X_test_cat_ohe], axis=1)
X_test_final.head ()

X_test_final.shape

xgr = xgb.XGBRegressor(objective='reg:squarederror', random_state=SEED)
xgr.fit(X_train_final, y_train)

y_pred = xgr.predict(X_test_final)
y_pred

from xgboost import plot_importance

fig, ax = plt.subplots(1,1, figsize=(20, 10))
plot_importance(xgr, ax=ax);