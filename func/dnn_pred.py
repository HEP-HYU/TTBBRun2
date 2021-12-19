import os, sys
import time

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, label_binarize
from itertools import groupby
import deepdish.io as io

def prediction(year, inputDir, outputDir):
    start_time = time.time()
    with open('var'+str(year)+'.txt', 'r') as f :
        while True :
            line = f.readline()
            if not line : break
            tmp = line.split()
            if 'ver' in tmp : ver = tmp[1]
            if 'configDir' in tmp : configDir = tmp[1]
            if 'weightDir' in tmp : weightDir = tmp[1]
            if 'modelfile' in tmp : modelfile = tmp[1]

    import tensorflow as tf
    from keras.backend.tensorflow_backend import set_session
    config = tf.ConfigProto()
    config.gpu_options.per_process_gpu_memory_fraction = 0.1
    set_session(tf.Session(config=config))
    import keras
    from keras.models import load_model

    import utils as ut
    varlist = ut.getVarlist()
    model = load_model(configDir+weightDir+ver+'/'+modelfile)

    for sample in os.listdir(inputDir):
        if not os.path.isdir(os.path.join(inputDir, sample)): continue
        if 'Training' in sample: continue
        if not os.path.exists(os.path.join(outputDir, sample)):
            os.makedirs(os.path.join(outputDir, sample))
        for item in os.listdir(os.path.join(inputDir, sample)):
            selEvent = pd.read_hdf(os.path.join(inputDir, sample, item))
            jetCombi = selEvent.filter(varlist)
            scaler = StandardScaler()
            pred = pd.DataFrame([])
            if len(jetCombi) is not 0:
                inputset = np.array(jetCombi)
                inputset_sc = scaler.fit_transform(inputset)
                pred = model.predict(inputset_sc, batch_size = 2000)

            pred = pd.DataFrame(pred, columns=['background','signal'])
            selEvent = pd.concat([selEvent,pred], axis=1)
            idx = selEvent.groupby(['event'])['signal'].transform(max) == selEvent['signal']
            selEvent = selEvent[idx]
            selEvent.reset_index(drop=True, inplace=True)
            io.save(os.path.join(outputDir, sample, item), selEvent)

    #keras.backend.clear_session()
    print "...Prediction is completed"
    print "Running time: %s" % (time.time() - start_time)
