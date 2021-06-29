import cv2
import numpy as np
import copy


cap = cv2.VideoCapture('bad.mp4')
success,image = cap.read()
np.set_printoptions(threshold=np.inf)

count = 0
width = 480
height = 360

# length = 1000
length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))-1

base = np.ones([length,height,width], dtype = int)
pointsCount = 400
polygonCount = 6
indCount = int(polygonCount/2)
xyt_pre = np.zeros((length,polygonCount, 2,pointsCount),dtype=int)
maxpoints = np.zeros(polygonCount, dtype = int)
scalefactorX = 12
scalefactorY = 12
chunkheight = int(height/scalefactorY)
chunkwidth = int(width/scalefactorX)
out = open("test.txt", "w")
f = open("new.txt", "w")
print(length)

while success:
	success,image = cap.read()
	image = cv2.resize(image, (width, height), fx = 0, fy = 0,interpolation = cv2.INTER_CUBIC)
	save = copy.deepcopy(image)
	save[save<=123] = 0
	save[save>123]=255
	save = cv2.cvtColor(save, cv2.COLOR_BGR2GRAY);
	blank = np.copy(image)
	blank[:,:,:] = 0
	contours, hierarchy = cv2.findContours(save, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

	contours.sort(key=len, reverse = True)
	# print(count)
	contourCount = 0
	wCount = 0
	bCount = 0
	while ((wCount+bCount)<polygonCount):
		colorWhite = True
		if(contourCount>=len(contours)):
			break
		else:
			contours[contourCount] = contours[contourCount].reshape((contours[contourCount].shape[0]*contours[contourCount].shape[1]), contours[contourCount].shape[2])
			contours[contourCount] = contours[contourCount].transpose()

			# edgecoordsmatrix = np.array([np.abs(edgecoords[0]-(height-1)), edgecoords[1]])
			minX = contours[contourCount][0][0]
			minY = contours[contourCount][1][0]
			# print("____________________________________________________________")
			# print("full list:---------------------")
			# print(contours[contourCount])
			# print("-------------------------------")
			# print("list where x is the same --------------")
			# print(contours[contourCount][1][contours[contourCount][0]==minX])
			# print("-------------------------------------")
			# print(f"({minX},{minY})")

			# print("___________________________________________________________")
			if(minX<width-1):
				minX+=1
			if(minY<height-1):
				minY+=1
			if(save[minY][minX] == 0):
				colorWhite = False
			edgecoordsmatrix = np.array([np.abs(contours[contourCount][1][0::20]-(height-1)), contours[contourCount][0][0::20]])
			
			contourCount +=1

			if(colorWhite):
				if(wCount < indCount):
					if(edgecoordsmatrix.shape[1]>maxpoints[wCount]):
						maxpoints[wCount]=edgecoordsmatrix.shape[1]
					xyt_pre[count,wCount,:, 0:edgecoordsmatrix.shape[1]] = edgecoordsmatrix
					wCount +=1
				else:
					continue
			else:
				if(bCount <indCount):
					if(edgecoordsmatrix.shape[1]>maxpoints[bCount+indCount]):
						maxpoints[indCount+bCount]=edgecoordsmatrix.shape[1]
					xyt_pre[count,indCount+bCount,:, 0:edgecoordsmatrix.shape[1]] = edgecoordsmatrix
					bCount +=1
				else:
					continue


	if(count == length-1):
		break


	count+=1
	# if cv2.waitKey(25) & 0xFF == ord('q'):
	# 	break

cap.release()
cv2.destroyAllWindows()
points = []
lastpoint = np.zeros((2,),dtype=int)
for t in range(xyt_pre.shape[0]):
	for c in range(polygonCount):
		for x in range(maxpoints[c]):
			if(np.any(xyt_pre[t,c,:,x]>0)):
				lastpoint = xyt_pre[t,c,:,x]
			else:
				xyt_pre[t,c,:,x] = lastpoint

for pc in range(polygonCount):
	for x in range(maxpoints[pc]):
		xString = str(pc)+("{0:03}".format(x))
		out.write(r"a_{"+xString+"} = "+str(xyt_pre[:,pc,0,x].tolist())+"\n")
		out.write(r"b_{"+xString+"} = "+str(xyt_pre[:,pc,1,x].tolist())+"\n")
		points.append(r"(b_{"+xString+"}[F],a_{"+xString+"}[F])")
	
	f.write(f"polygon({','.join(points)})\n")
	points = []

out.close()
f.close()


