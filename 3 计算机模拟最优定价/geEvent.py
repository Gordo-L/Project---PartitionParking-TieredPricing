import numpy as np

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
np.savetxt('Omegazjg.csv',Omega,fmt='%d',delimiter=',')

# 2.生成事件矩阵Event
F = [1/9,2/9,3/9,4/9,5/9,6/9,7/9,8/9,9/9]
#首先，给定到达不同p区（共9个）的累积分布向量F、U(0,1)上的随机数eta、起点start、终点end，产生服从该分布函数的随机数
def bisection_search(F, eta, start, end):    
    if (eta <= F[start]):
        return start
    n = end - start
    if (n <= 0):
        exit()
    k = (start + end) // 2
    if (eta > F[k]):
        if (eta <= F[k + 1]):
            return k + 1
        else:
            return bisection_search(F, eta, k + 1, end)
    else:
        return bisection_search(F, eta, start, k)
#其次，尝试生成叠加后的二维正态分布的随机点
#step1：生成一个服从U(0,1)的随机数，并带入bisection_search函数，从而得到随机点所属P区；
#step2：计算该P区的中心（（右下横坐标+左上横坐标）/2，（右下纵坐标+左上纵坐标）/2）、长度2sigma_x（右下横坐标-左上横坐标）、宽度2sigma_y（左上纵坐标-右下纵坐标），从而得到二维正态密度函数的参数；
#step3：获得随机点
def rand_PDF():
    #首先产生服从累积分布F的随机数
    U = np.random.rand()
    X = bisection_search(F, U, 0, numP) 
    #再产生对应P区的二维正态分布随机数
    mu_x = (P_rd[X,0]+P_lu[X,0])/2
    mu_y = (P_lu[X,1]+P_rd[X,1])/2
    sigma_x = (P_rd[X,0]-P_lu[X,0])/2
    sigma_y = (P_lu[X,1]-P_rd[X,1])/2
    mu = np.array([mu_x,mu_y])
    Sigma = np.array([[sigma_x**2, 0], [0,sigma_y**2]])  
    s = np.random.multivariate_normal(mu,Sigma)
    if 0<=s[0]<=width and 0<=s[1]<=length and Omega[int(s[0]),int(s[1])]!=-1:
        return s
    else:
        s = rand_PDF()
#若干个随机产生事件矩阵，其中m为行数，即用户个数；n为列数，即总时刻数。
def geEvent(m,n):
    #用shape为m*n*2的Event矩阵存储每个用户在每个时刻下发生的事件
    Event=np.zeros([m,n,2,2]) 
    for i in range(m):
        for j in range(n):
            for k in range(2):
                Event[i,j,k]=rand_PDF()
    return Event        

m = 1000
n = 100
Event = geEvent(m,n)
EventTest = Event[0,0,:,:]

#统一型与阶梯型的Event需要一致
#np.savetxt('Eventzjg.txt',Event,fmt='%d',delimiter=',') 由于是四维，所以保存不成功！
np.save(file="Eventzjg.npy", arr=Event)
ReEvent = np.load(file="Eventzjg.npy")
#成功！