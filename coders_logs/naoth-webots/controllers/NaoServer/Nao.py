from controller import Robot, Supervisor
from controller import TouchSensor, Camera, Motor, PositionSensor

import math


# simple mathematical function in 3D
# to safe dependency to numpy ;)
def length3(x):
  return math.sqrt(x[0]*x[0] + x[1]*x[1] + x[2]*x[2])

def normalize(v):
    """Return normalized 3D vector v."""
    det = length3(v)
    return [v[0] / det, v[1] / det, v[2] / det]
  
def subtract(a, b):
  return [a[0]-b[0], a[1]-b[1], a[2]-b[2]]
  
def add(a, b):
  return [a[0]+b[0], a[1]+b[1], a[2]+b[2]]
  
def multiply(R, v):
  return [ R[0]*v[0] + R[1]*v[1] + R[2]*v[2], R[3]*v[0] + R[4]*v[1] + R[5]*v[2], R[6]*v[0] + R[7]*v[1] + R[8]*v[2]]
  
'''
R[0] R[1] R[2]
R[3] R[4] R[5]
R[6] R[7] R[8]
'''
  
def transpose(R):
  return [ R[0], R[3], R[6],  R[1], R[4], R[7],  R[2], R[5], R[8] ]
  
# apply a coordinate transformation: R*x+t
def transform3(R, t, x):
  return add(multiply(R, x), t)
  
# apply the inverse coordinate transformation: R^T*(x-t)
def transform_inv3(R, t, x):
  return multiply(transpose(R), subtract(x, t))
  
# TODO: remove magic numbers!!!
def globalToImage(camera_node, openingAngleWidth, p):
  
  R = camera_node.getOrientation()
  t = camera_node.getPosition()
  
  # transform ball position to camera coordinates
  v = transform_inv3(R, t, p)
  
  a = openingAngleWidth
  x = 320 - (v[0] / v[2]) * (320.0 / math.tan(a*0.5))  # tan
  y = 240 + (v[1] / v[2]) * (320.0 / math.tan(a*0.5))
  
  # NOTE: v[2] < 0 => ball is in front of the camera, not behind 
  if x >= 0 and y >= 0 and x < 640 and y < 480 and v[2] < 0:
    return v#[x,y]
  else:
    return None
  
# debug: print available methods
def print_methods(o):
  object_methods = [method_name for method_name in dir(o) if callable(getattr(o, method_name))]
  print(object_methods)
  
# experimental: emulate the hand motor
class HandMotor:
  def __init__(self):
    self.l_phalanx1 = self.getDevice("LPhalanx1")
    self.l_phalanx2 = self.getDevice("LPhalanx2")
    self.l_phalanx3 = self.getDevice("LPhalanx3")
    self.l_phalanx4 = self.getDevice("LPhalanx4")
    self.l_phalanx5 = self.getDevice("LPhalanx5")
    self.l_phalanx6 = self.getDevice("LPhalanx6")
    self.l_phalanx7 = self.getDevice("LPhalanx7")
    self.l_phalanx8 = self.getDevice("LPhalanx8")
    
# combine a list of motors and controll them as it is a single motor
class MultiMotor:
    def __init__(self, motors):
        self.motors = motors
    
    def __getattr__(self, name):
        results = []
        # apply methods to all motors
        for m in motors:
            results += [getattr(m, name)(*args, **kwargs)]
        
        return results
    
    
class DualMotor:
  def __init__(self, motorA, motorB):
    self.motorA = motorA
    self.motorB = motorB
    
  def __getattr__(self, name):
    # apply any method call to both motors
    def method(*args, **kwargs):
      getattr(self.motorB, name)(*args, **kwargs)
      # fist mentioned motor is the main motor
      return getattr(self.motorA, name)(*args, **kwargs)
    return method

