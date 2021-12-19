import os, sys
import shutil
import subprocess

ntupleLoc = sys.argv[1]

listSplit = [item for item in os.listdir(ntupleLoc) if 'part' in item]
if len(listSplit) > 0:
    dictSplit = {}
    for item in listSplit:
        tmp = item.split('part')
        folderName = tmp[0][:-1]
        if not folderName in dictSplit:
            dictSplit[folderName] = []
        dictSplit[folderName].append(item)
    for key, value in dictSplit.items():
        if not os.path.exists(os.path.join(ntupleLoc, key)):
            os.mkdir(os.path.join(ntupleLoc, key))
        nfiles = 0 
        for item in value:
            print os.path.join(ntupleLoc, item), len(os.walk(os.path.join(ntupleLoc, item)).next()[2])
            for file in os.listdir(os.path.join(ntupleLoc, item)):
                digits = len(str(nfiles))
                fileNumber = (3-digits)*'0'+str(nfiles) 
                name = '_'.join(file.split('_')[0:-1])+'_'+fileNumber+'.root'
                shutil.copy(os.path.join(ntupleLoc,item,file),os.path.join(ntupleLoc,key,name))
                nfiles += 1
        print os.path.join(ntupleLoc, key), len(os.walk(os.path.join(ntupleLoc, key)).next()[2])
        if nfiles != len(os.walk(os.path.join(ntupleLoc, key)).next()[2]):
            print "WARNNING: THE FILES ARE MISSING"

#mergedLoc = ntupleLoc.replace('split','merged')
#if not os.path.exists(mergedLoc):
#    os.mkdir(mergedLoc)
#    for item in os.listdir(ntupleLoc):
#        if 'part' in item: continue
#        rootFiles = [os.path.join(ntupleLoc, item, file) for file in os.listdir(os.path.join(ntupleLoc, item))]
#        command = ['hadd', os.path.join(mergedLoc,item+'.root')]+rootFiles
#        subprocess.call(command)
