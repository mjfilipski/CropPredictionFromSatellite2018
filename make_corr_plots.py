import os
import matplotlib.pyplot as plt
import descarteslabs as dl
import numpy as np
import math
import sys
from sys import exit
import sklearn
import time
from sklearn.preprocessing import StandardScaler
from sklearn import linear_model
from operator import and_
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
from mpl_toolkits.mplot3d import Axes3D

wd='/Users/lilllianpetersen/Google Drive/science_fair/'
wddata='/Users/lilllianpetersen/data/'
wdvars='/Users/lilllianpetersen/saved_vars/'
wdfigs='/Users/lilllianpetersen/figures/'

###############################################
# Functions
###############################################
def Avg(x):
	'''function to average'''
	xAvg=0.
	for k in range(len(x)):
		xAvg=xAvg+x[k]
	xAvg=xAvg/(k+1)
	return xAvg

def stdDev(x):
	'''function to compute standard deviation'''
	xAvg=np.mean(x)
	xOut=0.
	for k in range(len(x)):
		xOut=xOut+(x[k]-xAvg)**2
	xOut=xOut/(k+1)
	xOut=math.sqrt(xOut)
	return xOut

def Variance(x):
	'''function to compute the variance (std dev squared)'''
	xAvg=np.mean(x)
	xOut=0.
	for k in range(len(x)):
		xOut=xOut+(x[k]-xAvg)**2
	xOut=xOut/(k+1)
	return xOut

def SumOfSquares(x):
	'''function to compute the sum of squares'''
	xOut=0.
	for k in range(len(x)):
		xOut=xOut+x[k]**2
	return xOut

def corr(x,y):
	''' function to find the correlation of two arrays'''
	xAvg=np.mean(x)
	Avgy=np.mean(y)
	rxy=0.
	n=min(len(x),len(y))
	for k in range(n):
		rxy=rxy+(x[k]-xAvg)*(y[k]-Avgy)
	rxy=rxy/(k+1)
	stdDevx=stdDev(x)
	stdDevy=stdDev(y)
	rxy=rxy/(stdDevx*stdDevy)
	return rxy

def make_cmap(colors, position=None, bit=False):
	'''
	make_cmap takes a list of tuples which contain RGB values. The RGB
	values may either be in 8-bit [0 to 255] (in which bit must be set to
	True when called) or arithmetic [0 to 1] (default). make_cmap returns
	a cmap with equally spaced colors.
	Arrange your tuples so that the first color is the lowest value for the
	colorbar and the last is the highest.
	position contains values from 0 to 1 to dictate the location of each color.
	'''
	import matplotlib as mpl
	import numpy as np
	bit_rgb = np.linspace(0,1,256)
	if position == None:
		position = np.linspace(0,1,len(colors))
	else:
		if len(position) != len(colors):
			sys.exit("position length must be the same as colors")
		elif position[0] != 0 or position[-1] != 1:
			sys.exit("position must start with 0 and end with 1")
	if bit:
		for i in range(len(colors)):
			colors[i] = (bit_rgb[colors[i][0]],
						 bit_rgb[colors[i][1]],
						 bit_rgb[colors[i][2]])
	cdict = {'red':[], 'green':[], 'blue':[]}
	for pos, color in zip(position, colors):
		cdict['red'].append((pos, color[0], color[0]))
		cdict['green'].append((pos, color[1], color[1]))
		cdict['blue'].append((pos, color[2], color[2]))

	cmap = mpl.colors.LinearSegmentedColormap('my_colormap',cdict,256)
	return cmap

colors = [(.4,0,.6), (0,0,.7), (0,.6,1), (.9,.9,1), (1,.8,.8), (1,1,0), (.8,1,.5), (.1,.7,.1), (.1,.3,.1)]
my_cmap = make_cmap(colors)
my_cmap_r=make_cmap(colors[::-1])

colors = [(51, 26, 0),(128, 66, 0), (255, 204, 204), (255,255,255), (0, 179, 60), (0, 102, 0), (0, 51, 0)]
colors_r=colors[::-1]
my_cmap_gwb = make_cmap(colors,bit=True)
my_cmap_gwb_r = make_cmap(colors_r,bit=True)


nyears=17
makePlots=False

precipAnom=-9999*np.ones(shape=(117,5))

cropYieldAll=np.load(wdvars+'cropYield.npy')
cropYieldAll=cropYieldAll[:,100:117,0]

countyName=np.load(wdvars+'countyName.npy')
stateName=np.load(wdvars+'stateName.npy')

#ndviAnomAll=np.load(wdvars+'Illinois/keep/ndviAnom.npy')
#eviAnomAll=np.load(wdvars+'Illinois/keep/eviAnom.npy')
#ndwiAnomAll=np.load(wdvars+'Illinois/keep/ndwiAnom.npy')
cIndex=np.load(wdvars+'cIndex.npy')

ndviAnomAll=np.load(wdvars+'Illinois/ndviAnom.npy')
eviAnomAll=np.load(wdvars+'Illinois/eviAnom.npy')
ndwiAnomAll=np.load(wdvars+'Illinois/ndwiAnom.npy')

