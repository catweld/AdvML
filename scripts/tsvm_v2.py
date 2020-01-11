# coding:utf-8
import numpy as np
import sklearn.svm as svm
from joblib import *
import pickle
from sklearn.model_selection import train_test_split,cross_val_score

class TSVM(object):
    def __init__(self):
        pass

    def initial(self, kernel, gamma, C ,num_positives): # C_labeled, C_unlabeled,
        '''
        Initial TSVM
        Parameters
        ----------
        kernel: kernel of svm
        '''
        self.kernel = kernel
        self.Cl, self.Cu = 1.5, 0.001
        self.gamma = gamma
        #self.C_labeled = C_labeled
        #self.C_unlabeled = C_unlabeled
        self.C = C
        self.clf = svm.SVC(C=self.C, kernel=self.kernel, gamma=self.gamma)
        self.num_positives = num_positives
        
        #self.C_unl_negative = 10**(-5)
        #self.C_unl_positive = None 
        
    def load(self, model_path='./TSVM.model'):
        '''
        Load TSVM from model_path
        Parameters
        ----------
        model_path: model path of TSVM
                        model should be svm in sklearn and saved by sklearn.externals.joblib
        '''
        self.clf = joblib.load(model_path)

    def train(self, X1, Y1, X2):
        '''
        Train TSVM by X1, Y1, X2
        Parameters
        ----------
        X1: Input data with labels
                np.array, shape:[n1, m], n1: numbers of samples with labels, m: numbers of features
        Y1: labels of X1
                np.array, shape:[n1, ], n1: numbers of samples with labels
        X2: Input data without labels
                np.array, shape:[n2, m], n2: numbers of samples without labels, m: numbers of features
        '''
        
        self.C_unl_positive = 10**(-5) * self.num_positives/(len(X1)-self.num_positives)

        
        N = len(X1) + len(X2)
        sample_weight = np.ones(N)
        sample_weight[len(X1):] = self.Cu

        self.clf.fit(X1, Y1)
        
                
        Y2_d = self.clf.decision_function(X2)  
        Y2 = np.zeros(len(X2))
        Y2[:] = -1
        Y2[np.argsort(Y2_d)[-self.num_positives:]] = 1
        
        Y2 = np.expand_dims(Y2, 1)
        X2_id = np.arange(len(X2))
        Y1 = np.expand_dims(Y1, 1)
        X3 = np.vstack([X1, X2])
        Y3 = np.vstack([Y1, Y2])

        #while (self.C_unl_positive < self.C_unlabeled) or (self.C_unl_negative < self.C_unlabeled):
        while self.Cu < self.Cl:
            self.clf.fit(X3, Y3, sample_weight=sample_weight)
            while True:
                Y2_d = self.clf.decision_function(X2)    # linear: w^Tx + b
                Y2 = Y2.reshape(-1)
                epsilon = 1 - Y2 * Y2_d   # calculate function margin
                positive_set, positive_id = epsilon[Y2 > 0], X2_id[Y2 > 0]
                negative_set, negative_id = epsilon[Y2 < 0], X2_id[Y2 < 0]
                positive_max_id = positive_id[np.argmax(positive_set)]
                negative_max_id = negative_id[np.argmax(negative_set)]
                a, b = epsilon[positive_max_id], epsilon[negative_max_id]
                if a > 0 and b > 0 and a + b > 2.0:
                    Y2[positive_max_id] = Y2[positive_max_id] * -1
                    Y2[negative_max_id] = Y2[negative_max_id] * -1
                    Y2 = np.expand_dims(Y2, 1)
                    Y3 = np.vstack([Y1, Y2])
                    self.clf.fit(X3, Y3, sample_weight=sample_weight)
                else:
                    break
            self.Cu = min(2*self.Cu, self.Cl)
            sample_weight[len(X1):] = self.Cu

    def score(self, X, Y):
        '''
        Calculate accuracy of TSVM by X, Y
        Parameters
        ----------
        X: Input data
                np.array, shape:[n, m], n: numbers of samples, m: numbers of features
        Y: labels of X
                np.array, shape:[n, ], n: numbers of samples
        Returns
        -------
        Accuracy of TSVM
                float
        '''
        return self.clf.score(X, Y)

    def predict(self, X):
        '''
        Feed X and predict Y by TSVM
        Parameters
        ----------
        X: Input data
                np.array, shape:[n, m], n: numbers of samples, m: numbers of features
        Returns
        -------
        labels of X
                np.array, shape:[n, ], n: numbers of samples
        '''
        return self.clf.predict(X)

    def save(self, path='./TSVM.model'):
        '''
        Save TSVM to model_path
        Parameters
        ----------
        model_path: model path of TSVM
                        model should be svm in sklearn
        '''
        joblib.dump(self.clf, path)

'''
if __name__ == '__main__':
    model = TSVM()
    model.initial('rbf',gamma=1,C=10)
    model.train(train_labeled, train_target, train_unlabeled)
    Y_hat = model.predict(test_inputs)
    accuracy = model.score(test_inputs, test_output)
    print(accuracy)
'''

