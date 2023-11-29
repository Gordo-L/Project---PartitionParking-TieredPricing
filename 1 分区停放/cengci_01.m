%层次聚类算法
clear all;
close all;
clc;
%输入簇z数k；
%输入所有点的对应的经纬度转换坐标，存放至一个excel表格中,总共有m个n维的向量。(事实上n=2)
k=input("");
all_data=xlsread('C:\Users\ASUS\OneDrive\桌面\location.xlsx','B2:C96');
[m,n]=size(all_data);
%对所有数据进行归类：自底向上，因此最初共有m类。
pattern_k=zeros(m,n+1);
for i=1:m
    pattern_k(i,[1,n])=all_data(i,:);
    pattern_k(i,n+1)=i;
end
%计算每两个簇类之间的平均距离/最大距离/最小距离，放入矩阵Distance中。
%这里采用平均距离.
for i=1:m
    for j=1:m
        Distance(i,j)=norm(all_data(i,:)-all_data(j,:));
    end
end

%自底向上进行聚类：
%设置当前聚类簇数q
q=m;
while q>k
    %找出距离最近的两个簇类
    index1=1;
    index2=2;
    for i=1:q
        for j=(i+1):q
            if(Distance(i,j)<Distance(index1,index2))
                index1=i;
                index2=j;
            end
        end
    end
    %把这两个簇类合并起来
    for i=1:m
        if(pattern_k(i,n+1)==index2)
            pattern_k(i,n+1)=index1;
        elseif(pattern_k(i,n+1)>index2)
            pattern_k(i,n+1)=pattern_k(i,n+1)-1;
        end
    end
    %对距离矩阵进行更新:首先删除第index2行，第index2列；再重新计算第index1类与q-1类的距离
    Distance(index2,:)=[];
    Distance(:,index2)=[];
    for i=1:(q-1)
        distance=0;%第index1类与第i类的所有元素总距离
        count1=0;%第index1类所有元素个数
        count2=0;%第i类所有元素个数
        for j=1:m
            if(pattern_k(j,n+1)==index1)
                count1=count1+1;
            end
        end
        for j=1:m
            if(pattern_k(j,n+1)==i)
                count2=count2+1;
            end
        end
        for j=1:m
            for l=1:m
                if(pattern_k(j,n+1)==index1&&pattern_k(l,n+1)==i)
                    distance=distance+norm(all_data(i,:)-all_data(j,:));
                end
            end
        end
        Distance(index1,i)=distance/(count1*count2);
        Distance(i,index1)=distance/(count1*count2);
    end
    q=q-1;
end

%再计算每个簇类的中心点
center=zeros(k,n);
for i=1:k
    sum=zeros(1,n);
    count=0;
    for j=1:m
        if(pattern_k(j,n+1)==i)
            sum=sum+all_data(j,:);
            count=count+1;
        end
        center(i,:)=sum/count;
    end
end

%最后利用图象显示聚类后的数据
plot(all_data(:,1),all_data(:,2),'*');
grid on;
figure;
hold on;
for i=1:m
    for j=1:k
        if pattern_k(i,n+1)==j
            plot(pattern_k(i,1),pattern_k(i,2),'r*');
            plot(center(j,1),center(j,2),'ko');
        end
    end
end
grid on; %画图的时候添加网线格    
    
%最后效果很差，为什么呢？聚类簇一点都不清楚，而且大多数的聚类中心彼此相距非常近，可能是距离计算错误了?
            
    