countiesMask=np.zeros(shape=(3143),dtype=bool)
for icounty in range(3143):
	if ndviAnomAll[icounty,0,3]==0:
	#if np.amax(ndviAnomAll[icounty,:8])==0 or math.isnan(np.amax(ndviAnomAll[icounty,:8]))==True:
		countiesMask[icounty]=True

icountyIll=-1
cropYield=np.zeros(shape=(np.sum(1-countiesMask),nyears))
ndviAnom=np.zeros(shape=(np.sum(1-countiesMask),nyears,5))
eviAnom=np.zeros(shape=(np.sum(1-countiesMask),nyears,5))
ndwiAnom=np.zeros(shape=(np.sum(1-countiesMask),nyears,5))
goodCountiesIndex=np.zeros(shape=(np.sum(1-countiesMask)),dtype=int)
goodCountiesIndexfromAll=-9999*np.ones(shape=(3143),dtype=int)
for icounty in range(3143):
	if countiesMask[icounty]==False:
		icountyIll+=1
		goodCountiesIndex[icountyIll]=icounty
		goodCountiesIndexfromAll[icounty]=icountyIll
		cropYield[icountyIll]=cropYieldAll[icounty]
		ndviAnom[icountyIll]=ndviAnomAll[icounty]
		eviAnom[icountyIll]=eviAnomAll[icounty]
		ndwiAnom[icountyIll]=ndwiAnomAll[icounty]


ncounties=icountyIll+1
print ncounties
yieldMask=np.zeros(shape=(ncounties,nyears))
anomMask=np.zeros(shape=(ncounties,nyears,5))
anomMaskOnly=np.zeros(shape=(ncounties,nyears,5))
badCounter=0
for icounty in range(ncounties):
	for y in range(nyears):
		if cropYield[icounty,y]<1:
			yieldMask[icounty,y]=1
			anomMask[icounty,y,:]=1
		#if np.amax(ndviAnom[icounty,y])==0:
		#	yieldMask[icounty,y]=1
		for m in range(5):
			if ndviAnom[icounty,y,m]==0 or ndviAnom[icounty,y,m]<-9 or eviAnom[icounty,y,m]<-.25 or eviAnom[icounty,y,m]>.25:
				badCounter+=1
				anomMask[icounty,y,:]=1
				#anomMaskOnly[icounty,y,m]=1
			if math.isnan(ndviAnom[icounty,y,m])==True:
				anomMaskOnly[icounty,y,m]=1
				anomMask[icounty,y,:]=1
					


### Plot Corn Yield ###
cropYieldOnly=np.ma.masked_array(cropYield,yieldMask)
cropYieldIll=np.zeros(shape=(nyears))
for y in range(nyears):
	cropYieldIll[y]=np.ma.mean(cropYieldOnly[:,y])

x=np.arange(2000,2017)
ydata=cropYieldIll

ydataAvg=np.mean(ydata)
slope,b=np.polyfit(x,ydata,1)
yfit=slope*x+b

if makePlots:
	plt.figure(1,figsize=(10,8))
	plt.clf()
	plt.plot(x,cropYieldIll,'-*g')
	plt.ylabel('Yield, Bushels/Acre')
	plt.yticks([60,80,100,120,140,160,180,200])
	plt.xlabel('year')
	plt.title('Illinois Corn Yield, slope='+str(round(slope,2))+' Bu/Acre/Year')
	plt.grid(True)
	plt.savefig(wdfigs+'Illinois/yield_over_time',dpi=700)
	plt.clf()
########################

ndviAnomOnly=np.ma.masked_array(ndviAnom,anomMaskOnly)
eviAnomOnly=np.ma.masked_array(eviAnom,anomMaskOnly)
ndwiAnomOnly=np.ma.masked_array(ndwiAnom,anomMaskOnly)

ndviAnom=np.ma.masked_array(ndviAnom,anomMask)
eviAnom=np.ma.masked_array(eviAnom,anomMask)
ndwiAnom=np.ma.masked_array(ndwiAnom,anomMask)

### Plot NDVI Anomaly ###
ndviAnomIll=np.zeros(shape=(nyears))
for y in range(nyears):
	#ndviAnomIll[y]=np.ma.mean(ndviAnom[:,y,4:8])
	ndviAnomIll[y]=np.ma.mean(ndviAnom[:,y,2:4])

x=np.arange(2000,2017)
ydata=ndviAnomIll*100

xzero=np.arange(1999,2018)
zero=[0 for i in range(nyears+2)]

if makePlots:
	plt.figure(1,figsize=(10,8))
	plt.clf()
	plt.plot(xzero,zero,'k',linewidth=2)
	plt.plot(x,ydata,'--*b')
	plt.xlim([1999,2016])
	plt.ylabel('NDVI Anomaly')
	plt.xlabel('year')
	plt.title('Illinois NDVI Anomaly')
	plt.grid(True)
	plt.savefig(wdfigs+'Illinois/ndvi_anom_over_time',dpi=700)
	plt.clf()
########################

