#! /usr/bin/env python
from __future__ import print_function
import sys, os
import google.protobuf

os.environ["CUDA_VISIBLE_DEVICES"] = "2"

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.preprocessing import StandardScaler, label_binarize
from sklearn.decomposition import PCA
from sklearn.utils import shuffle, class_weight
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score
import numpy as np
from root_numpy import array2tree, tree2array
import csv
import re
import string
import math
from array import array

import tensorflow as tf
import keras
from keras.utils import np_utils, multi_gpu_model
from keras.models import Model, Sequential, load_model
from keras.layers import Input, Dense, Activation, Dropout, add
from keras.layers.normalization import BatchNormalization
from keras.regularizers import l2
from keras.optimizers import Adam, SGD
from keras.callbacks import Callback, ModelCheckpoint

class RocCallback(Callback):
    def __init__(self, training_data, validation_data, model, output_dir, auc_list, val_auc_list):
        self.x = training_data[0]
        self.y = training_data[1]
        self.x_val = validation_data[0]
        self.y_val = validation_data[1]
        self.auc_list = auc_list
        self.val_auc_list = val_acu_list
        self.model_to_save = model
        self.output_dir = output_dir

    def on_train_begin(self, logs={}):
        return

    def on_train_end(self, logs={}):
        return

    def on_epoch_begin(self, epoch, logs={}):
        return

    def on_epoch_end(self, epoch, logs={}):
        ############
        #compute AUC
        ############
        print('Calculating AUC of epoch '+str(epoch+1))
        y_pred = self.model.predict(self.x, batch_size=2000)
        roc = roc_auc_score(self.y, y_pred)
        y_pred_val = self.model.predict(self.x_val, batch_size=2000)
        roc_val = roc_auc_score(self.y_val, y_pred_val)
        print('\rroc-auc: %s - roc-auc_val: %s' % (str(round(roc,4)), str(round(roc_val,4))),end=100*' '+'\n')
        self.auc_list.append(roc)
        self.val_auc_list.append(roc_val)

        ###################
        #Calculate f1 score
        ###################
        val_predict = (y_pred_val[:,1]).round()
        val_targ = self.y_val[:,1]
        val_f1 = f1_score(val_targ, val_predict)
        val_recall = recall_score(val_targ, val_predict)
        val_precision = precision_score(val_targ, val_predict)
        print('val_f1: %.4f, val_precision: %.4f, val_recall %.4f' %(val_f1, val_precision, val_recall))

        ###############
        #Plot ROC curve
        ###############
        fpr = dict()
        tpr = dict()
        roc_auc = dict()
        #fpr[0], tpr[0], thresholds0 = roc_curve(self.y_val[:,0], y_pred_val[:,0], pos_label=1)#w.r.t bkg is truth in val set
        fpr[1], tpr[1], thresholds1 = roc_curve(self.y_val[:,1], y_pred_val[:,1], pos_label=1)#w.r.t sig is truth in val set
        fpr[2], tpr[2], thresholds2 = roc_curve(self.y[:,1], y_pred[:,1], pos_label=1)#w.r.t sig is truth in training set, for overtraining check
        #plt.plot(1-fpr[0], 1-(1-tpr[0]), 'b')#same as [1]
        plt.plot(tpr[1], 1-fpr[1])#HEP style ROC
        plt.plot(tpr[2], 1-fpr[2])#training ROC
        plt.xlabel('Signal Efficiency')
        plt.ylabel('Background Rejection')
        plt.title('ROC Curve')
        plt.legend(['Test', 'Train'], loc='lower left')
        plt.savefig(os.path.join(self.output_dir, 'fig_roc_%d_%.4f.pdf' %(epoch+1,round(roc_val,4))))
        plt.gcf().clear()

        ########################################################
        #Overtraining Check, as well as bkg & sig discrimination
        ########################################################
        bins = 40
        scores = [tpr[1], fpr[1], tpr[2], fpr[2]]
        low = min(np.min(d) for d in scores)
        high = max(np.max(d) for d in scores)
        low_high = (low,high)

        #test is filled
        plt.hist(tpr[1],
            color='b', alpha=0.5, range=low_high, bins=bins,
            histtype='stepfilled', density=True, label='S (test)')
        plt.hist(fpr[1],
            color='r', alpha=0.5, range=low_high, bins=bins,
            histtype='stepfilled', density=True, label='B (test)')

        #training is dotted
        hist, bins = np.histogram(tpr[2], bins=bins, range=low_high, density=True)
        scale = len(tpr[2]) / sum(hist)
        err = np.sqrt(hist * scale) / scale
        width = (bins[1] - bins[0])
        center = (bins[:-1] + bins[1:]) / 2
        plt.errorbar(center, hist, yerr=err, fmt='o', c='b', label='S (training)')
        hist, bins = np.histogram(fpr[2], bins=bins, range=low_high, density=True)
        scale = len(tpr[2]) / sum(hist)
        err = np.sqrt(hist * scale) / scale
        plt.errorbar(center, hist, yerr=err, fmt='o', c='r', label='B (training)')

        plt.xlabel("Deep Learning Score")
        plt.ylabel("Arbitrary units")
        plt.legend(loc='best')
        overtrain_path = self.output_dir+'/fig_overtraining_%d_%.4f.pdf' %(epoch+1,round(roc_val,4))
        plt.savefig(overtrain_path)
        plt.gcf().clear()
        print('ROC curve and overtraining check plots are saved!')

        del y_pred, y_pred_val, fpr, tpr, roc_auc

        ###############################
        #Save single gpu model manually
        ###############################
        modelfile = 'model_%d_%.4f.h5' %(epoch+1,round(roc_val,4))
        self.model_to_save.save(self.output_dir+'/'+modelfile)
        print('Current model is saved')

        return

    def on_batch_begin(self, batch, logs={}):
        return

    def on_batch_end(self, batch, logs={}):
        return
