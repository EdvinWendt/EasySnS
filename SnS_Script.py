import pymel.core as pm
import math
from PySide2   import QtCore
from PySide2   import QtWidgets
from PySide2   import QtGui
from functools import partial    #Arguments for button connections

# CreateCTRLS
# CreateMessure - getMaxDistance
# CreateExpression
# WriteExpression#
# print 'offsetNorm = X = ' + str(offsetNorm[0]) + ', Y = ' + str(offsetNorm[1]) + ', Z = ' + str(offsetNorm[2])
# pCube1.rotateX = pCube2.rotateX;
startJoint = []
endJoint = []
sizeValue = 1.0

# --------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------- Minor Functions ------------------------------------------------------------------------ #
# --------------------------------------------------------------------------------------------------------------------------------------------------------------- #

jntList = []
def getJntList(startJnt, endJnt):
    global jntList
    for child in startJnt.getChildren():
        if (child == endJnt):
            for jnt in jntList:
                print str(jnt)
            
        else:
            jntList.append(child)
            getJntList(child, endJnt)

def getMiddlePoint(startJnt, endJnt):
        middlePos = [0, 0, 0]

        startPos = pm.xform(startJnt, q = True, ws = True, rp = True)
        endPos   = pm.xform(endJnt, q = True, ws = True, rp = True)

        middlePos[0] = (startPos[0] + endPos[0]) / 2
        middlePos[1] = (startPos[1] + endPos[1]) / 2
        middlePos[2] = (startPos[2] + endPos[2]) / 2
        
        return middlePos

def getPlacingPoint(startJnt, endJnt):
    global jntList
    middlePos = [0, 0, 0]
    
    if (int(len(jntList)) % 2) == 0:
        jntA = jntList[int(len(jntList) / 2) - 1]
        jntB = jntList[int(len(jntList) / 2)]
        middlePos = getMiddlePoint(jntA, jntB)
        
        
    else:
        middleJnt = jntList[int(len(jntList) / 2)]
        middleJntPos = pm.xform(middleJnt, q = True, ws = True, rp = True)
        middlePos[0] = middleJntPos[0]
        middlePos[1] = middleJntPos[1]
        middlePos[2] = middleJntPos[2]

    return middlePos

maxDistance = 0   
def getMaxLength(jnt, endJnt):
    global maxDistance
    child = jnt.getChildren()[0]
    jntPos = pm.xform(jnt, q = True, ws = True, rp = True)
    childPos = pm.xform(child, q = True, ws = True, rp = True)
    
    vec = [0, 0, 0]
    vec[0] = childPos[0] - jntPos[0]
    vec[1] = childPos[1] - jntPos[1]
    vec[2] = childPos[2] - jntPos[2]
    
    len = math.sqrt(pow(vec[0], 2) + pow(vec[1], 2) + pow(vec[2], 2))
    maxDistance += len
    
    if (child != endJnt):
        getMaxLength(child, endJnt)
    
stretchString = ""
def getStretchString(jnt, endJnt, distanceShape):
    global maxDistance
    global stretchString
    child = jnt.getChildren()[0]
    
    stretchString += "    " + str(jnt) + ".scaleX = " + str(distanceShape) + ".distance / " + str(maxDistance) + ";\n"
    
    if (child != endJnt):
        getStretchString(child, endJnt, distanceShape)

squashString = ""       
def getSquashString(jnt, endJnt):
    global squashString
    child = jnt.getChildren()[0]
    
    squashString += "    " + str(jnt) + ".scaleX = 1;\n"
    
    if (child != endJnt):
        getSquashString(child, endJnt)

# --------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------------------- Major Functions ------------------------------------------------------------------------- #
# --------------------------------------------------------------------------------------------------------------------------------------------------------------- #


