'''
author: Julian Bueche

Programmstart wie gewünscht mit RenderWindow.py objFile.obj
oder auch nur mit RenderWindow.py und als Default wird das Bunny geladen.

Maustastenbelegung bei gedrückter Taste
LINKS - Objekt rotieren
MITTE - Objekt zoomen
RECHTS - Objekt verschieben

Tastaturbelegung
Y - Hintergrund Gelb
S - Hintergrund Schwarz
W - Hintergrund Weiss
B - Hintergrund Blau
R - Hintergrund Rot
--> Mit Shift jeweils das Objekt in der Farbe wechseln.
O - Umstellen auf orthograpische Projektion
P - Umstellen auf perspektische Projektion
H - Schatten Aus/An
ESC - Beenden
'''
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo
import numpy as np

class Scene:

    def __init__(self, width, height, filename):
        self.vertices = []
        self.vn = []
        self.faces = []
        self.NeedNormals = False
        self.readValues(filename)
        self.min, self.max = 0,0
        self.boundingBox()
        self.center = self.getMidOfBoundingbox()
        self.curOrientation = [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]]
        self.angle = 0
        self.axis = np.array([0,0,1])
        self.newPosX = 0
        self.newPosY = 0
        self.startPoint = [0,0,0]
        self.light = np.array([1.0, 1.0, 1.0, 0.0])
        self.boundingBox()
        self.point = np.array([0, 0])
        self.vector = np.array([10, 10])
        self.t = 0
        self.pointsize = 3
        self.width = width
        self.height = height
        self.zoom = 0
        self.scaleFactor = self.scale()
        self.color = (1.0, 0.0, 0.0) #Red
        self.shadowColor = (0.0, 0.0, 0.0) #Black
        self.bg_color = (1.0, 1.0, 1.0, 0) #White
        self.showVector = True
        self.doRotate = False
        self.zooming = False
        self.translation = False
        self.shadow = True
        glPointSize(self.pointsize)
        glLineWidth(self.pointsize)

        self.data = []
        for vertex in self.faces:
            vn = int(vertex[0]) - 1
            nn = int(vertex[1]) - 1
            if self.NeedNormals:
                # Normalen berechnung, falls vn's leer
                index1 = int(vertex[0]-1)
                index2 = int(vertex[1]-1)
                index3 = int(vertex[2]-1)
                normal = self.calcNormals(self.vertices[index1], self.vertices[index2], self.vertices[index3])
                self.data.append(self.vertices[index1] + normal)
                self.data.append(self.vertices[index2] + normal)
                self.data.append(self.vertices[index3] + normal)
            else:
                self.data.append(self.vertices[vn] + self.vn[nn])
        self.myVBO = vbo.VBO(np.array(self.data, 'f'))

    def calcNormals(self, v1, v2, v3):
        x = [v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2]]
        y = [v3[0] - v1[0], v3[1] - v1[1], v3[2] - v1[2]]
        n = [x[1]*y[2] - x[2]*y[1],
             x[2]*y[0] - x[0]*y[2],
             x[0]*y[1] - x[1]*y[0]]
        return n

    def readValues(self, obj):
        file = open(obj)
        for lines in file:
            if lines.split():
                if lines.split()[0] == 'v':
                    self.vertices.append(list((float(lines.split()[1]), float(lines.split()[2]), float(lines.split()[3]))))
                if lines.split()[0] == 'vn':
                    self.vn.append(list((float(lines.split()[1]), float(lines.split()[2]), float(lines.split()[3]))))
                if lines.split()[0] == 'f':
                    values = lines.split()[1:]
                    if '//' in lines:
                        for face in values:
                            self.faces.append(list(map(float, face.split('//'))))
                    else:
                        self.faces.append(list((float(lines.split()[1]), float(lines.split()[2]), float(lines.split()[3]))))

        if len(self.vn) <= 0:
            self.NeedNormals = True
            self.vn = self.vertices

    def boundingBox(self):
        xvalues = [x[0] for x in self.vertices]
        yvalues = [y[1] for y in self.vertices]
        zvalues = [z[2] for z in self.vertices]
        self.min = ((np.min(xvalues)), (np.min(yvalues)), (np.min(zvalues)))
        self.max = ((np.max(xvalues)), (np.max(yvalues)), (np.max(zvalues)))
        self.light = (
            -(self.min[1] - self.max[1])*2,
            -(self.min[1] - self.max[1])*5,
            -(self.min[1] - self.max[1])*2
        )

    def scale(self):
        xr = self.max[0] - self.min[0]
        yr = self.max[1] - self.min[1]
        zr = self.max[2] - self.min[2]
        scale = 1.5 / max(xr, yr, zr)
        return scale

    def getMidOfBoundingbox(self):
        p = np.array(self.min)
        q = np.array(self.max)
        mid = (p + q) / 2
        x,y,z = mid
        return x,y,z

    def translate(self):
        #noch ändern
        xmin, ymin, zmin = self.min
        xmax, ymax, zmax = self.max
        transx = - ((self.max[0] + self.min[0]) / 2.0)
        transy = - ((self.max[1] + self.min[1]) / 2.0)
        transz = - ((self.max[2] + self.min[2]) / 2.0)
        return transx, transy, transz

    def setColor(self, color):
        if color == 'blue':
            self.color = (0.0, 0.0, 1.0)
        if color == 'yellow':
            self.color = (1.0, 1.0, 0.0)
        if color == 'red':
            self.color = (1.0, 0.0, 0.0)
        if color == 'white':
            self.color = (1.0, 1.0, 1.0)
        if color == 'black':
            self.color = (0.0, 0.0, 0.0)

    def setBGColor(self, color):
        if color == 'blue':
            glClearColor(0.0, 0.0, 1.0, 0.0)
        if color == 'yellow':
            glClearColor(1.0, 1.0, 0.0, 0.0)
        if color == 'red':
            glClearColor(1.0, 0.0, 0.0, 0.0)
        if color == 'white':
            glClearColor(1.0, 1.0, 1.0, 0.0)
        if color == 'black':
            glClearColor(0.0, 0.0, 0.0, 0.0)

    def setShadow(self, s):
        self.shadow = s

    def rotate(self, angle, axis):
        c, mc = np.cos(angle), 1 - np.cos(angle)
        s = np.sin(angle)
        l = np.sqrt(np.dot(np.array(axis), np.array(axis)))
        x, y, z = np.array(axis) / l
        r = np.matrix(
            [[x * x * mc + c, x * y * mc - z * s, x * z * mc + y * s, 0],
             [x * y * mc + z * s, y * y * mc + c, y * z * mc - x * s, 0],
             [x * z * mc - y * s, y * z * mc + x * s, z * z * mc + c, 0],
             [0, 0, 0, 1]])
        return r.transpose()

    def projectOnSphere(self, x, y, r):
        x,y = x - self.width / 2.0, self.height / 2.0 - y
        a = min(r*r, x**2 + y**2)
        z = np.sqrt(r*r - a)
        l = np.sqrt(x**2 + y**2 + z**2)
        return x/l, y/l, z/l

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.myVBO.bind()
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glVertexPointer(3, GL_FLOAT, 24, self.myVBO)
        glNormalPointer(GL_FLOAT, 24, self.myVBO + 12)
        glLoadIdentity()

        if self.newPosX is not None:
            glTranslatef(self.newPosX, self.newPosY, 0.0)

        glLightfv(GL_LIGHT0, GL_POSITION, self.light)

        glColor(*self.color)
        glEnable(GL_COLOR_MATERIAL)

        print("angle", self.angle)
        print("axis", self.axis)
        print("actOri", self.curOrientation)
        glMultMatrixf(self.curOrientation * self.rotate(self.angle, self.axis))
        glScale(self.scaleFactor, self.scaleFactor, self.scaleFactor)
        x,y,z = self.getMidOfBoundingbox()
        glTranslate(-x, -y, -z)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glDrawArrays(GL_TRIANGLES, 0, len(self.data))

        if self.shadow:
            xLight, yLight, zLight = self.light
            p = [1.0, 0, 0, 0, 0, 1.0, 0, -1.0 / (yLight), 0, 0, 1.0, 0, 0, 0, 0, 0]
            glColor3fv(self.color)
            glCallList(self.myVBO)
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glTranslatef(xLight, yLight, zLight)
            glTranslate(0, self.min[1], 0)

            glMultMatrixf(p)
            glTranslatef(-xLight, -yLight, -zLight)
            glTranslatef(0, -self.min[1], 0)
            glColor3fv((0,0,0))
            glDrawArrays(GL_TRIANGLES, 0, len(self.data))

            glCallList(self.myVBO)
            glPopMatrix()

        self.myVBO.unbind()
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisable(GL_COLOR_MATERIAL)


