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

import utils as ut

auc_list = []
val_auc_list = []

class RocCallback(Callback):
    def __init__(self, training_data, validation_data, model, output_dir):
        self.x = training_data[0]
        self.y = training_data[1]
        self.x_val = validation_data[0]
        self.y_val = validation_data[1]
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
        auc_list.append(roc)
        val_auc_list.append(roc_val)

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

class MakeModel:
    def __init__(self, train_input, config_file):
        self.config_file = config_file
        self.train_input = train_input
        self.config = {}

    def load_config(self):
        import yaml
        with open(self.config_file, 'r') as f:
            self.config = yaml.load(f)
        if not self.config:
            print "Error: fail loading the config file %s" % self.config_file
            sys.exit(0)

        import utils as ut
        if not os.path.exists(self.train_input):
            ut.mergeHDF(os.path.join(self.config['directory'],'Training'),"array_train_ttbb")

        if not os.path.exists(self.config['output']):
            os.makedirs(self.config['output'])
        else:
            for item in os.listdir(self.config['output']):
                if item.endswith('pdf') or item.endswith('h5') or item.endswith('log'):
                    os.remove(os.path.join(self.config['output'], item))

    def save_config(self):
        import yaml
        with open(self.config_file, 'w') as f:
            self.config = yaml.dump(f)

    def draw_correlation(self, data, name, **kwds):
        """Calculate pairwise correlation between features.

        Extra arguments are passed on to DataFrame.corr()
        """
        # simply call df.corr() to get a table of
        # correlation values if you do not need
        # the fancy plotting
        corrmat = data.corr(**kwds)

        fig, ax1 = plt.subplots(ncols=1, figsize=(6,5))

        opts = {'cmap': plt.get_cmap("RdBu"),
                'vmin': -1, 'vmax': +1}
        heatmap1 = ax1.pcolor(corrmat, **opts)
        plt.colorbar(heatmap1, ax=ax1)

        ax1.set_title("Correlations")

        labels = corrmat.columns.values
        for ax in (ax1,):
            ax.tick_params(labelsize=6)
            # shift location of ticks to center of the bins
            ax.set_xticks(np.arange(len(labels))+0.5, minor=False)
            ax.set_yticks(np.arange(len(labels))+0.5, minor=False)
            ax.set_xticklabels(labels, minor=False, ha='right', rotation=90)
            ax.set_yticklabels(labels, minor=False)

        plt.tight_layout()
        #plt.show()
        if name == 'sig' :
            plt.savefig(configDir+weightDir+ver+'/fig_corr_s.pdf')
            print('Correlation matrix for signal is saved!')
            plt.gcf().clear()
        elif name == 'bkg' :
            plt.savefig(configDir+weightDir+ver+'/fig_corr_b.pdf')
            plt.gcf().clear()
            print('Correlation matrix for background is saved!')
        else : print('Wrong class name!')

    def draw_input_variables(self, sigdata, bkgdata, signame, bkgname, **kwds):
        print('Plotting input variables')
        bins = 40
        for colname in sigdata:
            dataset = [sigdata, bkgdata]
            low = min(np.min(d[colname].values) for d in dataset)
            high = max(np.max(d[colname].values) for d in dataset)
            if high > 500: low_high = (low,500)
            else: low_high = (low,high)

            plt.figure()
            sigdata[colname].plot.hist(color='b', density=True, range=low_high, bins=bins, histtype='step', label='signal')
            bkgdata[colname].plot.hist(color='r', density=True, range=low_high, bins=bins, histtype='step', label='background')
            plt.xlabel(colname)
            plt.ylabel('A.U.')
            plt.title('Intput variables')
            plt.legend(loc='upper right')
            plt.savefig(configDir+weightDir+ver+'/fig_input_'+colname+'.pdf')
            plt.gcf().clear()
            plt.close()

    def compile_train(self):
        multiGPU = True
        if os.environ['CUDA_VISIBLE_DEVICES'] in ['0','1','2','3']: multiGPU = False

        data = pd.read_hdf(self.train_input)

        ##########################################
        #drop phi and label features, correlations
        ##########################################
        labels = data.filter(['signal'], axis=1)
        data = data.filter(['signal']+ut.getVarlist())
        data.astype('float32')

        #self.draw_correlations(data.loc[data['signal'] == 0].drop('signal', axis=1), 'bkg')
        #self.draw_correlations(data.loc[data['signal'] == 1].drop('signal', axis=1), 'sig')
        #self.draw_input_variables(data.loc[data['signal'] == 1].drop('signal', axis=1), data.loc[data['signal'] == 0].drop('signal', axis=1), 'sig', 'bkg')

        data = data.drop('signal', axis=1) #then drop label

        ###############
        #split datasets
        ###############
        train_sig = labels.loc[labels['signal'] == 1].sample(frac=0.8,random_state=200)
        train_bkg = labels.loc[labels['signal'] == 0].sample(frac=0.8,random_state=200)
        test_sig = labels.loc[labels['signal'] == 1].drop(train_sig.index)
        test_bkg = labels.loc[labels['signal'] == 0].drop(train_bkg.index)

        train_idx = pd.concat([train_sig, train_bkg]).index
        test_idx = pd.concat([test_sig, test_bkg]).index

        data_train = data.loc[train_idx,:].copy()
        data_test = data.loc[test_idx,:].copy()
        labels_train = labels.loc[train_idx,:].copy()
        labels_test = labels.loc[test_idx,:].copy()

        print('Training signal: '+str(len(train_sig))+' / testing signal: '+str(len(test_sig))+' / training background: '+str(len(train_bkg))+' / testing background: '+str(len(test_bkg)))

        labels_train = labels_train.values
        Y_train = np_utils.to_categorical(labels_train)
        labels_test = labels_test.values
        Y_test = np_utils.to_categorical(labels_test)

        ########################
        #Standardization and PCA
        ########################
        scaler = StandardScaler()
        data_train_sc = scaler.fit_transform(data_train)
        data_test_sc = scaler.fit_transform(data_test)
        X_train = data_train_sc
        X_test = data_test_sc

        #################################
        #Keras model compile and training
        #################################
        nvar = len(ut.getVarlist())
        a = 300
        b = 0.08
        init = 'glorot_uniform'

        with tf.device("/cpu:0") :
            inputs = Input(shape=(nvar,))
            x = Dense(a, kernel_regularizer=l2(1E-2))(inputs)
            x = Dropout(b)(x)
            x = BatchNormalization()(x)
            #branch_point1 = Dense(a, name='branch_point1')(x)
            x = Dense(a, activation='relu', kernel_initializer=init, bias_initializer='zeros')(x)
            x = Dropout(b)(x)
            x = BatchNormalization()(x)
            x = Dense(a, activation='relu', kernel_initializer=init, bias_initializer='zeros')(x)
            x = Dropout(b)(x)
            #x = add([x, branch_point1])
            x = BatchNormalization()(x)
            #branch_point2 = Dense(a, name='branch_point2')(x)
            x = Dense(a, activation='relu', kernel_initializer=init, bias_initializer='zeros')(x)
            x = Dropout(b)(x)
            x = BatchNormalization()(x)
            x = Dense(a, activation='relu', kernel_initializer=init, bias_initializer='zeros')(x)
            x = Dropout(b)(x)
            #x = add([x, branch_point2])
            x = BatchNormalization()(x)
            #branch_point3 = Dense(a, name='branch_point3')(x)
            x = Dense(a, activation='relu', kernel_initializer=init, bias_initializer='zeros')(x)
            x = Dropout(b)(x)
            x = BatchNormalization()(x)
            x = Dense(a, activation='relu', kernel_initializer=init, bias_initializer='zeros')(x)
            x = Dropout(b)(x)
            #x = add([x, branch_point3])
            x = BatchNormalization()(x)
            #branch_point4 = Dense(a, name='branch_point4')(x)
            x = Dense(a, activation='relu', kernel_initializer=init, bias_initializer='zeros')(x)
            x = Dropout(b)(x)
            x = BatchNormalization()(x)
            x = Dense(a, activation='relu', kernel_initializer=init, bias_initializer='zeros')(x)
            x = Dropout(b)(x)
            #x = add([x, branch_point4])
            x = BatchNormalization()(x)
            #branch_point5 = Dense(a, name='branch_point5')(x)
            x = Dense(a, activation='relu', kernel_initializer=init, bias_initializer='zeros')(x)
            x = Dropout(b)(x)
            x = BatchNormalization()(x)
            x = Dense(a, activation='relu', kernel_initializer=init, bias_initializer='zeros')(x)
            x = Dropout(b)(x)
            #x = add([x, branch_point5])
            #x = BatchNormalization()(x)
            #x = Dense(a, activation='relu', kernel_initializer=init, bias_initializer='zeros')(x)
            #x = Dropout(b)(x)
            predictions = Dense(2, activation='softmax')(x)
            model = Model(inputs=inputs, outputs=predictions)

        if multiGPU : train_model = multi_gpu_model(model, gpus=4)
        else : train_model = model

        adam=keras.optimizers.Adam(lr=1E-3, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=1E-3)
        train_model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy','binary_accuracy'])