def createCTRLS(startJnt, endJnt):
    # 1) Create group and controller:
    grp  = pm.group(name = 'EasySnS', empty = True)
    ctrl = pm.circle(name = 'IK_CTRL', normal = (0, 1, 0), center = (0, 0, 0) )[0]
    pm.addAttr(longName = "ActivateSquash", attributeType = 'bool', keyable = True, defaultValue = False)
    
    # 2) Prepera to move controller:
    pm.parentConstraint(endJnt, grp)
    pm.delete(str(grp) + '_parentConstraint1')
    
    # 3) Move controller:
    pm.parent(ctrl, grp)
    ctrl.setAttr('translate', 0, 0, 0)
    ctrl.setAttr('rotate', 0, 0, 90)
    ctrl.setAttr('scale', sizeValue, sizeValue, sizeValue)
    
    # 4) Clean up controller:
    pm.makeIdentity(ctrl, apply = True, translate = True, rotate = True, scale = True)
    pm.delete(ctrl, ch = True)
    
    # -------------------------------------
    
    # 1) Crate controller:
    ctrl2 = pm.sphere(name = 'LookAt_CTRL')[0]
    
    # 2) Find between positions:
    getJntList(startJnt, endJnt)
    betweenJointPos    = getPlacingPoint(startJnt, endJnt)
    betweenStartEndPos = getMiddlePoint(startJnt, endJnt)
    
    # 3) Calculate offset:
    offsetVec = [0, 0, 0]
    offsetVec[0] = betweenJointPos[0] - betweenStartEndPos[0]
    offsetVec[1] = betweenJointPos[1] - betweenStartEndPos[1]
    offsetVec[2] = betweenJointPos[2] - betweenStartEndPos[2]

    offsetLen = math.sqrt(pow(offsetVec[0], 2) + pow(offsetVec[1], 2) + pow(offsetVec[2], 2))
    
    offsetNorm = [0, 0, 0]
    offsetNorm[0] = offsetVec[0] / offsetLen
    offsetNorm[1] = offsetVec[1] / offsetLen
    offsetNorm[2] = offsetVec[2] / offsetLen

    # 4) Set Poition for controller:
    ctrl2Pos = [0, 0, 0]
    ctrl2Pos[0] = betweenJointPos[0] + (offsetNorm[0] * (sizeValue * 1.5))
    ctrl2Pos[1] = betweenJointPos[1] + (offsetNorm[1] * (sizeValue * 1.5))
    ctrl2Pos[2] = betweenJointPos[2] + (offsetNorm[2] * (sizeValue * 1.5))
    ctrl2.setAttr('translate', ctrl2Pos[0], ctrl2Pos[1], ctrl2Pos[2])
    ctrl2.setAttr('rotate', 0, 0, 90)
    ctrl2.setAttr('scale', sizeValue / 2, sizeValue / 2, sizeValue / 2)
    pm.parent(ctrl2, grp)
    
    # 5) Clean up controller:
    pm.makeIdentity(ctrl2, apply = True, translate = True, rotate = True, scale = True)
    pm.delete(ctrl2, ch = True)
    
    # -------------------------------------
    
    return ctrl, ctrl2, grp
    
def createConstrains(startJnt, endJnt, ctrl, ctrl2, grp):
    IK_Handle, IK_Effector = pm.ikHandle(name = "IK_Handle", sj = startJnt, ee = endJnt, solver = "ikRPsolver")
    IK_Handle.setAttr('visibility', False)
    
    pm.parent(IK_Handle, grp)
    pm.parentConstraint(ctrl, IK_Handle, name = "Praent_Constraint")
    pm.poleVectorConstraint(ctrl2, IK_Handle, name = "Pole_Vector")
    pm.orientConstraint(ctrl, endJnt, name = "Rotate_Constraint")
    pm.scaleConstraint(ctrl, endJnt, name = "Scale_Constraint")
    
    
def createExpression(startJnt, endJnt, ctrl, ctrl2, grp):
    global maxDistance
    global stretchString
    global squashString
    maxDistance -= 0.001
    
    distanceShape = pm.distanceDimension(startPoint = pm.xform(startJnt, q = True, ws = True, rp = True), endPoint = pm.xform(endJnt, q = True, ws = True, rp = True))
    startLocator, endLocator = pm.listConnections(distanceShape)
    distance = pm.listRelatives(distanceShape, p = True)[0]
    pm.parent(distance, grp)
    pm.parent(startLocator, grp)
    pm.parent(endLocator, grp)
    pm.rename(distance, "Distance")
    pm.rename(startLocator, "Start_Locator")
    pm.rename(endLocator, "End_Locator")
    pm.pointConstraint(startJnt, startLocator, name = "Point_Constraint")
    pm.pointConstraint(ctrl, endLocator, name = "Point_Constraint")
    distance.setAttr('visibility', False)
    startLocator.setAttr('visibility', False)
    endLocator.setAttr('visibility', False)
    
    getMaxLength(startJnt, endJnt)
    getStretchString(startJnt, endJnt, distanceShape)
    getSquashString(startJnt, endJnt)
    
    expressionString = "if(" + str(distanceShape) + ".distance >= " + str(maxDistance) + " || " + str(ctrl) + ".ActivateSquash)\n"
    expressionString += "{\n"
    expressionString += stretchString
    expressionString += "}\n"
    expressionString += "else\n"
    expressionString += "{\n"
    expressionString += squashString
    expressionString += "}\n"
    pm.expression(name = str(grp) + "_Expression", string = expressionString)
    try:
        pm.expression(name = str(grp) + "_Expression", string = expressionString)
        
    except:
        pm.delete(str(grp) + "_Expression")
        pm.expression(name = str(grp) + "_Expression", string = expressionString)
        
    select(ctrl)
       
def enableConstarinButton():
    global startJoint
    global endJoint
    if str(startJoint) != "[]" and str(endJoint) != "[]":
        constrainButton.setEnabled(True)
     
# --------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------------------------- Button Logic -------------------------------------------------------------------------- #
# --------------------------------------------------------------------------------------------------------------------------------------------------------------- #

helpToggle = False
def helpButtonFunc():
    global helpToggle
    startJntButton .setVisible(helpToggle)
    endJntButton   .setVisible(helpToggle)
    textC          .setVisible(helpToggle)
    minusButton    .setVisible(helpToggle)
    sizeInput      .setVisible(helpToggle)
    plusButton     .setVisible(helpToggle)
    constrainButton.setVisible(helpToggle)
    helpText       .setVisible(not helpToggle)

    if (helpToggle == False):
        helpButton.setText("Back")
        helpToggle = True
    else:
        helpButton.setText("Help")
        helpToggle = False