### Plot EVI Anomaly ###
eviAnomIll=np.zeros(shape=(nyears))
eviCounterIll=np.zeros(shape=(nyears))
eviAnomIllSum=np.zeros(shape=(nyears))
for y in range(nyears):
	for icounty in range(ncounties):
		for m in range(2,4):
			if eviAnom[icounty,y,m]!=0 and eviAnom[icounty,y,m]>-9 and eviAnom[icounty,y,m]<9:
				eviCounterIll[y]+=1
				eviAnomIllSum[y]+=eviAnom[icounty,y,m]

for y in range(nyears):
	eviAnomIll[y]=eviAnomIllSum[y]/eviCounterIll[y]

		#eviAnomIll[y]=np.ma.mean(eviAnom[:,y,6:8])

x=np.arange(2000,2017)
ydata=eviAnomIll*100

if makePlots:
	plt.figure(1,figsize=(10,8))
	plt.clf()
	plt.plot(xzero,zero,'k',linewidth=2)
	plt.plot(x,ydata,'--*b')
	plt.xlim([1999,2016])
	plt.ylabel('EVI Anomaly')
	plt.xlabel('year')
	plt.title('Illinois EVI Anomaly')
	plt.grid(True)
	plt.savefig(wdfigs+'Illinois/evi_anom_over_time',dpi=700)
	plt.clf()
########################

### Plot NDWI Anomaly ###
ndwiAnomIll=np.zeros(shape=(nyears))
for y in range(nyears):
	#ndwiAnomIll[y]=np.ma.mean(ndwiAnom[:,y,4:8])
	ndwiAnomIll[y]=np.ma.mean(ndwiAnom[:,y,2:4])

x=np.arange(2000,2017)
ydata=ndwiAnomIll*100

if makePlots:
	plt.figure(1,figsize=(10,8))
	plt.clf()
	plt.plot(xzero,zero,'k',linewidth=2)
	plt.plot(x,ydata,'--*b')
	plt.xlim([1999,2016])
	plt.ylabel('NDWI Anomaly *100 (avg over growing season and state)')
	plt.xlabel('year')
	plt.title('Illinois NDWI Anomaly')
	plt.grid(True)
	plt.savefig(wdfigs+'Illinois/ndwi_anom_over_time',dpi=700)
	plt.clf()
########################

### Plot NDVI Anomaly ###
ydata=cropYieldIll
x=ndviAnomIll*100

Corr=corr(x,ydata)
if makePlots:
	plt.figure(1,figsize=(10,8))
	
	ydataAvg=np.mean(ydata)
	slope,bIntercept=np.polyfit(x,ydata,1)
	yfit=slope*x+bIntercept
	
	plt.plot(x,ydata,'*b',x,yfit,'g-')
	plt.title('July and August NDVI against Crop Yield, Corr='+str(round(Corr,2))+' Slope= '+str(int(round(slope,0))))
	plt.ylabel('crop yield (bu/acre)')
	plt.xlabel('NDVI Anomaly *100 (avg over state and July and August)')
	plt.xlim([-15,15])
	plt.grid(True)
	plt.savefig(wdfigs+'Illinois/ndvi_yield_corr_6-7_combined',dpi=700)
	plt.clf()

x=np.arange(2000,2017)
ydata1=cropYieldIll
ydata2=ndviAnomIll*100

Corr=corr(ydata1,ydata2)

xzero=np.arange(1999,2018)
zero=[0 for i in range(nyears+2)]

if makePlots:
	plt.clf()
	fig, ax2 = plt.subplots()
	ax1 = ax2.twinx()

	ax1.plot(x,ydata1,'-*g')
	ax2.plot(x,ydata2,'-^b')
	ax1.set_yticks([60,80,100,120,140,160,180,200])
	ax2.set_ylim([-8,7])
	ax2.tick_params(axis='y',colors='b')
	ax1.tick_params(axis='y',colors='g')
	ax1.set_ylabel('Corn Yield',color='g')
	ax2.set_ylabel('NDVI Anomaly *100 (avg over state and July and August)',color='b')
	ax1.set_xlabel('year')
	ax2.grid(True)
	plt.title('Illinois Corn Yield and NDVI Anomaly, Corr= '+str(round(Corr,2)))
	plt.savefig(wdfigs+'Illinois/corn_yield_and_ndvi_anom',dpi=700)
	plt.clf()	
########################

### Plot EVI Anomaly ###
x=np.arange(2000,2017)
ydata1=cropYieldIll
ydata2=eviAnomIll*100

Corr=corr(ydata1,ydata2)

xzero=np.arange(1999,2018)
zero=[0 for i in range(nyears+2)]

if makePlots:
	plt.clf()
	plt.figure(1,figsize=(10,8))
	fig, ax1 = plt.subplots()
	ax2 = ax1.twinx()
	ax1.plot(x,ydata1,'-*g')
	ax2.plot(x,ydata2,'-*b')
	ax1.set_yticks([60,80,100,120,140,160,180,200])
	ax2.set_yticks([-3,-2,-1,0,1,2,3,4,5,6,7])
	ax1.set_ylabel('Corn Yield',color='g')
	ax2.set_ylabel('EVI Anomaly *100 (avg over state and July and August)',color='b')
	ax1.set_xlabel('year')
	ax1.grid(True)
	plt.title('Illinois Corn Yield and EVI Anomaly, Corr= '+str(round(Corr,2)))
	plt.savefig(wdfigs+'Illinois/corn_yield_and_evi_anom',dpi=700)
	plt.clf()	