class Nao(Supervisor):
    def __init__(self):
        super().__init__()
        self.timestep = int(self.getBasicTimeStep())

        # cameras
        self.camera_top = self.getDevice("CameraTop")
        self.camera_bottom = self.getDevice("CameraBottom")
        # image every third simulation frame
        #self.camera_top.enable(self.timestep*3)
        #self.camera_bottom.enable(self.timestep*3)
        
        # supervisor infos about the global positions for gps and virtual vision
        self.camera_top_position = self.getFromDef('NAO_ROBOT.CAM_TOP')
        self.camera_bottom_position = self.getFromDef('NAO_ROBOT.CAM_BOTTOM')
        self.ball_position = self.getFromDef('BALL')
        
        # other sensors
        self.accelerometer = self.getDevice("accelerometer")
        self.accelerometer.enable(self.timestep)
        
        self.gyro = self.getDevice("gyro")
        self.gyro.enable(self.timestep)
        
        self.imu = self.getDevice("inertial unit")
        self.imu.enable(self.timestep)
        
        
        # TODO add fsr like in webots nao demo
        self.fsr_r = self.getDevice("RFsr")
        self.fsr_r.enable(self.timestep)
        
        self.fsr_l = self.getDevice("LFsr")
        self.fsr_l.enable(self.timestep)

        # create actuator members
        # order of joints - needed for lola
        self.joint_names = [
          "HeadYaw",
          "HeadPitch",
          "LShoulderPitch",
          "LShoulderRoll",
          "LElbowYaw",
          "LElbowRoll",
          "LWristYaw",
          "LHipYawPitch", # "RHipYawPitch"
          "LHipRoll",
          "LHipPitch",
          "LKneePitch",
          "LAnklePitch",
          "LAnkleRoll",
          "RHipRoll",
          "RHipPitch",
          "RKneePitch",
          "RAnklePitch",
          "RAnkleRoll",
          "RShoulderPitch",
          "RShoulderRoll",
          "RElbowYaw",
          "RElbowRoll",
          "RWristYaw",
          "LHand",
          "RHand"
        ]
        
        self.joints = [self.getDevice(name) for name in self.joint_names]
        self.joints_sensors = [self.getDevice(name + "S") for name in self.joint_names]
        #print(self.joints)
        
        # enable joint position sensors
        for joint in self.joints_sensors:
          if joint is not None:
            joint.enable(self.timestep)
            
        # experimental: set more realistic PID parameters
        for j in self.joints:
          if j is not None:
            j.setControlPID(40,1,0.3)

    # NOTE: this deals with the hand joints. Each falanx 
    #       is a separate motor in webots. We need to 
    #       implement a combined joint.
    # TODO: this needs to be implemented correctly
    def getDevice(self, name):
      if name == "LHipYawPitch" or name == "RHipYawPitch":
        print("create a dual motor")
        l = super().getDevice("LHipYawPitch")
        r = super().getDevice("RHipYawPitch")
        return DualMotor(l,r)
      elif name == "LHand" or name == "RHand":
        print(f"WARNING: Joint {name} does not exist.")
        return None
      elif name == "LHandS" or name == "RHandS":
        print(f"WARNING: Joint {name} does not exist.")
        return None
      
      return super().getDevice(name)
      
            
    def get_joint_positions(self):
      return [joint.getValue() for joint in self.joints_sensors if joint is not None]
      
    def set_joint_positions(self, positions):
      for (joint, p) in zip(self.joints, positions):
        if joint is not None:
          joint.setPosition(p)
    
    def get_virtual_vision(self):
      # global ball coordinates
      ball = self.ball_position.getPosition()
      # add radius to get the true ball center
      r = self.ball_position.getField("radius").getSFFloat()
      ball[1] += r
      
      # calculate ball in image
      openingAngleWidth = self.camera_bottom.getFov()
      ball_top = globalToImage(self.camera_top_position, openingAngleWidth, ball)
      ball_bottom = globalToImage(self.camera_bottom_position, openingAngleWidth, ball)
      
      if ball_bottom is not None:
        virtual_vision = {"Seen": True, "Position": ball_bottom, "Cam": "bottom"}
        #rt = self.getSelf().getPosition()
        #rR = self.getSelf().getOrientation()
        #ball_local = transform_inv3(rR, rt, ball)
        #print(ball_local)
      elif ball_top is not None:
        virtual_vision = {"Seen": True, "Position": ball_top, "Cam": "top"}
      else:
        virtual_vision = {"Seen": False, "Position": [-1,-1,-1]}
      
      return virtual_vision
      
      
    ''' Example of sensor data received from the LOLA on NAO 6.
    {
      "RobotConfig":["P0000073A03S83I00011","6.0.0","P0000074A03S84F00006","6.0.0"],
      "Accelerometer":[8.66997,0.287402,-5.48939],
      "Angles":[-0.0239685,0.990951],
      "Battery":[0.99,-32552,0.016,3.6],
      "Current":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      "FSR":[0.190524,1.52253,0.000270986,0.654938,1.86128,0.130825,0.692107,0.000510382],
      "Gyroscope":[0.00186421,-0.00559264,0],
      "Position":[0.00302601,0.54913,0.544528,0.0674541,-1.45734,-0.0122299,-0.122762,-0.513848,-0.30369,-1.44038,2.13375,-1.21497,0.024586,0.222472,-1.43126,2.1231,-1.20568,0.0322559,0.503194,-0.0276539,1.58305,0.024586,-0.0997519,0.0188,0.036],
      "Sonar":[0.2,0.2],
      "Stiffness":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      "Temperature":[38,40,38,38,38,38,38,33,27,27,27,27,27,27,27,27,27,27,38,38,38,38,38,38,38],
      "Touch":[0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      "Status":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    }
    '''
    def getSensors(self):
    
      acc = self.accelerometer.getValues()
      imu = self.imu.getRollPitchYaw()
      gyro = self.gyro.getValues()
      
      fsrL = length3(self.fsr_l.getValues())
      fsrR = length3(self.fsr_r.getValues())
        
      data = {
        "lolaSensors": {
          "RobotConfig"  : ["WEBOTS","6.0.0","WEBOTS","6.0.0"],
          "Accelerometer": acc,
          "Angles"       : imu[0:2],
          "Battery"      : [0.99,-32552,0.016,3.6],
          "Current"      : [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
          "FSR"          : [fsrL,fsrL,fsrL,fsrL, fsrR,fsrR,fsrR,fsrR],
          "Gyroscope"    : gyro,
          "Position"     : self.get_joint_positions(),
          "Sonar"        : [0.2,0.2],
          "Stiffness"    : [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
          "Temperature"  : [38,40,38,38,38,38,38,33,27,27,27,27,27,27,27,27,27,27,38,38,38,38,38,38,38],
          "Touch"        : [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
          "Status"       : [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        },
        # get position from the supervisor
        "GPS"  : {"Position": self.getSelf().getPosition(), "Rotation": self.getSelf().getOrientation()},
        "Time" : self.getTime(),
        "Ball" : self.get_virtual_vision()
      }
      
      return data
        
    def setActuators(self, data):
      self.set_joint_positions(data['Position'])
        
    
