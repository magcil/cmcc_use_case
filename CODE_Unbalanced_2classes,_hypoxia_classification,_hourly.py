# -*- coding: utf-8 -*-
"""Copia di Unbalanced_2classes, Hypoxia_CLASSIFICATION, hourly.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ao56T1ZnrWYHUtFw0gxnm1vIMa9QWReE

**HYPOXIA - VENICE LAGOON - 
  IMBALANCED CLASSIFICATION PROBLEM**
  

*   Severe Imbalance -->  1:120
"""

import pandas as pd
# Use numpy to convert to arrays
import numpy as np
#Import Random Forest Model
from sklearn.ensemble import RandomForestClassifier
from sklearn import neighbors
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 
# Import train_test_split function

from sklearn.model_selection import train_test_split, RandomizedSearchCV

from sklearn.metrics import mean_squared_error,confusion_matrix,accuracy_score, roc_auc_score, f1_score
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
#Import scikit-learn metrics module for accuracy calculation
from sklearn import metrics
from datetime import date, datetime

from google.colab import drive
drive.mount('/content/gdrive')

"""# ▶ *Upload the dataset*"""

path_stations = '/content/gdrive/My Drive/Dati/DatiOriginali/Lagoon_WaterQuality/Elaborati/Dataset_hypoxia/Hourly/'

features = pd.read_excel(path_stations + 'hypoxia_dataset_2008-2019_hourly.xlsx')
features

# selecting rows based on condition
#features =  features.loc[features['IDSonda'] < 2]  #only station 1

# histogram of all the variables
features.hist(figsize=(15, 15))

features.describe()

"""# ▶ Classes of DO"""

#HYPOXIA < 60 % SAT     #https://www.sincem.unibo.it/images/tesi/Tesi_bianchi.pdf   https://nmsfarallones.blob.core.windows.net/farallones-prod/media/archive/manage/pdf/sac/16_08/SAC_HypoxiaInSanctuaries_JLargier2.pdf
low = features[features.DO <= 60]
high = features[features.DO > 60]

#assigns label to the classes
low["DO"] = 0 
high["DO"] = 1

#feature_class = pd.concat([primo, secondo, terzo, quarto])
feature_class = pd.concat([low, high])
feature_class

"""# ▶ Data preparation

"""

features.columns

# data preparation

dataset = feature_class  #feature_class
print("Dataset shape", dataset.shape)

# predictors
X_t = dataset.drop(labels=['DO', 'date', 'Unnamed: 0', 'Unnamed: 0.1'], axis=1) #'STATION' 'ODmol', ,'Data'
print("X_t shape", X_t.shape)

# target variable
y = dataset['DO']  #ODmol

print("y shape", y.shape)
print("Etichette: ", y)

y.value_counts()

y.value_counts().plot.pie(autopct='%.2f', colors = ['lightblue', 'orange'] )

"""# ▶ Divide training and testing
*   Keep the test set separated!



"""

# Split dataset into training set and test set
X_train, X_test, y_train, y_test = train_test_split(X_t, y, test_size=0.3, stratify=y) # 70% training and 30% test

"""# UNDERSAMPLING TRIALS

### *Random Undersampling*
"""

'''
from imblearn.under_sampling import RandomUnderSampler

rus = RandomUnderSampler(sampling_strategy=1)
X_train_res, y_train_res = rus.fit_resample(X_train, y_train)

ax = y_train_res.value_counts().plot.pie(autopct='%.2f')
_ = ax.set_title("Under-sampling")

#y_train_res.value_counts()

"""### *Tomek Links Undersampling*"""

'''
from imblearn.under_sampling import TomekLinks

tl = TomekLinks(sampling_strategy=0)
X_train_tl, y_train_tl, id_tl = tl.fit_sample(X_train, y_train)

print('Removed indexes:', id_tl)

plot_2d_space(X_train_tl, y_train_tl, 'Tomek links under-sampling')

