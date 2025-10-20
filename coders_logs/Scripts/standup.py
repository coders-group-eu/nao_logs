from Nao import Nao
import math
import time

nao = Nao()

dict = {}


stiffness = 0.0

for name in nao.joint_names:
        nao.jointStiffnessData[name] = 0.0
        print('stiffness')

nao.jointStiffnessData["HeadYaw"] = 0.5

t_0 = nao.getTime()

while nao.update():

        t = nao.getTime() - t_0
        yaw = nao.jointSensorData["HeadYaw"]
        print("{:.3}: {}".format(t,yaw))
        if t > 1:
                break

# Beginning of walking movement
        
for name in nao.joint_names:
        dict[name] = nao.jointSensorData[name]

for name in nao.joint_names:
        nao.jointStiffnessData[name] = 0.6

movement_adjustment = 0.1

while nao.update():
        finished = True
        print('update')
        for name in dict.keys():
                print(name, abs(dict[name]))
                if abs(dict[name]) < movement_adjustment:
                        dict[name] = 0
                        nao.jointMotorData[name] = 0
                else:
                        if dict[name] < 0:
                                print(dict[name])
                                dict[name] = dict[name] + movement_adjustment
                        else:
                                dict[name] = dict[name] - movement_adjustment

                        nao.jointMotorData[name] = dict[name]

                        finished = False
        time.sleep(0.3)
        if finished:

                break