def minus():
    global sizeValue
    sizeValue = float(sizeInput.text())
    sizeValue -= 1.0
    if (sizeValue <= 0):
        sizeValue = 0.0
    sizeInput.setText(str(sizeValue))

def plus():
    global sizeValue
    sizeValue = float(sizeInput.text())
    sizeValue += 1.0
    if (sizeValue <= 0):
        sizeValue = 0.0
    sizeInput.setText(str(sizeValue))


def getStartJoint():
    global startJoint 
    startJoint = pm.ls(selection = True)[0]
    if (str(startJoint.nodeType()) == 'joint'):
        startJntButton.setText(str(startJoint))
        enableConstarinButton()
    else:
        pm.warning('The selection must be a joint')


def getEndJoint():
    global endJoint
    endJoint = pm.ls(selection = True)[0]
    if (str(endJoint.nodeType()) == 'joint'):
        endJntButton.setText(str(endJoint))
        enableConstarinButton()
    else:
        pm.warning('The selection must be a joint')

def main():
    global startJoint
    global endJoint
    global jntList
    global maxDistance
    global stretchString
    global squashString
    jntList = []
    maxDistance = 0   
    stretchString = ""
    squashString = "" 

    ctrl, ctrl2, grp = createCTRLS(startJoint, endJoint)
    createConstrains(startJoint, endJoint, ctrl, ctrl2, grp)
    createExpression(startJoint, endJoint, ctrl, ctrl2, grp)
    
# --------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- Window ----------------------------------------------------------------------------- #
# --------------------------------------------------------------------------------------------------------------------------------------------------------------- #

# --- Initialize window --- #
application = QtWidgets.QApplication.instance()
myWindow = QtWidgets.QWidget()
myWindow.resize(400, 400)
myWindow.setWindowTitle("Squash and Stretch Tool")
myWindow.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

# --- Title Text --- #
titleText = QtWidgets.QLabel(myWindow)
titleText.setText("Easy Squash and Stretch")
titleText.setStyleSheet("font: 20pt;")
titleText.move(52, 20)

# --- Name Text --- #
nameText = QtWidgets.QLabel(myWindow)
nameText.setText("Tristan Wikstrom, Edvin Wendt")
nameText.setStyleSheet("font: 8pt;")
nameText.move(120, 60)

# --- Help Button --- #
helpButton = QtWidgets.QPushButton(myWindow)
helpButton.resize(40, 20)
helpButton.move(355, 5)
helpButton.setText("Help")
helpButton.clicked.connect(helpButtonFunc)

# --- Help Text --- #
helpText = QtWidgets.QLabel(myWindow)

helpText.setText("""Note!     For this tool to work on a model the user must
provide a weight painted skeletal mesh. The area the user
wants to apply the squash and stretch constraints on can
not have any existing constarins, they must be removed.
                              
How to use this tool:
1) Select the first joint that you want.
2) Select the second joint that you want.
3) Select the desiered settings.
4) Click the Create Constarins button.""")
helpText.setStyleSheet("font: 10pt;")
helpText.move(40, 100)
helpText.setVisible(False)

# --- Start Joint --- #
startJntButton = QtWidgets.QPushButton(myWindow)
startJntButton.resize(300, 30)
startJntButton.move((400 / 2) - 150, 100)
startJntButton.setText("Select start Joint...")
startJntButton.clicked.connect(getStartJoint)

# --- End Joint --- #
endJntButton = QtWidgets.QPushButton(myWindow)
endJntButton.resize(300, 30)
endJntButton.move((400 / 2) - 150, 140)
endJntButton.setText("Select End Joint...")
endJntButton.clicked.connect(getEndJoint)

# --- Size Input --- #
textC = QtWidgets.QLabel(myWindow)
textC.setText("Select Controller Size:")
textC.move(50, 230)
# 1
minusButton = QtWidgets.QPushButton(myWindow)
minusButton.resize(25, 25)
minusButton.move(172, 225)
minusButton.setText("-")
minusButton.clicked.connect(minus)
# 2
sizeInput = QtWidgets.QLineEdit(myWindow)
sizeInput.move(203, 225)
sizeInput.resize(50,25)
sizeInput.setValidator(QtGui.QIntValidator(0, 100))
sizeInput.setText(str(sizeValue))
# 3
plusButton = QtWidgets.QPushButton(myWindow)
plusButton.resize(25, 25)
plusButton.move(259, 225)
plusButton.setText("+")
plusButton.clicked.connect(plus)

# --- Create constrains --- #
constrainButton = QtWidgets.QPushButton(myWindow)
constrainButton.resize(300, 40)
constrainButton.move((400 / 2) - 150, 325)
constrainButton.setText("Create Constrains")
constrainButton.clicked.connect(main)
constrainButton.setEnabled(False)

# --- Finalize window --- #
myWindow.show()
application.exec_()

# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv #