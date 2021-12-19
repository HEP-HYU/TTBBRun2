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

class MakeModel:
    def __init__(self, config):
        self.config = config
        self.auc_list = []
        self.val_auc_list = []

        self._load_array()

    def _load_array(self):
        import utils as ut
        self.train_input = self.config['train']+'/../array_train_ttbb.h5'
        if not os.path.exists(self.train_input):
            ut.mergeHDF(self.config['train'], "array_train_ttbb")

        if not os.path.exists(self.config['model']['dir']):
            os.makedirs(self.config['model']['dir'])
        else:
            for item in os.listdir(self.config['model']['dir']):
                if item.endswith('pdf') or item.endswith('h5') or item.endswith('log'):
                    os.remove(os.path.join(self.config['model']['dir'], item))

    def _save_config(self):
        import yaml
        with open(self.config_file, 'w') as f:
            self.config = yaml.dump(f)

    def _draw_correlation(self, data, name, **kwds):
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

    def _draw_input_variables(self, sigdata, bkgdata, signame, bkgname, **kwds):
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

        #self._draw_correlations(data.loc[data['signal'] == 0].drop('signal', axis=1), 'bkg')
        #self._draw_correlations(data.loc[data['signal'] == 1].drop('signal', axis=1), 'sig')
        #self._draw_input_variables(data.loc[data['signal'] == 1].drop('signal', axis=1), data.loc[data['signal'] == 0].drop('signal', axis=1), 'sig', 'bkg')

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
                                     callbacks=[RocCallback(training_data=(X_train,Y_train), validation_data=(X_test,Y_test), model=model, output_dir=self.config['output'], self.auc_list, self.val_auc_list)]
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

        plt.plot(self.auc_list)
        plt.plot(self.val_auc_list)
        plt.title('Area under curve')
        plt.ylabel('AUC')
        plt.xlabel('Epoch')
        plt.legend(['Train','Test'], loc='upper right')
        plt.savefig(os.path.join(configDir,weightDir+ver,'fig_score_auc.pdf'))
        plt.gcf().clear()

        self.config['model'] = str(bestModel)
        self._save_config()