"""# OVERSALMPLING TRIALS

https://www.kaggle.com/code/rafjaa/resampling-strategies-for-imbalanced-datasets/notebook

### *Random Oversampling*
"""

from imblearn.over_sampling import RandomOverSampler

ros = RandomOverSampler(sampling_strategy="not majority")
X_train_res, y_train_res = ros.fit_resample(X_train, y_train)

ax = y_train_res.value_counts().plot.pie(autopct='%.2f')
_ = ax.set_title("Over-sampling")

'''
from collections import Counter
from sklearn.datasets import make_classification
from imblearn.over_sampling import SMOTE 
from matplotlib import pyplot
from numpy import where

'''
oversample = SMOTE()
X_train_res, y_train_res = oversample.fit_resample(X_train, y_train)

'''
ax = y_train_res.value_counts().plot.pie(autopct='%.2f')
_ = ax.set_title("Over-sampling_SMOTE")

"""# OVER & UNDER SAMPLING with SMOTETomek

"""

'''
from imblearn.combine import SMOTETomek

smt = SMOTETomek(sampling_strategy='auto')
X_train_smt, y_train_smt = smt.fit_resample(X_train, y_train)

'''
def plot_2d_space(x_train, y_train, label='Classes'):   
    colors = ['#1F77B4', '#FF7F0E']
    markers = ['o', 's']
    for l, c, m in zip(np.unique(y), colors, markers):
        plt.scatter(
            X_train[y_train==l, 0],
            X_train[y_train==l, 1],
            c=c, label=l, marker=m
        )
    plt.title(label)
    plt.legend(loc='upper right')
    plt.show()

#plot_2d_space(X_train_smt, y_train_smt, 'SMOTE + Tomek links')

"""# ▶ *train resampled and test to numpy*"""

X_train = X_train_res.to_numpy()
y_train = y_train_res.to_numpy()
#X_train = X_train_smt.to_numpy()
#y_train =y_train_smt.to_numpy()

X_test = X_test.to_numpy()
y_test = y_test.to_numpy()

"""#**RANDOM** **FOREST**

## RF traditional method - **Train** **Model**
"""

#SETTING THE SEARCH SPACE

# Number of trees in random forest
n_estimators = [10, 50, 100, 500, 700]

# Maximum number of levels in tree
max_depth = [3, 6, 10, None]

# Minimum number of samples required to split a node
min_samples_split = [3, 5, 7]

# Create the random grid
random_grid = {'n_estimators': n_estimators,
               'max_depth': max_depth,
               'min_samples_split': min_samples_split}   #learning rate

# Use the random grid to search for best hyperparameters
rf = RandomForestClassifier()
rf_random = RandomizedSearchCV(rf, random_grid, n_iter=10, cv = 10, verbose = 4, n_jobs = -1)
# Fit the random search model
rf_random.fit(X_train, y_train)

"""## Performances"""

#best hyperparameters
print(rf_random.best_params_)

best_rf = RandomForestClassifier(n_estimators=50, max_depth=10 , min_samples_split=5, min_samples_leaf=1)   # class_weight='balanced_subsample
best_rf.fit(X_train, y_train)

#create prediction basing on the test set
y_pred = best_rf.predict(X_test)
ytrain_pred = best_rf.predict(X_train)

#create prediction OF THE PROBABILITIES basing on the test set
#y_pred = best_rf.predict_proba(X_test)
#ytrain_pred = best_rf.predict_proba(X_train)

#ytrain_pred

#print("Accuracy train: ", accuracy_score(y_train, ytrain_pred))
print("Accuracy test: ", accuracy_score(y_test, y_pred))
#print('F1_score train: ',f1_score(y_train, ytrain_pred))
#print('Roc auc train: ',roc_auc_score(y_train, ytrain_pred))

features = X_t.columns
importances = best_rf.feature_importances_
indices = np.argsort(importances)
plt.figure(figsize=(10,10))
plt.title('Feature Importances')
plt.barh(range(len(indices)), importances[indices], color='b', align='center')
plt.yticks(range(len(indices)), [features[i] for i in indices])
plt.xlabel('Relative Importance')
plt.show()
#plt.savefig(output_path+'features_importance.png')

# get the probability distribution  #probas = rf_clf.predict_proba(X_test)
# plot
plt.figure(dpi=150)
plt.hist(y_pred, bins=20)
plt.title('Classification Probabilities')
plt.xlabel('Probability')
plt.ylabel('# of Instances')
plt.xlim([0.5, 1.0])
plt.legend()
plt.show()

"""## ROC AUC"""

#ROC CURVE
from sklearn.metrics import RocCurveDisplay
best_rf_disp = RocCurveDisplay.from_estimator(best_rf, X_test, y_test)
plt.show()

'''
#PRECISION AND RECALL CURVE
from sklearn.metrics import precision_recall_curve, average_precision_score, auc
# get precision and recall values
precision, recall, thresholds = precision_recall_curve(y_test, probas[:,0], pos_label=0)
# average precision score
avg_precision = average_precision_score(y_test, probas[:,1])
# precision auc
pr_auc = auc(recall, precision)
# plot
plt.figure(dpi=150)
plt.plot(recall, precision, lw=1, color='blue', label=f'AP={avg_precision:.3f}; AUC={pr_auc:.3f}')
plt.fill_between(recall, precision, -1, facecolor='lightblue', alpha=0.5)
plt.title('PR Curve for RF classifier')
plt.xlabel('Recall (TPR)')
plt.ylabel('Precision')
plt.xlim([-0.05, 1.05])
plt.ylim([-0.05, 1.05])
plt.legend()
plt.show()