class RenderWindow:

    def __init__(self):
        cwd = os.getcwd()
        if not glfw.init():
            return
        os.chdir(cwd)
        glfw.window_hint(glfw.DEPTH_BITS, 32)
        self.frame_rate = 100

        self.mouse_x = 0
        self.mouse_y = 0
        self.ortho = True
        self.perspective = False

        # make a window
        self.width, self.height = 640, 480
        self.aspect = self.width / float(self.height)
        self.window = glfw.create_window(self.width, self.height, "2D Graphics", None, None)
        if not self.window:
            glfw.terminate()
            return

        glfw.make_context_current(self.window)

        glViewport(0, 0, self.width, self.height)
        glEnable(GL_DEPTH_TEST)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glMatrixMode(GL_PROJECTION)
        glOrtho((-1.5) * self.aspect, 1.5 * self.aspect, -1.5, 1.5, -10.0, 10.0)
        glMatrixMode(GL_MODELVIEW)

        glDepthFunc(GL_LEQUAL)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE)

        # set window callbacks
        glfw.set_mouse_button_callback(self.window, self.onMouseButton)
        glfw.set_key_callback(self.window, self.onKeyboard)
        glfw.set_window_size_callback(self.window, self.onSize)
        glfw.set_cursor_pos_callback(self.window, self.mouse_moved)

        # Get Filename
        if len(sys.argv) == 1:
            file = "bunny.obj"
        else:
            file = sys.argv[1]

        self.obj = file.split(".")[0]
        self.scene = Scene(self.width, self.height, file)
        self.exitNow = False
        self.animation = True

    def onMouseButton(self, win, button, action, mods):
        print("mouse button: ", win, button, action, mods)

        r = min(self.width, self.height) / 2.0
        if button == glfw.MOUSE_BUTTON_LEFT:
            if glfw.get_mouse_button(win, button) == glfw.PRESS:
                self.scene.doRotate = True
                self.scene.startPoint = self.scene.projectOnSphere(self.mouse_x, self.mouse_y, r)
            if glfw.get_mouse_button(win, button) == glfw.RELEASE:
                self.scene.doRotate = False
                self.scene.curOrientation = self.scene.curOrientation*self.scene.rotate(self.scene.angle, self.scene.axis)
                self.scene.angle = 0
        if button == glfw.MOUSE_BUTTON_MIDDLE:
            if glfw.get_mouse_button(win, button) == glfw.PRESS:
                self.scene.zooming = True
            if glfw.get_mouse_button(win, button) == glfw.RELEASE:
                self.scene.zooming = False
        if button == glfw.MOUSE_BUTTON_RIGHT:
            if glfw.get_mouse_button(win, button) == glfw.PRESS:
                self.scene.translation = True
            if glfw.get_mouse_button(win, button) == glfw.RELEASE:
                self.scene.translation = False

    def mouse_moved(self, win, x, y):
        self.mouse_x = x
        self.mouse_y = y
        sf = self.scene.scaleFactor

        if self.scene.doRotate:
            r = min(self.width, self.height) / 2.0
            movePoint = self.scene.projectOnSphere(x,y,r)
            self.scene.angle = np.arccos(np.dot(self.scene.startPoint, movePoint))
            self.scene.axis = np.cross(self.scene.startPoint, movePoint)

        if self.scene.zooming:
            if self.obj == "elephant":
                if y > 0 and sf > 0 and sf < 1.0:
                    self.scene.scaleFactor += 0.00001
                if y < 0 and sf >= 0.0001:
                    self.scene.scaleFactor -= 0.00001
            else:
                if y > 0 and sf > 0 and sf < 3:
                    self.scene.scaleFactor += 0.01
                if y < 0 and sf >= 0.5:
                    self.scene.scaleFactor -= 0.01

        if self.scene.translation:
            self.scene.newPosX = x / self.width
            self.scene.newPosY = y / self.height
            self.scene.startPoint = [x,y,0]

    def onKeyboard(self, win, key, scancode, action, mods):
        print("keyboard: ", win, key, scancode, action, mods)
        if action == glfw.PRESS:
            if key == glfw.KEY_ESCAPE:
                self.exitNow = True
            if key == glfw.KEY_V:
                self.scene.showVector = not self.scene.showVector
            if key == glfw.KEY_A:
                self.animation = not self.animation
            if key == glfw.KEY_H:
                self.scene.shadow = not self.scene.shadow
            if key == glfw.KEY_O:
                print("pressed O")
                if self.perspective:
                    self.ortho = True
                    self.perspective = False
                    glMatrixMode(GL_PROJECTION)
                    glLoadIdentity()
                    glOrtho((-1.5) * self.aspect, 1.5 * self.aspect, -1.5, 1.5, -10.0, 10.0)
                    glMatrixMode(GL_MODELVIEW)
            if key == glfw.KEY_P:
                print("pressed P")
                if self.ortho:
                    self.ortho = False
                    self.perspective = True
                    glMatrixMode(GL_PROJECTION)
                    glLoadIdentity()
                    gluPerspective(45, self.aspect, 0.1, 100)
                    gluLookAt(0, 0, 3, 0, 0, 0, 0, 1, 0)
                    glMatrixMode(GL_MODELVIEW)
            if key == glfw.KEY_B and action == glfw.PRESS:
                if (mods == glfw.MOD_SHIFT):
                    self.scene.setColor('blue')
                else:
                    self.scene.setBGColor('blue')
            if key == glfw.KEY_Z and action == glfw.PRESS:
                if(mods == glfw.MOD_SHIFT):
                    self.scene.setColor('yellow')
                else:
                    self.scene.setBGColor('yellow')
            if key == glfw.KEY_R and action == glfw.PRESS:
                if(mods == glfw.MOD_SHIFT):
                    self.scene.setColor('red')
                else:
                    self.scene.setBGColor('red')
            if key == glfw.KEY_W and action == glfw.PRESS:
                if(mods == glfw.MOD_SHIFT):
                    self.scene.setColor('white')
                else:
                    self.scene.setBGColor('white')
            if key == glfw.KEY_S and action == glfw.PRESS:
                if(mods == glfw.MOD_SHIFT):
                    self.scene.setColor('black')
                else:
                    self.scene.setBGColor('black')

    def onSize(self, win, width, height):
        print("onsize: ", win, width, height)
        if height == 0:
            height = 1
        glViewport(0,0,width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        if self.ortho:
            glOrtho((-1.5) * self.aspect, 1.5 * self.aspect, -1.5, 1.5, -10.0, 10.0)
        if self.perspective:
            gluPerspective(45, self.aspect, 0.1, 100)
            gluLookAt(0,0, 3, 0, 0, 0, 0, 1, 0)

        glMatrixMode(GL_MODELVIEW)
        self.width = width
        self.height = height
        self.aspect = width / float(height)
        #print("aspect", self.aspect)
        glViewport(0, 0, self.width, self.height)

    def run(self):
        # initializer timer
        glfw.set_time(0.0)
        t = 0.0
        while not glfw.window_should_close(self.window) and not self.exitNow:
            # update every x seconds
            currT = glfw.get_time()
            if currT - t > 1.0 / self.frame_rate:
                # update time
                t = currT
                # clear
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

                # render scene
                #if self.animation:
                    #self.scene.step()
                self.scene.render()

                glfw.swap_buffers(self.window)
                # Poll for and process events
                glfw.poll_events()
        # end
        glfw.terminate()

def main():
    print("Simple glfw render Window")
    rw = RenderWindow()
    rw.run()

if __name__ == '__main__':
    main()