import random
import numpy as np
import matplotlib.pyplot as plt
import math


def createDataSet():
    dataNum = 100
    X = np.array([[random.uniform(0, 1), random.uniform(0, 1)] for _ in range(dataNum)], dtype=float)
    Y = np.array([np.sign(x[0]-x[1]) for x in X], dtype=float)
    return X, Y

class SimpleSMO(object):

    def __init__(self, X, y, b, C, sigma, tolerance, MaxIter):
        self.n = len(X)
        self.X = X
        self.y = y
        self.b = b
        self.sigma = sigma
        self.C = C
        self.MaxIter = MaxIter
        self.tolerance = tolerance
        self.alpha = np.zeros((self.X.shape[0], 1))

        self.K = np.array([np.zeros(len(X)) for _ in X])
        for i in range(len(X)):
            for j in range(0, i + 1):
                self.K[i][j] = self.RBFKernel(X[i], X[j])
                self.K[j][i] = self.RBFKernel(X[i], X[j])

        self.E = np.array([-label for label in y], dtype=float)


    def RBFKernel(self, x, z):
        s = x - z
        e = np.sum(s * s)
        return math.exp(-e * (self.sigma))

    def linearKernel(self, i, j):
        x = self.X[i]
        z = self.X[j]
        return np.sum(x*z)

    def g(self, i):
        k = self.K[i]
        r2 = np.sum(self.alpha*self.y.reshape(-1, 1)*k.reshape(-1, 1)) + self.b

        return r2

    def SelectJ(self, i):
        #max = -1
        #j = -1
        #for ei, e in enumerate(self.E):
        #    if abs(self.E[i] - e) > max:
        #        max = abs(self.E[i] - e)
        #        j = ei
        #return j
        # 简化版SMO:随机选择第二个优化变量j，并使其不等于第一个i
        j = i
        while (j == i):
            j = int(random.uniform(0, self.X.shape[0]))
        return j


    def Optimization(self):
        iter = 0
        K = self.K
        E = self.E
        alpha = self.alpha
        y =self.y
        c = self.C

        # while循环用于判定变量是否继续更新，iter只有在alpha不再发生变化时才会更新
        while (iter < self.MaxIter):
            # alphaPairsChanged用于建立alpha是否改变的标志
            alphaPairsChanged = 0
            # 建立for循环，for循环作为外层循环，寻找一个变量
            for i in range(self.alpha.size):
                ##########################################
                # 选择第一个变量的要求：alpha_i是否严重违反kkt条件
                ##########################################
                if (y[i] * E[i] < -self.tolerance and alpha[i] < c) \
                        or (y[i] * E[i] > self.tolerance and alpha[i] > 0):
                    # 违反kkt条件成立，随机选择第二个优化变量aplha_j（简化版SMO算法）
                    j = self.SelectJ(i)

                    # 记录未更新前alpha_i,alpha_j的值（即alpha_old值）为计算new值作准备
                    alpha_i_old = alpha[i]
                    alpha_j_old = alpha[j]
                    # 根据alpha_i_old，alpha_j_old的值获得alpha_j_new的取值范围
                    if (y[i] != y[j]):
                        L = max(0, alpha_j_old - alpha_i_old)
                        H = min(c, c + alpha_j_old - alpha_i_old)
                    else:
                        L = max(0, alpha_j_old + alpha_i_old - c)
                        H = min(c, alpha_j_old + alpha_i_old)
                    if L == H:
                        print("L = H", E[i] - E[j])
                        continue
                    # 计算eta
                    eta = 2 * K[i][j] - K[i][i] - K[j][j]
                    if eta >= 0:
                        print("eta>=0")
                        continue
                    # 根据alpha_j_old,eta，y_i,E_i,E_j更新alpha_j_new_unc未剪辑的更新值
                    alpha_j_new_unc = alpha_j_old - y[j] * (E[i] - E[j]) / eta
                    # 获得剪辑后的更新值并保存
                    alpha_j_new = np.clip(alpha_j_new_unc, L, H)
                    delta_j = alpha_j_new - alpha_j_old
                    ########################################
                    # 选择第二个变量的要求：alpha_j具有足够大的变化
                    ########################################
                    if abs(delta_j) < 0.00001:
                        print("j not moving enough")
                        continue
                    # 根据alpha_j_old 和 更新后的self.alpha[j] 更新 self.alpha[i]
                    alpha_i_new = alpha_i_old - y[i] * y[j] * delta_j
                    delta_i = alpha_i_new - alpha_i_old

                    b_old = self.b
                    # 更新常数项b_i_new
                    b_i_new = self.b - E[i] - y[i] * K[i][i] * delta_i - y[j] * K[j][i] * delta_j
                    # 更新常数项b_j_new
                    b_j_new = self.b - E[j] - y[i] * K[i][j] * delta_i - y[j] * K[j][j] * delta_j

                    if (alpha_i_new > 0 and alpha_i_new < c):
                        self.b = b_i_new
                    elif (alpha_j_new > 0 and alpha_j_new < c):
                        self.b = b_j_new
                    else:
                        self.b = (b_i_new + b_j_new) / 2

                    self.alpha[j] = alpha_j_new
                    self.alpha[i] = alpha_i_new

                    for ei, e in enumerate(E):
                        self.E[ei] = e + self.b - b_old + y[i]*delta_i*K[i][ei] + y[j]*delta_j*K[j][ei]

                    # 若程序无中断，alpha必然发生改变，所以标志也要变化
                    alphaPairsChanged += 1
                    print("External loop: %d; Internal loop i :%d; alphaPairsChanged :%d" % (iter, i, alphaPairsChanged))
            # 只有alpha不再改变时（此时意味着很有可能是最优解），迭代次数iter更新从而验证是否为最优解
            if (alphaPairsChanged == 0):
                iter += 1
            # alpha改变时，迭代次数iter置0
            else:
                iter = 0
            print("Iteration number : %d" % iter)

        return self

    def test(self):
        total = len(self.X)
        correct = 0
        for i, x in enumerate(self.X):
            yi = self.y[i]
            pred = -1
            if self.g(i) > 0:
                pred = 1
            if pred == yi:
                correct += 1
        return float(correct / total)



list = []
for i in range(10):
    X, y = createDataSet()
    list.append(SimpleSMO(X, y, 0, 1, 1, 0.000001, 60).Optimization().test())

print(list)


