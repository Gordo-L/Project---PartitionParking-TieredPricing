%利用肘部法则来确定kmeans算法的聚类簇数
sum=zeros(1,15);
N=zeros(1,15);
%输入所有点的对应的经纬度转换坐标，存放至一个excel表格中,总共有m个n维的向量。(事实上n=2)
all_data=xlsread('C:\Users\ASUS\OneDrive\桌面\location.xlsx','B2:C96');
[m,n]=size(all_data);
for countk=2:15
    %输入簇z数k；
    k=countk;
    %初始化簇类中心,选取k个初始聚类中心为前k个向量
    center=all_data([1:k],:);
    %对所有数据进行归类,共有k类
    pattern_k=zeros(m,n+1);
    pattern_k(:,[1,n])=all_data(:,:);
    while true
        distance=zeros(1,k);
        count=zeros(1,k);
        new_center=zeros(k,n);
        %对m个数据进行归类
        for i=1:m
            for j=1:k
                distance(1,j)=norm(all_data(i,:)-center(j,:)) %计算第i个数据与第j个簇类中心的距离；
            end
            [~,index]=min(distance);
            pattern_k(i,n+1)=index;
        end
        %更新簇类中心
        valid_k=0;
        for j=1:k
            for i=1:m
                if (pattern_k(i,n+1)==j)
                    new_center(j,:)=new_center(j,:)+pattern_k(i,[1:n]);
                    count(j)=count(j)+1;
                end
            end
            new_center(j,:)=new_center(j,:)/count(j);
            %判断第j类的收敛情况是否足够
            if (norm(new_center(j,:)-center(j,:))<0.000001)
                valid_k=valid_k+1;
            end
        end
        if (valid_k==k)
            break;
        else
            center=new_center;
        end
    end
    %new_center即为我们要寻找的k个单车停放点
    
    for j=1:k
        for i=1:m
            if pattern_k(i,n+1)==j
                sum(countk)=sum(countk)+norm(all_data(i,:)-new_center(j,:));
            end
        end
        N(1,countk)=countk;
    end
end
plot(N,sum);
    