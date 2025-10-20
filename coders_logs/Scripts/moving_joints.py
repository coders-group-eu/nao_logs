import math
from Nao import Nao

nao = Nao()

stiffness = 0.0

for name in nao.joint_names:
    nao.jointStiffnessData[name] = 0.0

t_0 = nao.getTime()

i = 0

while nao.update():
    nao.jointStiffnessData[nao.joint_names[i]] = 0.5
    t = nao.getTime() - t_0
    yaw = nao.jointSensorData[nao.joint_names[i]]
    print("{:.3}: {}".format(t,yaw))
    nao.jointMotorData[nao.joint_names[i]] = math.sin(t)

    if t >= 5.00:
        t_0 = t
        i += 1

    if i == 5: 
        break




#   for name in nao.joint_names:
#    nao.jointMotorData[name] = nao.jointSensorData[name]
#    nao.jointStiffnessData[name] = stiffness



