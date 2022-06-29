import os,sys
import Sofa
from stlib3.scene import Scene
dirPath = os.path.dirname(os.path.abspath(__file__))+'/'
from stlib3.visuals import VisualModel
from fixingbox import FixingBox

class ServoMotor(Sofa.Prefab):
    '''A S90 servo motor

    This prefab is implementing a S90 servo motor.
    https://servodatabase.com/servo/towerpro/sg90

    The prefab ServoMotor is composed of:
    - a visual model
    - a mechanical model composed two rigids. One rigid is for the motor body
      while the other is implementing the servo rotating wheel.

    The prefab has the following parameters:
    - translation           to change default location of the servo (default [0.0,0.0,0.0])
    - rotation              to change default rotation of the servo (default [0.0,0.0,0.0,1])
    - scale                 to change default scale of the servo (default 1)
    - showServo             to control wether a visual model of the motor is added (default True)
    - showWheel             to control wether the rotation axis of the motor is displayed (default False)

    The prefab have the following property:
    - angle         use this to specify the angle of rotation of the servo motor
    - angleLimits   use this to set a min and max value for the servo angle rotation
    - position      use this to specify the position of the servo motor

    Example of use in a Sofa scene:

    def addScene(root):
        ...
        servo = ServoMotor(root)

        ## Direct access to the components
        servo.angle.value = 1.0
    '''
    properties = [
        {'name':'name',                'type':'string', 'help':'Node name',                   'default':'ServoMotor'},
        {'name':'rotation',            'type':'Vec3d',  'help':'Rotation',                    'default':[0.0, 0.0, 0.0]},
        {'name':'translation',         'type':'Vec3d',  'help':'Translation',                 'default':[0.0, 0.0, 0.0]},
        {'name':'scale3d',               'type':'Vec3d',  'help':'Scale 3d',                    'default':[1.0, 1.0, 1.0]}]

    def __init__(self, *args, **kwargs):
        Sofa.Prefab.__init__(self, *args, **kwargs)

    def init(self):

        # The inputs
        self.addData(name='minAngle', group='S90Properties', help='min angle of rotation (in radians)', type='float', value=-100)
        self.addData(name='maxAngle', group='S90Properties', help='max angle of rotation (in radians)', type='float', value=100)
        self.addData(name='angleIn', group='S90Properties', help='angle of rotation (in radians)', type='float', value=0)

        # Servo body
        servoBody = self.addChild('ServoBody')
        mechanicalmodel = servoBody.addChild("MechanicalModel")
        # mechanicalmodel.addObject('MeshGmshLoader',
        #                           name='loader',
        #                           rotation=list(self.rotation.value),
        #                           translation=list(self.translation.value),
        #                           filename='data/Ass_robot/Axis_2.msh')
        # mechanicalmodel.addObject('TetrahedronSetTopologyContainer',
        #                           src='@loader',
        #                           name='container')
        mechanicalmodel.addObject('MechanicalObject', name='dofs',
                                  template='Rigid3d',
                                  # position=[[0., 0., 0., 0., 0., 0., 1.]],
                                  translation=list(self.translation.value),
                                  rotation=list(self.rotation.value),
                                  scale3d=list(self.scale3d.value))
        mechanicalmodel.addObject('FixedConstraint')
        mechanicalmodel.addObject('UniformMass',name="mass", vertexMass=[1, 1, [1., 0., 0., 0., 1., 0., 0., 0., 1.]])


        visual = servoBody.addChild('VisualModel')
        visual.addObject('MeshSTLLoader', name='loader', filename='data/Ass_robot/Axis_2.STL')
        visual.addObject('MeshTopology', src='@loader')
        visual.addObject('OglModel', name='renderer',color=[0.15, 0.45, 0.75, 0.7], writeZTransparent=True)
        visual.addObject('RigidMapping',input=mechanicalmodel.dofs.getLinkPath(),
                          output=visual.renderer.getLinkPath())
        #coliision
        objectCollis = servoBody.addChild('collision')
        objectCollis.addObject('MeshGmshLoader',
                                  name='loader',
                                  rotation=list(self.rotation.value),
                                  translation=list(self.translation.value),
                                  filename='data/Ass_robot/Axis_2.msh')
        objectCollis.addObject('MeshTopology', src="@loader")
        objectCollis.addObject('MechanicalObject')
        objectCollis.addObject('TriangleCollisionModel',)
        objectCollis.addObject('LineCollisionModel', )
        objectCollis.addObject('PointCollisionModel', )
        objectCollis.addObject('RigidMapping',input=mechanicalmodel.dofs.getLinkPath(),)

        # # Servo wheel
        angle = self.addChild('Articulation')
        angle.addObject('MechanicalObject', name='dofs', template='Vec1', position=[[0]],
                        # rest_position=self.getData('angleIn').getLinkPath()
                        )
        # angle.addObject('RestShapeSpringsForceField', points=0, stiffness=1e9)
        angle.addObject('UniformMass', totalMass=0.01)

        servoWheel = angle.addChild('ServoWheel')
        servoWheel.addObject('MechanicalObject', name='dofs', template='Rigid3', position=[[0., 0., 0., 0., 0., 0., 1.],[0., 0., 0., 0., 0., 0., 1.]], showObjectScale=10,
                                    translation=list(self.translation.value),rotation=list(self.rotation.value),scale3d=list(self.scale3d.value))
        servoWheel.addObject('ArticulatedSystemMapping', input1="@../dofs", input2="@../../ServoBody/MechanicalModel/dofs", output="@./")

        ServoArm = servoWheel.addChild('ServoArm')
        ServoArm.addObject('MechanicalObject',
                       name='dofs',
                       size=1,
                       template='Rigid3',
                       showObject=True,
                       showObjectScale=5,
                       translation=[10, 0, 0])
        ServoArm.addObject('UniformMass', totalMass=0.01)
        ServoArm.addObject('RigidRigidMapping', name='mapping', input="@../dofs", index=1)
        #
        # # #visual model
        visual1=ServoArm.addChild('VisualModel')
        visual1.addObject('MeshSTLLoader', name='loader', filename='data/Ass_robot/upperArm_Long.STL',
                          translation=[0.0, 0.0, 0.0],
                          rotation=[0.0, 0.0, 0.0])
        visual1.addObject('MeshTopology', src='@loader')
        visual1.addObject('OglModel',color=[0.5, 0.45, 0.75, 0.7], writeZTransparent=True)
        visual1.addObject('RigidMapping')


        articulationCenter = angle.addChild('ArticulationCenter')
        articulationCenter.addObject('ArticulationCenter', parentIndex=0, childIndex=1, posOnParent=[0., 0., 0.], posOnChild=[0., 0., 0.])
        articulation = articulationCenter.addChild('Articulations')
        articulation.addObject('Articulation', translation=False, rotation=True, rotationAxis=[0, 1, 0], articulationIndex=0)
        angle.addObject('ArticulatedHierarchyContainer', printLog=False)

        # The output
        self.addData(name='angleOut', group='S90Properties', help='angle of rotation (in degree)', type='float', value=angle.dofs.getData('position').getLinkPath())


