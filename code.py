############
############
##
## Maze for 64x32 RGB matrix and matrixportal M4 from Adafruit
##
## By Marius_450
## Based on https://github.com/Marius-450/Maze_CP
##
############
############

# CONFIG VARS ############
##########################

# inactivity in secs before automatically activating demo mode.
inactivity_limit = 300

# sensitivity (smaller means more sensitive), only used for detection of inactivity.
sensitivity = 150

# color theme to use first
curent_theme = 0

# each theme have colors for : ball, walls, goal center, goal periph
# original blue, dark, pink
color_themes = [[0x139913,0x108ec4,0xf364bd,0x000040],[0x0000CC,0x400040,0xC00000,0x400000],[0x139913,0xdb4242,0xf364bd,0x3fc2ea]]

demo = False

##########################

# libs

import time
import math
from random import randint
import board
import displayio
import adafruit_display_text.label
from adafruit_display_shapes.rect import Rect
from adafruit_matrixportal.matrix import Matrix
import adafruit_imageload

import busio
import digitalio
import adafruit_lis3dh

# accelerometer setup

i2c = busio.I2C(board.SCL, board.SDA)
int1 = digitalio.DigitalInOut(board.ACCELEROMETER_INTERRUPT)
lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19, int1=int1)

# Display setup

WIDTH = 64
WIDTH_GRID = 12
HEIGHT = 32 # 64
HEIGHT_GRID = 6 # 12

matrix = Matrix(width=WIDTH, height=HEIGHT)
display = matrix.display

# Buttons setup

button_a = digitalio.DigitalInOut(board.BUTTON_UP)
button_a.direction = digitalio.Direction.INPUT
button_a.pull = digitalio.Pull.UP

button_b = digitalio.DigitalInOut(board.BUTTON_DOWN)
button_b.direction = digitalio.Direction.INPUT
button_b.pull = digitalio.Pull.UP

# functions

def get_angle():
    global acc_values, last_activity, sensitivity
    x, y, z = lis3dh.acceleration
    angle = math.degrees(math.atan2(y,x)) + 90.0
    if angle < 0:
        angle = 360 + angle
    #print(angle, abs(z))
    if  -sensitivity < math.trunc(x*100) - acc_values[0] < sensitivity and -sensitivity < math.trunc(y*100) - acc_values[1] < sensitivity and -sensitivity < math.trunc(z*100) - acc_values[2] < sensitivity:
        # no change
        # print("DEBUG : no movement", acc_values, time.monotonic()-last_activity, "s")
        pass
    else:
        acc_values = [math.trunc(x*100),math.trunc(y*100),math.trunc(z*100)]
        if time.monotonic() - last_activity > 30:
            print("movement after", time.monotonic() - last_activity, "s of inactivity")
        last_activity = time.monotonic()
    return (angle, abs(z))

def shuffle(x):
    """Shuffle list x in place, and return None.
    From Cpython source code
    """
    for i in reversed(range(1, len(x))):
        # pick an element in x[:i+1] with which to exchange x[i]
        j = randint(0,i)
        x[i], x[j] = x[j], x[i]

def collision(a, b):
    # 2.2 pixels distance minimum for collision (2.2^2 = 4.84)
    if abs(a.x-b.x)**2 + abs(a.y-b.y)**2 < 4.84:
        # collision
        # print("COLLISION !!!")
        return True
    else:
        return False


def reinit_maze(x, y):
    global goal_position, start_position
    for i in range(0,WIDTH_GRID):
        for j in range(0,HEIGHT_GRID):
            maze[i,j] = 1
            time.sleep(0.01)
    goal_group.hidden = True
    start_position, goal_position = generate_maze(start_x=x, start_y=y)
    goal_tilegrid.x = goal_position[0]*5 + 3
    goal_tilegrid.y = goal_position[1]*5 + 1
    ball.x = start_position[0]*5 + 4
    ball.y = start_position[1]*5 + 2
    goal_group.hidden = False
    return True


def generate_maze(start_x=None, start_y=None):
    global max_depth, goal_x, goal_y, vis, solution_path
    w = WIDTH_GRID
    h = HEIGHT_GRID
    max_depth = 0
    goal_x = 0
    goal_y = 0
    # visited cells
    vis = [[0] * w + [1] for _ in range(h)] + [[1] * (w + 1)]
    path = []
    def walk(x, y, depth):
        global max_depth, goal_x, goal_y, solution_path
        path.append((x,y))
        while len(path)>0:
            move = False
            if depth > max_depth:
                max_depth = depth
                goal_x = x
                goal_y = y
                solution_path = path.copy()
            if vis[y][x] != 1 :
                path.append((x,y))
                vis[y][x] = 1
            d = [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]
            shuffle(d)
            for (xx, yy) in d:
                if xx > w-1 or yy > h-1: continue
                if vis[yy][xx]: continue
                move = True
                if xx == x:
                    # vertical move
                    if yy > y:
                        # going south
                        maze[x,yy] = 3
                    else:
                        # going north
                        if maze[x,y] == 1:
                            maze[x,y] = 3
                        else:
                            maze[x,y] = 2
                if yy == y:
                    # horizontal move
                    if xx > x:
                        # going east
                        if maze[x,y] == 1:
                            maze[x,y] = 0
                        else:
                            maze[x,y] = 2
                    else:
                        #going west
                        maze[xx,y] = 0
                if move:
                    # print("moving to", xx, yy)
                    x,y,depth = (xx, yy, depth + 1)
                    time.sleep(0.05)
                    break

            if move:
                continue
            else:
                path.pop()
                if len(path) < 1:
                    print("maze completed")
                    break
                x,y = path[-1]
                depth -= 1
                #print("moving back to", x, y)

    if start_x == None:
        start_x = randint(0,w-1)

    if start_y == None:
        start_y = randint(0,h-1)
    start = (start_x, start_y)
    walk(start_x, start_y, 1)
    goal = (goal_x, goal_y)
    print(start, goal, max_depth)
    return start, goal

def change_color(n=None):
    global ball_palette, curent_theme, color_themes, rect1, rect2, rect3
    if n is not None:
        curent_theme = n
    else:
        curent_theme += 1
    if curent_theme >= len(color_themes):
        curent_theme = 0
    ball_palette[0] = color_themes[curent_theme][0]
    maze_palette[1] = color_themes[curent_theme][1]
    rect1.fill = color_themes[curent_theme][1]
    rect2.fill = color_themes[curent_theme][1]
    rect3.fill = color_themes[curent_theme][1]
    goal_palette[0] = color_themes[curent_theme][2]
    goal_palette[1] = color_themes[curent_theme][3]
    time.sleep(0.5)

# graphical setup

# Maze
maze_sprite_sheet, maze_palette = adafruit_imageload.load("/Maze_tiles_matrix_5x5.bmp",
                                                bitmap=displayio.Bitmap,
                                                palette=displayio.Palette)
maze = displayio.TileGrid(maze_sprite_sheet, pixel_shader=maze_palette,
                            width = WIDTH_GRID,
                            height = HEIGHT_GRID,
                            tile_width = 5,
                            tile_height = 5,
                            default_tile = 1)
maze_group = displayio.Group()
maze_group.append(maze)
maze_group.x = 3

# Outer walls
H_OFF = HEIGHT - (HEIGHT_GRID * 5)
rect1 = Rect(0, 0, 3, HEIGHT, fill=maze_palette[1])
rect2 = Rect(3, HEIGHT-H_OFF, WIDTH-4, H_OFF, fill=maze_palette[1])
rect3 = Rect(WIDTH-1, 0, 1, HEIGHT, fill=maze_palette[1])

# Goal

goal_sprite_sheet, goal_palette = adafruit_imageload.load("/goal.bmp",
                                                bitmap=displayio.Bitmap,
                                                palette=displayio.Palette)
goal_tilegrid = displayio.TileGrid(goal_sprite_sheet, pixel_shader=goal_palette,
                            width = 1,
                            height = 1,
                            tile_width = 4,
                            tile_height = 4 )
goal_group = displayio.Group()
goal_group.append(goal_tilegrid)
goal_group.hidden = True

ball_sprite_sheet, ball_palette = adafruit_imageload.load("/ball_matrix.bmp",
                                                bitmap=displayio.Bitmap,
                                                palette=displayio.Palette)
ball = displayio.TileGrid(ball_sprite_sheet, pixel_shader=ball_palette,
                            width = 1,
                            height = 1,
                            tile_width = 2,
                            tile_height = 2 )

ball_group = displayio.Group()
ball_group.append(ball)
ball_group.hidden = True

group = displayio.Group()
group.append(maze_group)
group.append(rect1)
group.append(rect2)
group.append(rect3)
group.append(goal_group)
group.append(ball_group)

display.show(group)

print("Maze time! Find the exit...")

solution_path = []
start_position, goal_position = generate_maze()

# Start position for the ball

ball.x = start_position[0]*5 + 4
ball.y = start_position[1]*5 + 2
ball_group.hidden = False

# Goal position

goal_tilegrid.x = goal_position[0]*5 + 3
goal_tilegrid.y = goal_position[1]*5 + 1
goal_group.hidden = False

# buttons tracking vars
but_a = True
but_b = True

# Variables tracking inactivity

last_activity = time.monotonic()
acc_values = [0,0,0]

# Apply color theme

change_color(curent_theme)

while True:
    # buttons press check
    if button_a.value == False and but_a:
        #but_a pressed
        but_a = False

    if button_a.value and but_a == False:
        #but_a released
        but_a = True
        if demo:
            demo = False
            print("demo mode deactivated")
        else:
            demo = True
            print("demo mode activated")

    if button_b.value == False and but_b:
        #but_b pressed
        but_b = False

    if button_b.value and but_b == False:
        #but_b released
        but_b = True
        change_color()

    if demo == False and time.monotonic() - last_activity > inactivity_limit:
        print("demo mode activated due to inactivity")
        demo = True

    # Ball collision with goal.
    if collision(ball, goal_tilegrid):
        ball.x = goal_tilegrid.x+1
        ball.y = goal_tilegrid.y+1
        reinit_maze(goal_position[0], goal_position[1])
        goal_group.hidden = False
        continue

    # Demo mode
    if demo:
        get_angle()
        if time.monotonic() - last_activity < 5:
            print("movement detected. demo mode deactivated")
            demo = False
            continue
        if len(solution_path) == 0:
            ball.x = goal_tilegrid.x+1
            ball.y = goal_tilegrid.y+1
            reinit_maze(goal_position[0], goal_position[1])
            goal_group.hidden = False
            continue
        ball.x = 4 + solution_path[0][0] * 5
        ball.y = 2 + solution_path[0][1] * 5
        solution_path.pop(0)
        time.sleep(0.5)
        continue

    # accelerometer values
    angle, z = get_angle()
    grid_x = []
    grid_y = []

    if (ball.x-3)// 5 == (ball.x-2)// 5:
        grid_x = [(ball.x-3)// 5]
    else:
        grid_x = [(ball.x-3)// 5, (ball.x-2)// 5]
    if ball.y // 5 == (ball.y+1) // 5:
        grid_y = [ball.y // 5]
    else:
        grid_y = [ball.y // 5, (ball.y+1) // 5]



    # moving the ball

    # Set speed relative to tilt
    if z > 9.67:
        delta_x = 0
        delta_y = 0
    else:
        if z > 8:
            speed = 1
        else :
            speed = 1.5
        delta_x = (0.5 + speed) * math.sin(math.radians(angle))
        delta_y = (-0.5 - speed) * math.cos(math.radians(angle))

    # collision detection with walls

    # distances = [N, E, S, W] in pixels
    distances = [0,0,0,0]
    # relative position of the ball in the cell
    local_x = ball.x - 3 - grid_x[0]*5
    local_y = ball.y - grid_y[0]*5
    # North distance
    if maze[grid_x[0],grid_y[0]] < 2:
        distances[0] = local_y - 1
    else:
        if maze[grid_x[0],grid_y[0]] == 2:
            if local_x > 4:
                distances[0] = local_y - 1
            else:
                distances[0] = 12
        else:
            distances[0] = 12

    # East distance
    if maze[grid_x[0],grid_y[0]] % 2 == 1:
        distances[1] =  5 - local_x - 3
    else:
        if maze[grid_x[0],grid_y[0]] == 2:
            if local_y < 1:
                distances[1] =  5 - local_x - 3
                #distances[1] = 12
            else:
                distances[1] = 12
        else:
            distances[1] = 12

    # South distance
    if grid_y[0] < HEIGHT_GRID-1:
        if local_x > 4:
            distances[2] = 3 - local_y
        else:
            if  maze[grid_x[0],grid_y[0]+1] < 2:
                distances[2] = 3 - local_y
            else :
                distances[2] = 12
    else:
        distances[2] = 3 - local_y
    # West distance
    if grid_x[0] > 0:
        if local_y < 1:
            distances[3] = local_x
        else:
            if maze[grid_x[0]-1,grid_y[0]] % 2 == 1:
                distances[3] = local_x
            else:
                distances[3] = 12
    else:
        distances[3] = local_x

    # if planned move is greater than available space, replace delta by distances[]
    if math.ceil(delta_x) > distances[1]:
        delta_x = distances[1]
    if math.ceil(delta_x) < -distances[3]:
        delta_x = -distances[3]
    if math.ceil(delta_y) > distances[2]:
        delta_y = distances[2]
    if math.ceil(delta_y) < -distances[0]:
        delta_y = -distances[0]

    ball.x += math.ceil(delta_x)
    ball.y += math.ceil(delta_y)
    time.sleep(0.04)
