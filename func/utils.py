import sys, os
import math
from tqdm import tqdm
import pandas as pd

def getVarlist():
    column = [
        'bbM', 'bbdR', 'bbdPhi', 'bbdEta', 'bbPhi', 'bbEta',
        'bbnM', 'bbndR', 'b1nM', 'b1ndR', 'b2nM', 'b2ndR',
        'bblM', 'bbldR', 'b1lM', 'b1ldR', 'b2lM', 'b2ldR',
        'bblndR',
        'b1pT', 'b1Eta', 'b1E', 'b1CSV', 'b1M',
        'b2pT', 'b2Eta', 'b2E', 'b2CSV', 'b2M',
        'lpT', 'lEta', 'lE',
        'npT', 'nPhi',
        'nbjets']
    return column

def getHistXlabel():
    dictionary = {
        'bbM':'m_{b#bar{b}}', 'bbdR':'#DeltaR_{b#bar{b}}', 
        'bbdPhi':'#Delta#phi_{b#bar{b}}', 'bbdEta':'#Delta#eta_{b#bar{b}}',
        'bbPhi':'#phi_{b#bar{b}}', 'bbEta':'#eta_{b#bar{b}}',
        'bbnM':'m_{b#bar{b}#nu}', 'bbndR':'#DeltaR_{b#bar{b}#nu}',
        'b1nM':'m_{b1#nu}', 'b1ndR':'#DeltaR_{b1#nu}', 'b2nM':'m_{b2#nu}', 'b2ndR':'DeltaR_{b2#nu}',
        'bblM':'m_{b#bar{b}lep}', 'bbldR':'#DeltaR_{b#bar{b}lep}',
        'b1lM':'m_{b1lep}', 'b1ldR':'#DeltaR_{b1lep}', 'b2lM':'m_{b2lep}', 'b2ldR':'DeltaR_{b2lep}',
        'bblndR':'#DeltaR_{b#bar{b}lep#nu}',
        'b1pT':'pT_{b1}', 'b1Eta':'#eta_{b1}', 'b1E':'E_{b1}', 'b1CSV':'CSV_{b1}', 'b1M':'m_{b1}',
        'b2pT':'pT_{b2}', 'b2Eta':'#eta_{b2}', 'b2E':'E_{b2}', 'b2CSV':'CSV_{b2}', 'b2M':'m_{b2}',
        'lpT':'pT_{lep}', 'lEta':'#eta_{lep}', 'lE':'E_{lep}',
        'npT':'pT_{#nu}', 'nPhi':'#phi_{#nu}',
        'nbjets':'Number of b jets'}
    return dictionary

def getHistRange(var):
    histRange = []

    if 'dR' in var:
        histRange = [20, 0, 4]
    elif 'dEta' in var:
        histRange = [20, 0, 2.5]
    elif 'dPhi' in var:
        histRange = [20, 0, math.pi]
    elif 'pT' in var:
        histRange = [20, 0, 400]
    elif ('Eta' in var) and (not 'dEta' in var):
        histRange = [20, -2.5, 2.5]
    elif ('Phi' in var) and (not 'dPhi' in var):
        histRange = [20, -math.pi, math.pi]
    elif ('mT' in var) or ('M' in var):
        histRange = [20, 0, 400]
    elif ('E' in var) and (not 'Et' in var):
        histRange = [20, 0, 400]
    elif 'CSV' in var:
        histRange = [20, 0.75, 1]
    elif 'nbjets' in var:
        histRange = [10, 0, 10]
    else:
        histRange = [20, 0, 10]
        print("Variable does not exist")

    return histRange

def printProgress(iteration, total, prefix = '', suffix = '', decimals = 1, barLength = 100):
    nEvent = str(iteration) + '/' + str(total)
    formatStr = "{0:." + str(decimals) + "f}"
    percent = formatStr.format(100*(iteration/float(total)))
    filledLength = int(round(barLength * iteration/float(total)))
    bar = '#'*filledLength + '-'*(barLength-filledLength)
    sys.stdout.write('\r%s |%s| %s%s %s %s' % (prefix, bar, percent, '%', suffix, nEvent)),
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()

def mergeHDF(arrayDir,outName):
    print "Merge hdf files in", arrayDir
    selEvent = pd.DataFrame([])
    max_nevt_num = 0
    for array in os.listdir(arrayDir):
        df = pd.read_hdf(os.path.join(arrayDir, array))
        last = 0
        if df.size != 0: last = int(df.tail(1)['event'])+1
        df['event'] = df['event'] + max_nevt_num
        selEvent = pd.concat([selEvent,df], axis=0)
        max_nevt_num += last
    selEvent.reset_index(drop=True, inplace=True)
    selEvent.style.format('table')
    selEvent.to_hdf(arrayDir+'/../'+outName+'.h5',key='selEvent',mode='w')

def calculateMatchingRatio(trainingDir, ttbbDir):
    print "Calculate additional b jets matching ratio"

    print "Matched events/Matchable events = "
    print "Matched events/Total ttbb events = "