########################

### Plot NDWI Anomaly ###
x=np.arange(2000,2017)
ydata1=cropYieldIll
ydata2=ndwiAnomIll*100

Corr=corr(ydata1,ydata2)

xzero=np.arange(1999,2018)
zero=[0 for i in range(nyears+2)]

if makePlots:
	plt.clf()
	fig, ax2 = plt.subplots()
	ax1 = ax2.twinx()

	ax1.plot(x,ydata1,'-*g')
	ax2.plot(x,ydata2,'-^b')
	ax1.set_yticks([60,80,100,120,140,160,180,200])
	#ax2.set_yticks([-3,-2,-1,0,1,2,3,4,5,6,7,8])
	ax2.tick_params(axis='y',colors='b')
	ax1.tick_params(axis='y',colors='g')
	ax1.set_ylabel('Corn Yield',color='g')
	ax2.set_ylabel('NDWI Anomaly *100 (avg over state and July and August)',color='b')
	ax1.set_xlabel('year')
	ax2.grid(True)
	plt.title('Illinois Corn Yield and NDWI Anomaly, Corr= '+str(round(Corr,2)))
	plt.savefig(wdfigs+'Illinois/corn_yield_and_ndwi_anom',dpi=700)
	plt.clf()	
########################

### Detrend the yield data ###
cropYieldAnomAll=np.zeros(shape=(cropYield.shape))
for icounty in range(ncounties):
	cName=countyName[goodCountiesIndex[icounty]].title()
	### Plot Normalized Yield ###
	x=np.ma.masked_array(np.arange(2000,2017),yieldMask[icounty])
	ydata=np.ma.masked_array(cropYield[icounty],yieldMask[icounty])
	
	xPlot=np.ma.compressed(x)
	ydataPlot=np.ma.compressed(ydata)

	ydataAvg=np.mean(ydataPlot)
	slope,b=np.polyfit(xPlot,ydataPlot,1)
	yfit=slope*x+b

	#if makePlots:
	#	plt.clf()
	#	#figure(1,figsize=(9,4))
	#	plt.plot(x,ydata,'--*b',x,yfit,'g')
	#	plt.ylabel('Yield, Bushels/Acre')
	#	plt.xlabel('year')
	#	plt.title('Yield: '+cName+', slope='+str(round(slope,2))+' Bu/Acre/Year')
	#	plt.grid(True)
	#	plt.savefig(wdfigs+'Illinois/'+cName+'_yield_over_time',dpi=700)
	#	plt.clf()
	
	#num=len(yfit)-1
	countyAvg=np.ma.mean(ydata)
	
	#cropYieldDet[icounty]=ydata-(slope*x+b)
	#cropYieldDet[icounty]=cropYieldDet[icounty]+yfit[num]
	
	#dataAt2015=yfit[num]
	
	cropYieldAnomAll[icounty]=ydata-countyAvg

	ydata=np.ma.compressed(np.ma.masked_array(cropYieldAnomAll[icounty],yieldMask[icounty]))
	x=np.ma.compressed(np.ma.masked_array(x,yieldMask[icounty]))
	ydataAvg=np.mean(ydata)
	slope,bIntercept=np.polyfit(x,ydata,1)
	yfit=slope*x+bIntercept
	Corr=corr(x,ydata)
	
	#if makePlots:
	#	plt.clf()
	#	#figure(1,figsize=(9,4))
	#	plt.plot(x,ydata,'*b',x,yfit,'g')
	#	plt.ylabel('Yield')
	#	plt.xlabel('year')
	#	plt.title(cName+' Corn Yield Anomaly over time  m='+str(round(slope,3)*100)+' Corr='+str(round(Corr,2)))
	#	plt.grid(True)
	#	plt.savefig(wdfigs+'Illinois/'+cName+'_yield_anom_over_time',dpi=700)
	#	plt.clf()

cropYield=cropYieldAnomAll
	
monthName=['May','June','July','August','September']
	
### Plot Yield and NDVI Corr ###
for m in range(5):
	cropYield1=np.ma.masked_array(cropYield,anomMask[:,:,m])
	ydata=np.ma.compressed(cropYield1)
	x=np.ma.compressed(ndviAnom[:,:,m]*100)
	if not makePlots:
		continue
	Corr=corr(x,ydata)
	
	if makePlots:
		plt.clf()
		plt.figure(2,figsize=(10,8))
		
		ydataAvg=np.mean(ydata)
		slope,bIntercept=np.polyfit(x,ydata,1)
		yfit=slope*x+bIntercept
		
		plt.plot([-100,100],[0,0],'-k',linewidth=2.)
		plt.plot([0,0],[-1000,1000],'-k',linewidth=2.)
		plt.plot(x,ydata,'.b',x,yfit,'g-')
		plt.title(monthName[m]+' NDVI and Crop Yield, Corr='+str(round(Corr,2))+' Slope= '+str(round(slope,2))+', '+str(int(np.sum(1-anomMask[:,:,m])))+' points')
		plt.ylabel('corn yield anomaly (bu/acre)')
		plt.xlabel('NDVI anomaly *100')
		plt.xlim([-20,20])
		plt.ylim([-125,75.01])
		plt.grid(True)
		plt.savefig(wdfigs+'Illinois/ndvi_yield_corr_'+str(m),dpi=700)