#Import scikit-learn metrics module for accuracy calculation
from sklearn import metrics
# Model Accuracy, how often is the classifier correct?
print("Accuracy:",metrics.accuracy_score(y_test, y_pred))
print(metrics.classification_report(y_test, y_pred))
#print("roc_auc:",metrics.roc_auc_score(y_test, y_pred))

conf_mat = confusion_matrix(y_test, y_pred)
plt.title("Confusion Matrix")
sns.heatmap(conf_mat,annot=True,fmt='.0f')
plt.show()
#plt.savefig(output_path+'confusion_matrix.png')

#unique, counts = np.unique(y_pred, return_counts=True)
#dict(zip(unique, counts))

"""### *RF without best paramether method*"""

'''
from sklearn.linear_model import Ridge
from sklearn.model_selection import GridSearchCV

'''
parameters = {'n_estimators': [750],'criterion':['gini', 'entropy']}

'''
model = GridSearchCV(
      RandomForestClassifier(),
      param_grid=parameters,
      n_jobs=10, cv=10)
model.fit(X_train,y_train)
rm_pred=model.predict(X_test)
print("Accuracy Test:",metrics.accuracy_score(y_test, rm_pred))

'''
!pip install scikit-plot
import scikitplot.metrics as splt
splt.plot_confusion_matrix(y_test, rm_pred)