#train_model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy','categorical_accuracy'])

        modelfile = 'model_{epoch:02d}_{val_binary_accuracy:.4f}.h5'
        checkpoint = ModelCheckpoint(self.config['output']+'/'+modelfile, monitor='val_binary_accuracy', verbose=1, save_best_only=False)#, mode='max')

        history = train_model.fit(X_train, Y_train,
                                     epochs=30, batch_size=1024,
                                     validation_data=(X_test,Y_test),
                                     #class_weight={ 0: 14, 1: 1 }, 
                                     callbacks=[RocCallback(training_data=(X_train,Y_train), validation_data=(X_test,Y_test), model=model, output_dir=self.config['output'])]
                                     )

        print("Now predict score with test set")
        bestModel = ""
        best_acc = 0.0
        for filename in os.listdir(configDir+weightDir+ver):
            if not "h5" in filename : continue
            tmp = filename.split('.')
            tmp_acc = float("0."+tmp[1])
            if tmp_acc > best_acc :
                best_acc = tmp_acc
                bestModel = filename

        print("Use "+bestModel)
        model_best = load_model(self.config['output']+'/'+bestModel)
        y_pred = model_best.predict(X_test, batch_size=1024)

        plt.plot(history.history['binary_accuracy'])
        plt.plot(history.history['val_binary_accuracy'])
        plt.title('Model accuracy')
        plt.ylabel('Accuracy')
        plt.xlabel('Epoch')
        plt.legend(['Train','Test'], loc='lower right')
        plt.savefig(os.path.join(configDir,weightDir+ver,'fig_score_acc.pdf'))
        plt.gcf().clear()

        plt.plot(history.history['loss'])
        plt.plot(history.history['val_loss'])
        plt.title('Binary crossentropy')
        plt.ylabel('Loss')
        plt.xlabel('Epoch')
        plt.legend(['Train','Test'],loc='upper right')
        plt.savefig(os.path.join(configDir,weightDir+ver,'fig_score_loss.pdf'))
        plt.gcf().clear()

        plt.plot(auc_list)
        plt.plot(val_auc_list)
        plt.title('Area under curve')
        plt.ylabel('AUC')
        plt.xlabel('Epoch')
        plt.legend(['Train','Test'], loc='upper right')
        plt.savefig(os.path.join(configDir,weightDir+ver,'fig_score_auc.pdf'))
        plt.gcf().clear()

        self.config['model'] = str(bestModel) 