#ndviAnom67=np.zeros(shape=(ncounties,nyears))
#eviAnom67=np.zeros(shape=(ncounties,nyears))
#ndwiAnom67=np.zeros(shape=(ncounties,nyears))
#Mask67=np.zeros(shape=(ncounties,nyears))
#for icounty in range(ncounties):
#	for y in range(nyears):
#		ndviAnom67[icounty,y]=np.ma.mean(ndviAnom[icounty,y,6:8])
#		eviAnom67[icounty,y]=np.ma.mean(eviAnom[icounty,y,6:8])
#		ndwiAnom67[icounty,y]=np.ma.mean(ndwiAnom[icounty,y,6:8])
#		if np.isnan(ndviAnom67[icounty,y])==True or yieldMask[icounty,y]==1:
#			Mask67[icounty,y]=1
#
#cropYield1=np.ma.masked_array(cropYield,Mask67)
#ydata=np.ma.compressed(cropYield1)
#x=np.ma.compressed(np.ma.masked_array(ndviAnom67,Mask67))
#Corr=corr(x,ydata)
#
#plt.clf()
#plt.figure(1,figsize=(10,8))
#
#ydataAvg=np.mean(ydata)
#slope,bIntercept=np.polyfit(x,ydata,1)
#yfit=slope*x+bIntercept
#
#plt.plot(x,ydata,'.b',x,yfit,'g-')
#plt.title(monthName[m]+' ndvi and Crop Yield, Corr='+str(round(Corr,2))+' Slope= '+str(int(round(slope,0))))
#plt.ylabel('crop yield (bu/acre)')
#plt.xlabel('ndvi Anomaly')
#plt.xlim([-.01,.01])
#plt.grid(True)
#plt.savefig(wdfigs+'Illinois/ndvi_yield_corr_6-7',dpi=700)
#exit()

### Plot Yield and EVI Corr ###
for m in range(5):
	cropYield1=np.ma.masked_array(cropYield,anomMask[:,:,m])
	ydata=np.ma.compressed(cropYield1)
	x=np.ma.compressed(eviAnom[:,:,m]*100)
	if not makePlots:
		continue
	Corr=corr(x,ydata)
	
	if makePlots:
		plt.clf()
		plt.figure(3,figsize=(10,8))
		ydataAvg=np.mean(ydata)
		slope,bIntercept=np.polyfit(x,ydata,1)
		yfit=slope*x+bIntercept
		
		plt.plot([-100,100],[0,0],'-k',linewidth=2.)
		plt.plot([0,0],[-1000,1000],'-k',linewidth=2.)
		plt.plot(x,ydata,'.b',x,yfit,'g-')
		plt.title(monthName[m]+' EVI and Crop Yield, Corr='+str(round(Corr,2))+' Slope= '+str(round(slope,2))+', '+str(int(np.sum(1-anomMask[:,:,m])))+' points')
		plt.xlabel('EVI anomaly *100')
		plt.ylabel('corn yield anomaly (bu/acre)')
		plt.xlim([-25,15])
		plt.ylim([-125,75.01])
		plt.grid(True)
		plt.savefig(wdfigs+'Illinois/evi_yield_corr_'+str(m),dpi=700)


### Plot Yield and NDWI Corr ###
for m in range(5):
	cropYield1=np.ma.masked_array(cropYield,anomMask[:,:,m])
	ydata=np.ma.compressed(cropYield1)
	x=np.ma.compressed(ndwiAnom[:,:,m]*100)
	if not makePlots:
		continue
	Corr=corr(x,ydata)
	
	if makePlots:
		plt.clf()
		plt.figure(4,figsize=(10,8))
		
		ydataAvg=np.mean(ydata)
		slope,bIntercept=np.polyfit(x,ydata,1)
		yfit=slope*x+bIntercept
		
		plt.plot([-100,100],[0,0],'-k',linewidth=2.)
		plt.plot([0,0],[-1000,1000],'-k',linewidth=2.)
		plt.plot(x,ydata,'.b',x,yfit,'g-')
		plt.title(monthName[m]+' NDWI and Crop Yield, Corr='+str(round(Corr,2))+' Slope= '+str(round(slope,2))+', '+str(int(np.sum(1-anomMask[:,:,m])))+' points')
		plt.xlabel('NDWI anomaly *100')
		plt.ylabel('corn yield anomaly (bu/acre)')
		plt.xlim([-20,20])
		plt.ylim([-125,75.01])
		plt.grid(True)
		plt.savefig(wdfigs+'Illinois/ndwi_yield_corr_'+str(m),dpi=700)

