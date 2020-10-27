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


# setup for accelerometer

i2c = busio.I2C(board.SCL, board.SDA)
int1 = digitalio.DigitalInOut(board.ACCELEROMETER_INTERRUPT)
lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19, int1=int1)


# Display setup

matrix = Matrix()
display = matrix.display
#network = Network(status_neopixel=board.NEOPIXEL, debug=False)

# Buttons setup

button_a = digitalio.DigitalInOut(board.BUTTON_UP)
button_a.direction = digitalio.Direction.INPUT
button_a.pull = digitalio.Pull.UP

button_b = digitalio.DigitalInOut(board.BUTTON_DOWN)
button_b.direction = digitalio.Direction.INPUT
button_b.pull = digitalio.Pull.UP


def get_angle():
    x, y, z = lis3dh.acceleration
    angle = math.degrees(math.atan2(y,x)) + 90.0
    if angle < 0:
        angle = 360 + angle
    #print(angle, abs(z))
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
    global goal_position
    for i in range(0,10):
        for j in range(0,5):
            maze[i,j] = 1
            time.sleep(0.01)

    goal_group.hidden = True

    start_pos, goal_position = generate_maze(start_x=x, start_y=y)
    goal_tilegrid.x = goal_position[0]*6 + 3
    goal_tilegrid.y = goal_position[1]*6 + 2
    goal_group.hidden = False


    return True


def generate_maze(start_x=None, start_y=None):
    global max_depth, goal_x, goal_y, vis, solution_path
    w = 10
    h = 5
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
                if xx > 9 or yy > 4: continue
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
                    print("moving to", xx, yy)
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
                print("moving back to", x, y)

    if start_x == None:
        start_x = randint(0,9)

    if start_y == None:
        start_y = randint(0,4)
    start = (start_x, start_y)
    walk(start_x, start_y, 1)
    goal = (goal_x, goal_y)
    print(start, goal, max_depth)
    return start, goal

def change_color():
    global ball_palette, curent_theme, color_themes, rect1, rect2, rect3
    print("color change trigered !")
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

# graphical init

# Maze
maze_sprite_sheet, maze_palette = adafruit_imageload.load("/Maze_tiles_matrix.bmp",
                                                bitmap=displayio.Bitmap,
                                                palette=displayio.Palette)

maze = displayio.TileGrid(maze_sprite_sheet, pixel_shader=maze_palette,
                            width = 10,
                            height = 5,
                            tile_width = 6,
                            tile_height = 6,
                            default_tile = 1)

maze_group = displayio.Group()
maze_group.append(maze)
maze_group.x = 3

# Walls

rect1 = Rect(0, 0, 3, 32, fill=0xdb4242)
rect2 = Rect(3, 30, 60, 2, fill=0xdb4242)
rect3 = Rect(63, 0, 1, 32, fill=0xdb4242)

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



group = displayio.Group(max_size=6)
group.append(maze_group)
group.append(rect1)
group.append(rect2)
group.append(rect3)
group.append(ball_group)
group.append(goal_group)

display.show(group)

print("Maze time! Find the exit...")

solution_path = []
start_position, goal_position = generate_maze()

# Start position for the ball

ball.x = start_position[0]*6
ball.y = start_position[1]*6 + 3
ball_group.hidden = False

# Goal position

goal_tilegrid.x = goal_position[0]*6 + 3
goal_tilegrid.y = goal_position[1]*6 + 2
goal_group.hidden = False


# buttons
but_a = True
but_b = True

# Demo mode (toggled by the UP button)

demo = False

# Color themes

curent_theme = 0
# ball, walls, goal center, goal periph
# original, dark
color_themes = [[0x139913,0xdb4242,0xf364bd,0x3fc2ea],[0x0000CC,0x400040,0xC00000,0x400000]]



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


    # Ball collision with goal.
    if collision(ball, goal_tilegrid):
        ball.x = goal_tilegrid.x+1
        ball.y = goal_tilegrid.y+1
        reinit_maze(grid_x[0], grid_y[0])
        continue

    if demo:
        if len(solution_path) == 0:
            ball.x = goal_tilegrid.x+1
            ball.y = goal_tilegrid.y+1
            reinit_maze(goal_position[0], goal_position[1])
            continue
        print(solution_path)
        print(4 + solution_path[0][0] * 6)
        print(3 + solution_path[0][1] * 6)
        ball.x = 4 + solution_path[0][0] * 6
        ball.y = 3 + solution_path[0][1] * 6
        solution_path.pop(0)
        time.sleep(0.5)
        continue

    # accelerometer values
    angle, z = get_angle()
    grid_x = []
    grid_y = []

    if (ball.x-3)// 6 == (ball.x-2)// 6:
        grid_x = [(ball.x-3)// 6]
    else:
        grid_x = [(ball.x-3)// 6, (ball.x-2)// 6]
    if ball.y // 6 == (ball.y+2) // 6:
        grid_y = [ball.y // 6]
    else:
        grid_y = [ball.y // 6, (ball.y+2) // 6]



    # moving the ball

    # Set speed relative to tilt
    if z > 9.67:
        # print ("do nothing, z =", z)
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
    local_x = ball.x - 3 - grid_x[0]*6
    local_y = ball.y - grid_y[0]*6
    # North distance
    if maze[grid_x[0],grid_y[0]] < 2:
        distances[0] = local_y - 2
    else:
        if maze[grid_x[0],grid_y[0]] == 2:
            if local_x > 4:
                distances[0] = local_y - 2
            else:
                distances[0] = 12
        else:
            distances[0] = 12

    # East distance
    if maze[grid_x[0],grid_y[0]] % 2 == 1:
        distances[1] =  6 - local_x - 4
    else:
        if maze[grid_x[0],grid_y[0]] == 2:
            if local_y < 2:
                distances[1] =  6 - local_x - 4
            else:
                distances[1] = 12
        else:
            distances[1] = 12

    # South distance
    if grid_y[0] < 4:
        if local_x > 4:
            distances[2] = 4 - local_y
        else:
            if  maze[grid_x[0],grid_y[0]+1] < 2:
                distances[2] = 4 - local_y
            else :
                distances[2] = 12
    else:
        distances[2] = 4 - local_y
    # West distance
    if grid_x[0] > 0:
        if local_y < 2:
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