def createScene(rootNode):

    import math
    from splib3.animation import animate

    def animation(target, factor):
        target.angleIn.value = math.cos(factor * 2 * math.pi)

    scene = Scene(rootNode, plugins=['SofaConstraint', 'SofaGeneralRigid', 'SofaOpenglVisual', 'SofaRigid',
                                     ], iterative=False)
    scene.addMainHeader()
    scene.addObject('DefaultVisualManagerLoop')
    scene.addObject('FreeMotionAnimationLoop')
    scene.addObject('GenericConstraintSolver', maxIterations=1e3, tolerance=1e-5)
    scene.Simulation.addObject('GenericConstraintCorrection')
    scene.Settings.mouseButton.stiffness = 0.1
    scene.dt = 0.01
    scene.gravity = [0., -9810., 0.]
    scene.Modelling.addChild(ServoMotor(name="ServoMotor"))
    scene.Simulation.addChild(scene.Modelling.ServoMotor)
    # animate(animation, {'target': scene.Simulation.ServoMotor}, duration=10., mode='loop')
    # scene.Simulation.ServoMotor.Articulation.ServoWheel.dofs.showObject = True

    # box1 = FixingBox(scene.Modelling.ServoMotor,
    #                  scene.Modelling.ServoMotor.ServoBody.MechanicalModel,
    #                  name="box1",
    #                  translation=[0.0, 0.0, 0.0],
    #                  scale=[5., 5., 5.])
    # box1.BoxROI.drawBoxes = True
    # scene.Simulation.addChild(scene.Modelling.ServoMotor.box1)
    return scene

if __name__ == '__main__':
    # runSofa.exe路径
    path = "D:/Software_download/sofa_22/SOFA_robosoft2022_python-3.8_Windows/bin/runSofa"
    # 使用Sofa运行该文件
    os.system(path + " " + sys.argv[0])
