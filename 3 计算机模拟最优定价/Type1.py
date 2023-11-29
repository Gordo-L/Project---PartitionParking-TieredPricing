import numpy as np
import numpy.linalg as la

# 1.生成阶梯型区域Omega矩阵
#首先，将P、M、G区的左上坐标、右下坐标分别记录在两个数组中，其中numP、numM、numG区分别为P、M、G区的个数；
#再进行坐标轴变换（左上变成了左下坐标轴）
#最后得到左下和右上坐标
P_lu = np.array([[14,10],[29,10],[7,40],[7,50],[8,73],[26,97],[48,26],[53,62],[53,85]])
P_rd = np.array([[18,20],[33,20],[19,46],[19,58],[16,79],[32,103],[54,32],[61,68],[61,93]])
P_lu[:,1] = 110 - P_lu[:,1]
P_rd[:,1] = 110 - P_rd[:,1]
P_ld = np.zeros([9,2],int)
P_ld[:,0] = P_lu[:,0]
P_ld[:,1] = P_rd[:,1]
P_ru = np.zeros([9,2],int)
P_ru[:,0] = P_rd[:,0]
P_ru[:,1] = P_lu[:,1]


M_lu = np.array([[3,5],[3,28],[14,96],[44,23],[46,46]])
M_rd = np.array([[41,23],[23,94],[44,106],[68,41],[70,100]])
M_lu[:,1] = 110 - M_lu[:,1]
M_rd[:,1] = 110 - M_rd[:,1]
M_ld = np.zeros([5,2],int)
M_ld[:,0] = M_lu[:,0]
M_ld[:,1] = M_rd[:,1]
M_ru = np.zeros([5,2],int)
M_ru[:,0] = M_rd[:,0]
M_ru[:,1] = M_lu[:,1]

G_lu = np.array([[24,24],[33,54],[25,78]])
G_rd = np.array([[42,52],[45,76],[43,92]])
G_lu[:,1] = 110 - G_lu[:,1]
G_rd[:,1] = 110 - G_rd[:,1]
G_ld = np.zeros([3,2],int)
G_ld[:,0] = G_lu[:,0]
G_ld[:,1] = G_rd[:,1]
G_ru = np.zeros([3,2],int)
G_ru[:,0] = G_rd[:,0]
G_ru[:,1] = G_lu[:,1]

#其次，对omega区域进行赋值，如下所示
width = 74
length = 110
numP = 9
numM = 5
numG = 3
Omega = np.zeros([width,length]) 
for gn in range(numG):
    for gx in range(G_ld[gn,0],G_ru[gn,0]):
        for gy in range(G_ld[gn,1],G_ru[gn,1]):
            Omega[gx,gy] = -1;
for mn in range(numM):
    for mx in range(M_ld[mn,0],M_ru[mn,0]):
        for my in range(M_ld[mn,1],M_ru[mn,1]):
            Omega[mx,my] = 1; 
for pn in range(numP):
    for px in range(P_ld[pn,0],P_ru[pn,0]):
        for py in range(P_ld[pn,1],P_ru[pn,1]):
            Omega[px,py] = 2;

# 2.生成事件矩阵Event
m = 1000
n = 100
Event = np.load(file="Eventzjg.npy")  #统一型与阶梯型的Event需要是一致的！！！
#此命令读取文件，把内容赋给Event

# 3.计算最近停车点及其距离
# 计算距离终点最近的P/M区的点的坐标及距离
## 输入：
## flagValue = 2：最近的P区；1：最近的M区
## endPoint = array([x坐标,y坐标])：随机事件的终点
## 
def NearestPark(flagValue, endPoint):
    # 初始化距离矩阵Dist（即空间的每个格点到随机事件终点的距离形成一个与Omega大小相同的矩阵）
    Dist = np.zeros([74,110])
    for i in range(74):
        for j in range(110):
            Dist[i,j]=la.norm(endPoint-np.array([i,j]))
    minDist=np.min(Dist[Omega==flagValue])
    nearestPoint=np.where(Dist == np.min(Dist[Omega==2]))
    FinalnearestPoint=np.array([nearestPoint[0][0],nearestPoint[1][0]])
    return minDist,FinalnearestPoint

# 4.方格矩阵Cell的操作
# 初始化方格矩阵
## 作用：每次搬车后，车子回到初始状态——P区(2)1辆车，M区(1)和F区(0)都是0辆车
Cell = np.zeros([width,length])  #注意这里的Cell是全局变量，不要归为局部变量！！！
def initialCell():
    Cell[Omega==2] = 1
    Cell[Omega==1] = 0
    Cell[Omega==0] = 0
    Cell[Omega==-1] = 0
initialCell()

# 判定是否有车
## 作用：判定方格矩阵中某方格周围共9个方格内是否有车，没车就直接判定为不骑车，有车再骑
## 输入：某个点
## 输出：周围方格是否有车以及新的起点
## 查阅可得，紫金港占地面积5740000平方米，我们的矩阵是74*110，相当于缩小了700倍，依据这个比例确定搜索附近9个方格
def judgeCell(point):
    px = int(point[0])
    py = int(point[1])
    if Cell[px,py]!=0:
        return [px,py],1   #起点不变，且该方格内有车
    else:
        mini=max(0,px-1)
        maxi=min(width,px+2)
        minj=max(0,py-1)
        maxj=min(length,py+2)
        for i in range(mini,maxi): 
            for j in range(minj,maxj):
                if Cell[i,j]!=0:
                    return [i,j],1   #起点改变，周围方格内有车
                else:
                    continue
        return [px,py],0   #起点不变，该方格和周围方格都无车。判定为不骑车！

