# A simple open loop controller generating walking behavior 
# on a humanoid robot NAO.
# We use the asumption of 'parallel kinematics', i.e., feet are 
# kept parallel to the ground, to simplify kinematic calculations.
# The motion dynamics is generated with sin/cos based oscillations.

from Nao import Nao
import math

def left( x, y, z):
    
    # x, z 
    nao.jointMotorData["LKneePitch"] = ( z      )
    nao.jointMotorData["LHipPitch"] = (-z/2 + x)
    nao.jointMotorData["LAnklePitch"] = (-z/2 - x)
    
    # y
    nao.jointMotorData["LHipRoll"] = ( y)
    nao.jointMotorData["LAnkleRoll"] = (-y)
    
# move the right foot (keep the foot paralell to the ground)
def right( x, y, z):
    # x, z
    nao.jointMotorData["RKneePitch"] = ( z      )
    nao.jointMotorData["RHipPitch"] = (-z/2 + x)
    nao.jointMotorData["RAnklePitch"] = (-z/2 - x)
    
    # y
    nao.jointMotorData["RHipRoll"] = ( y)
    nao.jointMotorData["RAnkleRoll"] = (-y)

def run():
    ## 1. slow and steady
    f            = 4
    robot_height = 0.5
    shift_y      = 0.3
    step_height  = 0.4
    step_length  = 0.2
    arm_swing    = 2.0

    while nao.update():
    
        t = (nao.getTime() - t_0) * f

        # y
        yLeftRight = math.sin(t)*shift_y
        print(t)

        # z
        zLeft  = (math.sin(t)          + 1.0) / 2.0 * step_height + robot_height
        zRight = (math.sin(t + math.pi)+ 1.0) / 2.0 * step_height + robot_height

        # x
        # math.sin(t + math.pi/2) = math.cos(t)
        xLeft  = math.cos(t          )*step_length
        xRight = math.cos(t + math.pi)*step_length
        
        # apply
        left(  xLeft, yLeftRight, zLeft )
        right(xRight, yLeftRight, zRight)
        
        # move shoulders to stabilize steps
        nao.jointMotorData["RShoulderPitch"] =(arm_swing*xLeft  + math.pi/2  -0.1)
        nao.jointMotorData["LShoulderPitch"] =(arm_swing*xRight + math.pi/2  -0.1)

nao = Nao()

stiffness = 0.0

for name in nao.joint_names:
    nao.jointStiffnessData[name] = 0.0
    nao.jointMotorData[name] = nao.jointSensorData[name]

#set the stiffness of the joints
nao.jointStiffnessData['RShoulderPitch']= 0.5
nao.jointStiffnessData['LShoulderPitch']= 0.5

nao.jointStiffnessData['RHipYawPitch']= 0.5
nao.jointStiffnessData['LHipYawPitch']= 0.5
nao.jointStiffnessData['RHipRoll']= 0.5
nao.jointStiffnessData['LHipRoll']= 0.5
nao.jointStiffnessData['RHipPitch']= 0.5
nao.jointStiffnessData['LHipPitch']= 0.5
nao.jointStiffnessData['RKneePitch']= 0.5
nao.jointStiffnessData['LKneePitch']= 0.5
nao.jointStiffnessData['RAnklePitch']= 0.5
nao.jointStiffnessData['LAnklePitch']= 0.5
nao.jointStiffnessData['RAnkleRoll']= 0.5
nao.jointStiffnessData['LAnkleRoll']= 0.5

t_0 = nao.getTime()

run()