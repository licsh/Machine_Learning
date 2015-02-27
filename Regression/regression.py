from numpy import *
import matplotlib.pyplot as plt
from time import sleep
import json
import urllib2

def loadDataSet(fileName):
	numFeat = len(open(fileName).readline().split('\t')) - 1
	dataMat = []
	labelMat = []
	fr = open(fileName)
	for line in fr.readlines():
		lineArr = []
		curLine = line.strip().split('\t')
		for i in range(numFeat):
			lineArr.append(float(curLine[i]))
		dataMat.append(lineArr)
		labelMat.append(float(curLine[-1]))
	return dataMat, labelMat
	
def standRegress(xArr, yArr):
	xMat = mat(xArr)
	yMat = mat(yArr).T
	xTx = xMat.T * xMat
	if linalg.det(xTx) == 0.0:
		print 'This matrix is singular, cannot do inverse'
		return
	ws = xTx.I * (xMat.T * yMat)
	return ws
	
def testStandRegress():
	xArr, yArr = loadDataSet('ex0.txt')
	ws = standRegress(xArr, yArr)
	print ws
	xMat = mat(xArr)
	yMat = mat(yArr)
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.scatter(
		xMat[:,1].flatten().A[0], yMat.T[:, 0].flatten().A[0]
	)
	xCopy = xMat.copy()
	xCopy.sort(0)
	yHat = xCopy * ws
	ax.plot(xCopy[:,1], yHat)
	plt.show()
	
def lwlr(testPoint, xArr, yArr, k = 1.0):
	xMat = mat(xArr)
	yMat = mat(yArr).T
	m = shape(xMat)[0]
	weights = mat(eye(m))
	for j in range(m):
		# print 'testPoint =',testPoint
		# print 'xArr[j,:] =',xMat[j,:]
		diffMat = testPoint - xMat[j,:]
		weights[j, j] = exp(diffMat*diffMat.T/(-2.0*k**2))
	xTx = xMat.T * (weights * xMat)
	if linalg.det(xTx) == 0.0:
		print 'This matrix is singular, cannot do inverse'
		return
	ws = xTx.I * (xMat.T * weights * yMat)
	return testPoint * ws
	
def lwlrTest(testArr, xArr, yArr, k = 1.0):
	m = shape(testArr)[0]
	yHat = zeros(m)
	for i in range(m):
		yHat[i] = lwlr(testArr[i], xArr, yArr, k)
	return yHat
	
def testLwlr():
	xArr, yArr = loadDataSet('ex0.txt')
	yHat = lwlrTest(xArr, xArr, yArr, 0.003)
	xMat = mat(xArr)
	yMat = mat(yArr)
	srtInd = xMat[:, 1].argsort(0)
	xSort = xMat[srtInd][:,0,:]
	# print 'xSort = ', xSort
	# print 'xMat[srtInd] =', xMat[srtInd]
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.plot(xSort[:,1], yHat[srtInd])
	ax.scatter(
		xMat[:,1].flatten().A[0], yMat.T[:, 0].flatten().A[0], s=2, c='red'
	)
	plt.show()
	
def resError(yArr, yHatArr):
	return ((yArr - yHatArr)**2).sum()
	
def uciTest():
	abX, abY = loadDataSet('abalone.txt')
	trainX = abX[0:99]
	trainY = abY[0:99]
	yHat01 = lwlrTest(trainX, trainX, trainY, 0.1)
	yHat1  = lwlrTest(trainX, trainX, trainY, 1)
	yHat10 = lwlrTest(trainX, trainX, trainY, 10)
	e01 = resError(trainY, yHat01.T)
	e1  = resError(trainY, yHat1.T)
	e10 = resError(trainY, yHat10.T)
	print 'e01 =', e01
	print 'e1 =', e1
	print 'e10 =', e10
	testX = abX[100:199]
	testY = abY[100:199]
	yHat01 = lwlrTest(testX, trainX, trainY, 0.1)
	yHat1  = lwlrTest(testX, trainX, trainY, 1)
	yHat10 = lwlrTest(testX, trainX, trainY, 10)
	e01 = resError(testY, yHat01.T)
	e1  = resError(testY, yHat1.T)
	e10 = resError(testY, yHat10.T)
	print 'e01 =', e01
	print 'e1 =', e1
	print 'e10 =', e10
	
def ridgeRegress(xMat, yMat, lam=0.2):
	xTx = xMat.T * xMat
	denom = xTx  + eye(shape(xMat)[1])*lam
	if linalg.det(denom) == 0.0:
		print 'This matrix is singular, cannot do inverse'
		return
	ws = denom.T * (xMat.T * yMat)
	return ws
	
def ridgeTest(xArr, yArr):
	xMat = mat(xArr)
	yMat = mat(yArr).T
	ymean = mean(yMat, 0)
	yMat = yMat - ymean
	xMeans = mean(xMat, 0)
	xVar = var(xMat, 0)
	xMat = (xMat - xMeans) / xVar
	numTestPts = 30
	wMat = zeros((numTestPts, shape(xMat)[1]))
	for i in range(numTestPts):
		ws = ridgeRegress(xMat, yMat, exp(i-10))
		wMat[i,:] = ws.T
	return wMat
	
def testRidge():
	xArr, yArr = loadDataSet('abalone.txt')
	ridgeWeights = ridgeTest(xArr, yArr)
	print ridgeWeights
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.plot(ridgeWeights)
	plt.show()
	
