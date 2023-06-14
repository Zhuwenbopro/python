import numpy as np

def createDataSet():
    DATASET = [[0, 0, 0, 0, 'no'],
               [0, 0, 0, 1, 'no'],
               [0, 1, 0, 1, 'yes'],
               [0, 1, 1, 0, 'yes'],
               [0, 0, 0, 0, 'no'],
               [1, 0, 0, 0, 'no'],
               [1, 0, 0, 1, 'no'],
               [1, 1, 1, 1, 'yes'],
               [1, 0, 1, 2, 'yes'],
               [1, 0, 1, 2, 'yes'],
               [2, 0, 1, 2, 'yes'],
               [2, 0, 1, 1, 'yes'],
               [2, 1, 0, 1, 'yes'],
               [2, 1, 0, 2, 'yes'],
               [2, 0, 0, 0, 'no'],]
    LABELS = ['F1-AGE', 'F2-WORK', 'F3-HOUSE', 'F4-LOAN']
    # 在录入数据时记录每种属性有几种值
    LABELVALUES = [[0, 1, 2], [0, 1], [0, 1], [0, 1, 2]]
    return DATASET, LABELS, LABELVALUES

# dataset 数据集
# labels 当前还有哪些特性坐标可选（里面的特征会被掏空）
# featureLabels 已经选好的特性路径（里面会逐渐开始扩充特征）
def creatTree(dataIndexList, labelsIndexList, seqLabelIndexList):
    global DATASET, LABELS, LABELVALUES
    if len(dataIndexList) == 0:
        return "no data to predict"
    # 当前数据中所有结果
    resList = [DATASET[datasetIndex][-1] for datasetIndex in dataIndexList]
    # 分的很纯正，直接结束
    if resList.count(resList[0]) == len(resList):
        return resList[0]
    # 已经做到最后一个特征了
    if len(labelsIndexList) == 0:
        return majority(resList)
    # 选择分类效果最好的特性作为分类标准,并且直接删掉
    bestLabelIndex = chooseBestFeatureToSplit(dataIndexList, labelsIndexList)
    seqLabelIndexList.append(bestLabelIndex)
    treeNode = {LABELS[bestLabelIndex]:{}}
    # 准备分支
    for value in LABELVALUES[bestLabelIndex]:
        treeNode[LABELS[bestLabelIndex]][value] = \
            creatTree(splitDataSet(dataIndexList, bestLabelIndex, value), labelsIndexList.copy(), seqLabelIndexList)
    return treeNode

# 当前集合中最多的一个
def majority(classList):
    classCount = {}
    max = -1
    maxRes = ''
    for res in classList:
        if res not in classCount.keys():
            classCount[res] = 0
        classCount[res] += 1
        if classCount[res] > max:
            max = classCount[res]
            maxRes = res
    return  maxRes

# 更新 labelsIndexList
def chooseBestFeatureToSplit(dataAvailableList, availableLabels):
    global DATASET, LABELVALUES
    curEntropy = calcEntropy(dataAvailableList)
    bestGain = 0
    bestLabelIndex = -1
    bestLabelVal = -1
    for i, label in enumerate(availableLabels):
        newEntropy = 0
        for val in LABELVALUES[label]:
            availList = splitDataSet(dataAvailableList, label, val)
            p = len(availList)/float(len(dataAvailableList))
            newEntropy += p * calcEntropy(availList)
        gain = curEntropy - newEntropy
        if gain > bestGain:
            bestGain = gain
            bestLabelIndex = i
            bestLabelVal = label
    del availableLabels[bestLabelIndex]
    return bestLabelVal

def calcEntropy(dataList):
    global DATASET
    total = len(dataList)
    resNum = {}
    for i in dataList:
        res = DATASET[i][-1]
        if res not in resNum.keys(): resNum[res] = 0
        resNum[res] += 1
    entropy = 0
    for key in resNum:
        p = float(resNum[key])/total
        entropy -= p*np.log(p)
    return entropy


def splitDataSet(dataAvailableList, label, val):
    global DATASET
    resList = []
    for index in dataAvailableList:
        if(DATASET[index][label] == val):
            resList.append(index)
    return resList

DATASET, LABELS, LABELVALUES = createDataSet()
featureLabels = []
root = creatTree([a for a in range(len(DATASET))], [a for a in range(len(LABELS))], featureLabels)

for l in featureLabels:
    print(LABELS[l])