#更新该方格的车
# 作用：每一件事件发生后都需要重新更新方格矩阵
# 输入：起点和终点
# 无输出，仅对全局变量Cell做更改
def updateCell(startpoint,endpoint):
    sx = int(startpoint[0])
    sy = int(startpoint[1])
    Cell[sx,sy] = Cell[sx,sy] - 1
    ex = int(endpoint[0])
    ey = int(endpoint[1])
    Cell[ex,ey] = Cell[ex,ey] + 1
    
# 5. 模拟过程以及费用计算
##给定各个参数
#定义a<Cp<C<Cm<Cf<Df<Dm<D<Dp<b
#定义limitp和limitm
a=4
C=20
Cp=12
Cm=40
Cf=60
Df=800
Dm=800
Dp=800
D=800
b=800
limitp=2
limitm=1.5
park=np.zeros([m,n,2])
distance=np.zeros([m,n])

##搬运费函数
updatetime = 2
p1 = 2
p2 = 1.5
p3 = 1
cost = np.zeros(int(n/updatetime))  #初始化搬运费用，共有n/updatetime次
countFMP=np.zeros([int(n/updatetime),3])
def countcost(t):  #其中t代表当前时刻，即t = i + 1
    if t%updatetime == 0:
        countF = np.sum(Cell[Omega==0])
        countM = np.sum(Cell[Omega==1])
        countP = np.sum(Cell[Omega==2])  #由于P区中部分车无需搬运，这部分要如何计算？
        cost[t//updatetime - 1] = p1*countF + p2*countM + p3*countP  #搬运费是不同地区停车数量的加权和
        countFMP[t//updatetime - 1,:]=np.array([countF,countM,countP])
        initialCell()    #搬运车辆，即初始化

##计算搬运费
##计算距离
for i in range(m):
    for j in range(n):
        distance[i,j] = np.linalg.norm(Event[i,j,1]-Event[i,j,0])#事件矩阵起点和终点坐标
##判定是否骑车及其起点和终点
for j in range(n):
    for i in range(m):
        if i%50 == 0:
            np.savetxt("T1_Cell"+str(i//50)+".csv",Cell,fmt='%d',delimiter=',')
            #文件名，数组变量，数据类型，分隔符;此命令储存文件
        if a<distance[i,j] and distance[i,j]<b:#（排除极端情况）#if 这里有车才能进行:
            vector0 = Event[i,j,0]
            vector1,flag = judgeCell(vector0)
            vector2 = Event[i,j,1]
            if flag == 1:
                if Omega[int(vector2[0]),int(vector2[1])] == 2:  #（终点在p区内）
                    distance[i,j] = np.linalg.norm(vector2 - vector1)
                    park[i,j] = vector2 #（停车点距离相应的就等于终点的位置，录入到矩阵中）
                    if Cp>=distance[i,j] or distance[i,j]>=Dp:
                        distance[i,j] = 0
                    else:
                        updateCell(vector1,vector2)
                elif Omega[int(vector2[0]),int(vector2[1])] == 1:#（终点在m区）
                    Kp,vector3 = NearestPark(2, vector2)#此处用xll的方法找到最近的p区的点，就是找到最近的赋值为2的点,那个点记为vector3。计算此时终点到停车点的距离Kp
                    if Kp >= limitp:
                        distance[i, j] = np.linalg.norm(vector2 - vector1)
                        park[i,j] = vector2 #（停车点距离相应的就等于终点的位置，录入到矩阵中）
                        if Cm>=distance[i,j] or distance[i,j]>=Dm:
                            distance[i, j] = 0
                        else:
                            updateCell(vector1,vector2)
                    elif Kp < limitp:
                        distance[i, j] = np.linalg.norm(vector3-vector1)# 就是那个p点减去起点的距离。
                        park[i,j] = vector3
                        if Cp>=distance[i,j] or distance[i,j]>=Dp:
                            distance[i, j]=0
                        else:
                            updateCell(vector1,vector3)
                elif Omega[int(vector2[0]),int(vector2[1])] == 0:  # （终点在f区）
                    Kp,vector3 = NearestPark(2, vector2)#此处用xll的方法找到最近的p区的点，就是找到最近的赋值为2的点,那个点记为vector3。计算此时终点到停车点的距离Kp
                    Km,vector4 = NearestPark(1, vector2)#此处用xll的方法找到最近的m区的点，就是找到最近的赋值为1的点,那个点记为vector4。计算此时终点到停车点的距离Kp
                    if Kp<limitp:
                        distance[i,j] = np.linalg.norm(vector3-vector1)  # 就np.linalg.norm(vector2-vector1)是那个p点减去起点的距离。
                        park[i,j] = vector3
                        if Cp>=distance[i,j] or distance[i,j]>=Dp:
                            distance[i, j] = 0
                        else:
                            updateCell(vector1,vector3)
                    elif Kp>=limitp and Km<limitm:
                        distance[i,j] = np.linalg.norm(vector4-vector1) # 就是那个m点减去起点的距离。
                        park[i,j] = vector4
                        if Cm>=distance[i,j] or distance[i,j]>=Dm:
                            distance[i, j] = 0
                        else:
                            updateCell(vector1,vector4)
                    else:#就是此时Kp比p大，而且Km比m大
                        distance[i,j] = np.linalg.norm(vector2-vector1)# 就是终点减去起点的距离。
                        park[i,j] = vector2
                        if Cf>=distance[i,j] or distance[i,j]>=Df:
                            distance[i, j] = 0
                        else:
                            updateCell(vector1,vector2)
            else:
                distance[i,j] = 0
        else:
            distance[i,j] = 0
    countcost(j+1)  #计算是否需要重新搬运，对cell矩阵进行初始化
    