def regularize(xMat):#regularize by columns
    inMat = xMat.copy()
    inMeans = mean(inMat,0)   #calc mean then subtract it off
    inVar = var(inMat,0)      #calc variance of Xi then divide by it
    inMat = (inMat - inMeans)/inVar
    return inMat
	
def stageWise(xArr, yArr, eps=0.01, numIt=100):
	xMat = mat(xArr)
	yMat = mat(yArr).T
	yMean = mean(yMat, 0)
	yMat = yMat - yMean
	xMat = regularize(xMat)
	m, n = shape(xMat)
	returnMat = zeros((numIt, n))
	ws = zeros((n, 1))
	wsTest = ws.copy()
	wsMax = ws.copy()
	for i in range(numIt):
		# print ws.T
		lowestError = inf
		for j in range(n):
			for sign in [-1, 1]:
				wsTest = ws.copy()
				wsTest[j] += eps*sign
				yTest = xMat*wsTest
				resE = resError(yMat.A, yTest.A)
				if resE < lowestError:
					lowestError = resE
					wsMax = wsTest
		ws = wsMax.copy()
		returnMat[i, :] = ws.T
	return returnMat
	
def testStageWise():
	xArr, yArr = loadDataSet('abalone.txt')
	weights = stageWise(xArr, yArr, 0.001, 5000)
	print weights
	xMat = mat(xArr)
	yMat = mat(yArr).T
	xMat = regularize(xMat)
	yMean = mean(yMat, 0)
	yMat = yMat - yMean
	print standRegress(xMat, yMat.T)
	
def searchForSet(retX, retY, setNum, yr, numPce, origPrc):
	sleep(10)
	myAPIstr = 'get from code.google.com'
	searchURL = 'https:/www.googleapis.com/shopping/search/v1/public/products?\
				key=%s&country=US&q=lego+%d&alt=json' % (myAPIstr, setNum)
	pg = urllib2.urlopen(searchURL)
	retDict = json.load(pg.read())
	for i in range(len(retDict['items'])):
		try:
			currItem = retDict['items']
			if currItem['product']['condition']=='new':
				newFlag = 1
			else:
				newFlag = 0
			listOfInv = currItem['product']['inventories']
			for item in listOfInv:
				sellingPrice = item['price']
				print '%d\t%d\t%d\t%f\t%f' % (yr, numPce, newFlag, origPrc, sellingPrice)
				retX.append([yr, numPce, newFlag, origPrc])
				retY.append(sellingPrice)
		except:
			print 'problem with item %d' % (i)
			
def setDataCollect(retX, retY):
	searchForSet(retX, retY, 8288, 2006, 800, 49.99)
	searchForSet(retX, retY, 10030, 2002, 3096, 269.99)
	searchForSet(retX, retY, 10179, 2007, 5195, 499.99)
	searchForSet(retX, retY, 10181, 2007, 3428, 199.99)
	searchForSet(retX, retY, 10189, 2008, 5922, 299.99)
	searchForSet(retX, retY, 10196, 2009, 3263, 249.99)
	
def crossValidation(xArr, yArr, numVal=10):
	m = len(yArr)
	indexList = range(m)
	errorMat = zeros((numVal, 30))
	for i in range(numVal):
		trainX = []
		trainY = []
		testX = []
		testY = []
		random.shuffle(indexList)
		for j in range(m):
			if j<m*0.9:
				trainX.append(xArr[indexList[j]])
				trainY.append(yArr[indexList[j]])
			else:
				testX.append(xArr[indexList[j]])
				testY.append(yArr[indexList[j]])
		wMat = ridgeTest(trainX, trainY)
		for k in range(30):
			matTestX = mat(testX)
			matTrainX = mat(trainX)
			meanTrainX = mean(trainX, 0)
			varTrainX = var(matTrainX, 0)
			matTestX = (matTestX - meanTrainX) / varTrainX
			yEst = matTestX * mat(wMat[k,:]).T + mean(trainY)
			errorMat[i, k] = rssError(yEst.T.A, array(testY))
	meanErrors = mean(errorMat, 0)
	minMean = float(min(meanErrors))
	bestWeights = wMat[nonzero(meanErrors==minMean)]
	xMat = mat(xArr)
	yMat = mat(yArr).T
	meanX = mean(xMat, 0)
	varX = var(xMat, 0)
	unReg = bestWeights / varX
	print "the best model from Ridge Regression is:\n",unReg
	print "with constant term: ",-1*sum(multiply(meanX,unReg)) + mean(yMat)

def testLego():
	lgX = []
	lgY = []
	setDataCollect(lgX, lgY)
	m,n = shape(lgX)
	print shape(lgX)
	lgX1 = mat(ones(m, n+1))
	lgX1[:,1:n+1] = mat(lgX)
	ws = standRegress(lgX1, lgy)
	print 'ws =', ws
	crossValidation(lgX, lgY, 10)
	ridgeTest(lgX, lgY)

if __name__ == '__main__':
	# testStandRegress()
	# xArr, yArr = loadDataSet('ex0.txt')
	# ws = standRegress(xArr, yArr)
	# xMat = mat(xArr)
	# yMat = mat(yArr)
	# yHat = xMat * ws
	# print corrcoef(yHat.T, yMat)
	# testLwlr()
	# uciTest()
	# testRidge()
	# testStageWise()
	testLego()