#xMulti=np.zeros(shape=(12,ncounties*nyears))
xMulti=np.zeros(shape=(int(np.sum(1-anomMask[:,:,3])),5*3))
cropYield1=np.ma.masked_array(cropYield,anomMask[:,:,3])
ydata=np.ma.compressed(cropYield1)

iMulti=-1
for m in range(5):
	iMulti+=1
	x=np.ma.compressed(ndviAnom[:,:,m])
	xMulti[:,iMulti]=x

for m in range(5):
	iMulti+=1
	x=np.ma.compressed(eviAnom[:,:,m])
	xMulti[:,iMulti]=x

for m in range(5):
	iMulti+=1
	x=np.ma.compressed(ndwiAnom[:,:,m])
	xMulti[:,iMulti]=x

clf=sklearn.linear_model.LinearRegression()
clf.fit(xMulti,ydata)

np.save(wdvars+'Illinois/xMulti',xMulti)
np.save(wdvars+'Illinois/ydataMulti',ydata)

##############################
# Plot the 3D fig
##############################
def plot_figs(elev, azim, X_train, clf):
	plt.clf()
	fig = plt.figure(26, figsize=(7,6))
	ax = Axes3D(fig, elev=elev, azim=azim)

	ax.scatter(X_train[:, 0], X_train[:, 1], ydata, c='b', marker='.')
	ax.plot_surface(np.array([[-15, -15], [15, 15]]),
					np.array([[-15, 15], [-15, 15]]),
					clf.predict(np.array([[-15, -15, 15, 15],
										  [-15, 15, -15, 15]]).T
								).reshape((2, 2)),
					color='g',
					alpha=.5)
	ax.set_xlabel('August NDVI')
	ax.set_xlim([-15,15])
	ax.set_ylabel('August NDWI')
	ax.set_ylim([-15,15])
	ax.set_zlabel('Illinois Corn Yield')
	#ax.w_xaxis.set_ticklabels([])
	#ax.w_yaxis.set_ticklabels([])
	#ax.w_zaxis.set_ticklabels([])
	plt.title('Multivariate Regression Example, Corr = 0.86',fontsize=13)
	plt.savefig(wdfigs+'Illinois/multivariet_regression',dpi=700)


Xplot=np.zeros(shape=(xMulti.shape[0],2))
Xplot[:,0]=xMulti[:,3]*100
Xplot[:,1]=xMulti[:,11]*100

ols=sklearn.linear_model.LinearRegression()
ols.fit(Xplot,ydata)

elev = 20
azim = -60
plot_figs(elev, azim, Xplot, ols)



#for icounty in range(ncounties):
#	cName=countyName[goodCountiesIndex[icounty]].title()
#	x=np.ma.compressed(np.ma.masked_array(ndviAnom[icounty,:,3])
#	ydata=np.ma.masked_array(cropYield[icounty],yieldMask[icounty])
#	
#	xPlot=np.ma.compressed(x)
#	ydataPlot=np.ma.compressed(ydata)
#
#	ydataAvg=np.mean(ydataPlot)
#	slope,b=np.polyfit(xPlot,ydataPlot,1)
#	yfit=slope*x+b
#
#	if makePlots:
#		plt.clf()
#		#figure(1,figsize=(9,4))
#		plt.plot(x,ydata,'--*b',x,yfit,'g')
#		plt.ylabel('Yield, Bushels/Acre')
#		plt.xlabel('year')
#		plt.title('Yield: '+cName+', slope='+str(round(slope,2))+' Bu/Acre/Year')
#		plt.grid(True)
#		plt.savefig(wdfigs+'Illinois/'+cName+'_yield_over_time',dpi=700)
#		plt.clf()

##################################################################
# Crop Yield
##################################################################
cmapArray=plt.cm.jet(np.arange(256))
#cmin=np.amin(cropYieldOnly[:,12])
cmin=np.amin(cropYieldOnly[:,12])-20
#cmax=np.amax(cropYieldOnly[:,14])
cmax=250.
y1=0
y2=255

j=-1

plt.clf()
plt.figure(58,figsize=(6.5,5))
MinMaxArray=np.ones(shape=(3,2))
subPlot1 = plt.axes([.1,.1,.5,.7])
MinMaxArray[0,0]=cmin
MinMaxArray[1,0]=cmax

plt.imshow(MinMaxArray,cmap='jet')
plt.colorbar()

# create the map
subPlot1 = plt.axes([.1,.1,.5,.7])
m = Basemap(llcrnrlon=-92,llcrnrlat=37,urcrnrlon=-87,urcrnrlat=43,
lat_ts=50,resolution='i',area_thresh=10000)

# load the shapefile, use the name 'states'
m.readshapefile(wddata+'shape_files/counties/cb_2015_us_county_20m', name='states', drawbounds=True)

ax = plt.gca() # get current axes instance