'''
print(metrics.classification_report(y_test, rm_pred))

"""# ⬛ Save and load the model"""

#salva il modello
joblib.dump(best_rf, path_stations + "RF_hypoxia_undersample.joblib")
#joblib.dump(best_rf, path + "random_forest_full_pt_norm.joblib")

best_rf = joblib.load(path_stations + "RF_hypoxia_undersample.joblib")

"""--------------------------------------------------------------------------------
# ⛔ FOR THODORIS, STOP HERE :)

# Random Forest for unbalanced datasets

### Random Forest for Imbalanced Classification
"""

# class balanced random forest for imbalanced classification
from numpy import mean
from sklearn.datasets import make_classification
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.ensemble import RandomForestClassifier

# define model
model = RandomForestClassifier(n_estimators=10, class_weight='balanced')

# define evaluation procedure
cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)

# evaluate model
scores = cross_val_score(model, X_train, y_train, scoring='roc_auc', cv=cv, n_jobs=-1)

# summarize performance
print('Mean ROC AUC: %.3f' % mean(scores))

"""### *Class_weight argument to the value ‘balanced_subsample*"""

model = RandomForestClassifier(n_estimators=10, class_weight='balanced_subsample')

# define evaluation procedure
cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)

# evaluate model
scores = cross_val_score(model, X_train, y_train, scoring='roc_auc', cv=cv, n_jobs=-1)

# summarize performance
print('Mean ROC AUC: %.3f' % mean(scores))

"""### *BalancedRandomForestClassifier class* """

from imblearn.ensemble import BalancedRandomForestClassifier

# define model
model = BalancedRandomForestClassifier(n_estimators=10)

# define evaluation procedure
cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)

# evaluate model
scores = cross_val_score(model, X_train, y_train, scoring='roc_auc', cv=cv, n_jobs=-1)

# summarize performance
print('Mean ROC AUC: %.3f' % mean(scores))

"""# COMPARE CLASSIFIERS"""

from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.linear_model import SGDClassifier

"""Defining learning classifiers"""

names = ["Linear_SVM", "Polynomial_SVM", "RBF_SVM",  "Neural_Net", "AdaBoost",
         "Naive_Bayes"]

classifiers = [
    SVC(kernel="linear", C=0.025),
    SVC(kernel="poly", degree=3, C=0.025),
    SVC(kernel="rbf", C=1, gamma=2),
    MLPClassifier(alpha=1, max_iter=1000),
    AdaBoostClassifier(n_estimators=100),
    GaussianNB()]

model_ada = AdaBoostClassifier(n_estimators=100)

"""Build Model, Apply Model on Test Data & Record Accuracy Scores"""

scores = []
for name, clf in zip(names, classifiers):
    clf.fit(X_train, y_train)
    score = clf.score(X_test, y_test)
    scores.append(score)

scores

model_ada.fit(X_train, y_train)
score_model_ada = model_ada.score(X_test, y_test)

score_model_ada

"""Analysis of Model Performance"""

import seaborn as sns

"""Create data frame of model performance"""

df = pd.DataFrame()
df['name'] = names
df['score'] = scores
df

"""Adding colors to the data frame"""

#https://pandas.pydata.org/pandas-docs/stable/user_guide/style.html

cm = sns.light_palette("green", as_cmap=True)
s = df.style.background_gradient(cmap=cm)
s

"""Bar plot of model performance"""

sns.set(style="whitegrid")
ax = sns.barplot(y="name", x="score", data=df)

#create prediction basing on the test set
y_pred = model_ada.predict(X_test)
ytrain_pred = model_ada.predict(X_train)

"""vorrei capire se da qui posso ricavarmi le accuraci di ogni modello"""

print(metrics.classification_report(y_test, y_pred))

conf_mat = confusion_matrix(y_test, y_pred)
plt.title("Confusion Matrix")
sns.heatmap(conf_mat,annot=True,fmt='.0f')
plt.show()

"""# LOGISTIC REGRESSION"""

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

logistic = LogisticRegression(class_weight="balanced").fit(X_train, y_train)
y_pred = logistic.predict(X_test)

print('In-sample accuracy: %0.3f' %
      accuracy_score(y_train, logistic.predict(X_train)))
print('Out-of-sample accuracy: %0.3f' %
      accuracy_score(y_test, y_pred))

print(metrics.classification_report(y_test, y_pred))

conf_mat = confusion_matrix(y_test, y_pred)
plt.title("Confusion Matrix")
sns.heatmap(conf_mat,annot=True,fmt='.0f')
plt.show()

# Evaluate a score by cross-validation.
scores = cross_val_score(logistic, X_train, y_train, scoring='roc_auc', cv=None, n_jobs=-1)

# summarize performance
print('Mean ROC AUC: %.3f' % mean(scores))

#ROC CURVE
from sklearn.metrics import RocCurveDisplay
best_rf_disp = RocCurveDisplay.from_estimator(logistic, X_test, y_test)
plt.show()

"""## Probability of each sample to belong to a class"""

for var, coef in zip(dataset.w_temperature,
                     logistic.coef_[0]):
  print("%7s : %7.3f" %(var, coef))

print('\nclasses:', logistic.classes_)
print('\nProbs:\n', logistic.predict_proba(X_test)[:365,:])

"""# WEIGHTED SVM """

# fit a svm on an imbalanced classification dataset
from numpy import mean
from sklearn.datasets import make_classification
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.svm import SVC

# define model
#weights = {0:100.0, 1:1.0}
SVM_model = SVC(gamma='scale', class_weight='balanced')  # , class_weight='balanced'

# define evaluation procedure
cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)

# evaluate model
scores = cross_val_score(SVM_model, X_t, y, scoring='roc_auc', cv=cv, n_jobs=-1)
# summarize performance
print('Mean ROC AUC: %.3f' % mean(scores))

SVM_model.fit(X_train, y_train)

y_pred = SVM_model.predict(X_test)

print('In-sample accuracy: %0.3f' %
      accuracy_score(y_train, SVM_model.predict(X_train)))
print('Out-of-sample accuracy: %0.3f' %
      accuracy_score(y_test, y_pred))

print(metrics.classification_report(y_test, y_pred))

conf_mat = confusion_matrix(y_test, y_pred)
plt.title("Confusion Matrix")
sns.heatmap(conf_mat,annot=True,fmt='.0f')
plt.show()

"""### Bagging Classifier for imbalanced classification"""

# bagged decision trees on an imbalanced classification problem
from numpy import mean
from sklearn.datasets import make_classification
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.ensemble import BaggingClassifier

...
# define model
model = BaggingClassifier()

...
# define evaluation procedure
cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
# evaluate model
scores = cross_val_score(model, X, y, scoring='roc_auc', cv=cv, n_jobs=-1)

# summarize performance
print('Mean ROC AUC: %.3f' % mean(scores))

"""# BalancedBaggingClassifier class."""

# bagged decision trees with random undersampling for imbalanced classification
from numpy import mean
from sklearn.datasets import make_classification
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold
from imblearn.ensemble import BalancedBaggingClassifier

# define model
model = BalancedBaggingClassifier()

# define evaluation procedure
cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)

# evaluate model
scores = cross_val_score(model, X_t, y, scoring='roc_auc', cv=cv, n_jobs=-1)

# summarize performance
print('Mean ROC AUC: %.3f' % mean(scores))



"""## EasyEnsembleClassifier"""

# easy ensemble for imbalanced classification
from numpy import mean
from sklearn.datasets import make_classification
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold
from imblearn.ensemble import EasyEnsembleClassifier

# define model
model = EasyEnsembleClassifier(n_estimators=10)

# define evaluation procedure
cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)

# evaluate model
scores = cross_val_score(model, X_t, y, scoring='roc_auc', cv=cv, n_jobs=-1)

# summarize performance
print('Mean ROC AUC: %.3f' % mean(scores))

y

"""# FIT THE MODEL AND SEE THE PERFORMANCES"""

# Fit the random search model
model.fit(X_train, y_train)

#create prediction basing on the test set
y_pred = model.predict(X_test)
ytrain_pred = model.predict(X_train)

print("Accuracy test: ", accuracy_score(y_test, y_pred))
print(metrics.classification_report(y_test, y_pred))

conf_mat = confusion_matrix(y_test, y_pred)
plt.title("Confusion Matrix")
sns.heatmap(conf_mat,annot=True,fmt='.0f')
plt.show()

#ROC CURVE
from sklearn.metrics import RocCurveDisplay
best_rf_disp = RocCurveDisplay.from_estimator(model, X_test, y_test)
plt.show()