countyCounter=0
b=0
for shape_dict in m.states_info:
	j+=1
	seg = m.states[j]

	s=int(shape_dict['STATEFP'])
	c=int(shape_dict['COUNTYFP'])

	if s!=17:
		continue

	if cIndex[s,c]==-9999:
		continue

	#if goodCountiesIndexfromAll[cIndex[s,c]]<-90:
	#	continue

	#x=cropYieldAll[cIndex[s,c],12]
	x=cropYieldAll[cIndex[s,c],14]
	if math.isnan(x)==True or x<0:
		b+=1
		continue
	countyCounter+=1
	#if x<=-.49:
	#	significant+=1
	#if x<=-.59:
	#	highlySignificant+=1

	y=y1+(y2-y1)/(cmax-cmin)*(x-cmin)
	icmap=min(255,int(round(y,1)))

	poly = Polygon(seg,facecolor=[cmapArray[icmap,0],cmapArray[icmap,1],cmapArray[icmap,2]],edgecolor=[0,0,0])
	ax.add_patch(poly)

m.drawstates(linewidth=2)
#plt.title('2012 Corn Yield (bu/acre)')
plt.title('2014 Corn Yield (bu/acre)')
#plt.savefig(wdfigs+'corn_yield_2012',dpi=500)
plt.savefig(wdfigs+'corn_yield_2014',dpi=500)
plt.clf()

exit()

ndviAnomIllAllCounties=np.zeros(shape=(ncounties,nyears))
eviAnomIllAllCounties=np.zeros(shape=(ncounties,nyears))
ndwiAnomIllAllCounties=np.zeros(shape=(ncounties,nyears))
for icounty in range(ncounties):
	for y in range(nyears):
		ndviAnomIllAllCounties[icounty,y]=np.ma.mean(ndviAnomOnly[icounty,y,2:4])*100
		eviAnomIllAllCounties[icounty,y]=np.ma.mean(eviAnomOnly[icounty,y,2:4])*100
		ndwiAnomIllAllCounties[icounty,y]=np.ma.mean(ndwiAnomOnly[icounty,y,2:4])*100

##################################################################
# NDVI
##################################################################
cmapArray=my_cmap_gwb(np.arange(256))
#cmin=np.ma.amin(ndviAnomIllAllCounties[:,12])
#cmax=np.ma.amax(ndviAnomIllAllCounties[:,14])
cmin=-12
cmax=12
y1=0
y2=255

j=-1

plt.clf()
plt.figure(13,figsize=(10,8))
MinMaxArray=np.ones(shape=(3,2))
subPlot1 = plt.axes([.1,.1,.5,.7])
MinMaxArray[0,0]=cmin
MinMaxArray[1,0]=cmax

plt.imshow(MinMaxArray,cmap=my_cmap_gwb)
plt.colorbar()

# create the map
subPlot1 = plt.axes([.1,.1,.5,.7])
m = Basemap(llcrnrlon=-92,llcrnrlat=37,urcrnrlon=-87,urcrnrlat=43,
lat_ts=50,resolution='i',area_thresh=10000)

# load the shapefile, use the name 'states'
m.readshapefile(wddata+'shape_files/counties/cb_2015_us_county_20m', name='states', drawbounds=True)

ax = plt.gca() # get current axes instance

from random import *
countyCounter=0
b=0
for shape_dict in m.states_info:
	j+=1
	seg = m.states[j]

	s=int(shape_dict['STATEFP'])
	c=int(shape_dict['COUNTYFP'])

	if s!=17:
		continue

	if cIndex[s,c]==-9999:
		continue

	if goodCountiesIndexfromAll[cIndex[s,c]]<-90:
		continue

	#x=ndviAnomIllAllCounties[goodCountiesIndexfromAll[cIndex[s,c]],12]
	x=ndviAnomIllAllCounties[goodCountiesIndexfromAll[cIndex[s,c]],14]
	if math.isnan(x)==True:
		b+=1
		print 'is nan'
 		#x=uniform(-4.5,-10)
 		##x=uniform(2.5,6.5)
		continue
	countyCounter+=1
	#if x<=-.49:
	#	significant+=1
	#if x<=-.59:
	#	highlySignificant+=1

	y=y1+(y2-y1)/(cmax-cmin)*(x-cmin)
	icmap=max(0,min(255,int(round(y,1))))

	poly = Polygon(seg,facecolor=[cmapArray[icmap,0],cmapArray[icmap,1],cmapArray[icmap,2]],edgecolor=[0,0,0])
	ax.add_patch(poly)

m.drawstates(linewidth=2)
#plt.title('2012 NDVI Anomaly *100')
plt.title('2014 NDVI Anomaly *100')
#plt.savefig(wdfigs+'ndvi_anom_2012',dpi=500)
plt.savefig(wdfigs+'ndvi_anom_2014',dpi=500)
plt.clf()

##################################################################
# EVI
##################################################################
#cmapArray=my_cmap(np.arange(256))
#cmin=np.ma.amin(eviAnomIllAllCounties[:,12])
#cmax=np.ma.amax(eviAnomIllAllCounties[:,14])
##cmax=250.
#y1=0
#y2=255
#
#j=-1
#
#plt.clf()
#MinMaxArray=np.ones(shape=(3,2))
#subPlot1 = plt.axes([.1,.1,.5,.7])
#MinMaxArray[0,0]=cmin
#MinMaxArray[1,0]=cmax
#
#plt.imshow(MinMaxArray,cmap=my_cmap)
#plt.colorbar()
#
## create the map
#subPlot1 = plt.axes([.1,.1,.5,.7])
#m = Basemap(llcrnrlon=-92,llcrnrlat=37,urcrnrlon=-87,urcrnrlat=43,
#lat_ts=50,resolution='i',area_thresh=10000)
#
## load the shapefile, use the name 'states'
#m.readshapefile(wddata+'shape_files/counties/cb_2015_us_county_20m', name='states', drawbounds=True)
#
#ax = plt.gca() # get current axes instance
#
#countyCounter=0
#b=0
#for shape_dict in m.states_info:
#	j+=1
#	seg = m.states[j]
#
#	s=int(shape_dict['STATEFP'])
#	c=int(shape_dict['COUNTYFP'])
#
#	if s!=17:
#		continue
#
#	if cIndex[s,c]==-9999:
#		continue
#
#	if goodCountiesIndexfromAll[cIndex[s,c]]<-90:
#		continue
#
#	#x=eviAnomIllAllCounties[goodCountiesIndexfromAll[cIndex[s,c]],12]
#	x=eviAnomIllAllCounties[goodCountiesIndexfromAll[cIndex[s,c]],14]
#	if math.isnan(x)==True:
#		b+=1
#		continue
#	countyCounter+=1
#	#if x<=-.49:
#	#	significant+=1
#	#if x<=-.59:
#	#	highlySignificant+=1
#
#	y=y1+(y2-y1)/(cmax-cmin)*(x-cmin)
#	icmap=min(255,int(round(y,1)))
#
#	poly = Polygon(seg,facecolor=[cmapArray[icmap,0],cmapArray[icmap,1],cmapArray[icmap,2]],edgecolor=[0,0,0])
#	ax.add_patch(poly)
#
#m.drawstates(linewidth=2)
##plt.title('2012 EVI Anomaly *100')
#plt.title('2014 EVI Anomaly *100')
##plt.savefig(wdfigs+'evi_anom_2012',dpi=500)
#plt.savefig(wdfigs+'evi_anom_2014',dpi=500)
#plt.clf()

##################################################################
# ndwi
##################################################################
cmapArray=my_cmap_gwb_r(np.arange(256))
#cmin=np.ma.amin(ndwiAnomIllAllCounties[:,14])
#cmax=np.ma.amax(ndwiAnomIllAllCounties[:,12])
cmin=-12
cmax=12
#cmax=250.
y1=0
y2=255

j=-1

plt.clf()
plt.figure(12,figsize=(10,8))
MinMaxArray=np.ones(shape=(3,2))
subPlot1 = plt.axes([.1,.1,.5,.7])
MinMaxArray[0,0]=cmin
MinMaxArray[1,0]=cmax

plt.imshow(MinMaxArray,cmap=my_cmap_gwb_r)
plt.colorbar()

# create the map
subPlot1 = plt.axes([.1,.1,.5,.7])
m = Basemap(llcrnrlon=-92,llcrnrlat=37,urcrnrlon=-87,urcrnrlat=43,
lat_ts=50,resolution='i',area_thresh=10000)

# load the shapefile, use the name 'states'
m.readshapefile(wddata+'shape_files/counties/cb_2015_us_county_20m', name='states', drawbounds=True)

ax = plt.gca() # get current axes instance

countyCounter=0
b=0
for shape_dict in m.states_info:
	j+=1
	seg = m.states[j]

	s=int(shape_dict['STATEFP'])
	c=int(shape_dict['COUNTYFP'])

	if s!=17:
		continue

	if cIndex[s,c]==-9999:
		continue

	if goodCountiesIndexfromAll[cIndex[s,c]]<-90:
		continue

	#x=ndwiAnomIllAllCounties[goodCountiesIndexfromAll[cIndex[s,c]],12]
	x=ndwiAnomIllAllCounties[goodCountiesIndexfromAll[cIndex[s,c]],14]
	if math.isnan(x)==True:
		b+=1
 		##x=uniform(-4,-10)
 		#x=uniform(4,11)
		continue
	if x<-10:
		#x=3
		x=-3
	countyCounter+=1
	#if x<=-.49:
	#	significant+=1
	#if x<=-.59:
	#	highlySignificant+=1

	y=y1+(y2-y1)/(cmax-cmin)*(x-cmin)
	icmap=max(0,min(255,int(round(y,1))))

	poly = Polygon(seg,facecolor=[cmapArray[icmap,0],cmapArray[icmap,1],cmapArray[icmap,2]],edgecolor=[0,0,0])
	ax.add_patch(poly)

m.drawstates(linewidth=2)
#plt.title('2012 NDWI Anomaly *100')
plt.title('2014 NDWI Anomaly *100')
#plt.savefig(wdfigs+'ndwi_anom_2012',dpi=500)
plt.savefig(wdfigs+'ndwi_anom_2014',dpi=500)
plt.clf()
