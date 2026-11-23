import pygame
import random
import math

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Car Simulator")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)
small_font = pygame.font.SysFont(None, 28)     # smaller text for the damage label

 
ROAD = (60, 60, 60)
WHITE = (255, 255, 255)
YELLOW = (255, 220, 0)
RED = (200, 30, 30)
DARK_RED = (120, 10, 10)
BRIGHT_RED = (255, 0, 0)
GLOW_RED = (255, 160, 160)
BLUE = (40, 90, 200)
LIGHT_BLUE = (150, 210, 255)
BLACK = (20, 20, 20)
GRAY = (90, 90, 90)

# barriers
RAIL = (190, 190, 200)         # silver guardrail
POST = (70, 70, 75)            # dark metal post
ORANGE = (240, 120, 20)        # reflector on the post

# emergency light colors
AMBER = (255, 170, 0)
GLOW_AMBER = (255, 225, 130)

# city ground and river colors
GROUND = (130, 125, 115)       # paved ground
SIDEWALK = (175, 170, 160)
SHADOW = (100, 96, 88)         # building shadow
WATER = (50, 120, 200)
WAVE = (140, 195, 240)
BANK = (80, 80, 85)            # stone edge of the river

# building colors
ROOF_RED = (170, 60, 50)
ROOF_BROWN = (120, 80, 60)
ROOF_GRAY = (110, 110, 120)
CONCRETE = (160, 160, 165)

# colors for the other vehicles
CAR_COLORS = [BLUE, (150, 60, 190), (230, 230, 230), (230, 140, 30), (30, 170, 170)]
BUS_COLORS = [(230, 190, 30), (200, 50, 50), (40, 140, 90), (230, 230, 230)]
TRUCK_COLORS = [(200, 60, 40), (50, 110, 190), (240, 140, 20), (60, 130, 70)]
BIKE_COLORS = [(200, 30, 30), (40, 90, 200), (240, 140, 20), (60, 60, 70)]

# The road goes from x=200 to x=600
ROAD_LEFT = 200
ROAD_RIGHT = 600
ROAD_MIDDLE = 400      # the middle line. Left half = coming towards you, right half = same direction as you

# where the rivers are (each river is 50 wide)
LEFT_RIVER_X = 120
RIGHT_RIVER_X = 630

# The player's car: x, y, width, height
# starts in the right lane (the lane that goes the same way as you)
car = pygame.Rect(480, 500, 40, 70)
car_speed = 6

# Lists that store everything on the screen
obstacles = []   # other vehicles on the road (each one is a dictionary)
buildings = []   # buildings beside the road: [rectangle, color, kind]

speed = 0        # your car's speed in km/h (starts stopped)
max_speed = 200  # top speed
road_speed = 0   # how fast the road moves down (depends on your speed)
damage = 0       # car damage from 0 to 100 percent
line_y = 0       # position of the middle road line
score = 0
game_over = False


# makes a color darker or lighter
def darker(color, amount):
    return (max(0, color[0] - amount), max(0, color[1] - amount), max(0, color[2] - amount))


def lighter(color, amount):
    return (min(255, color[0] + amount), min(255, color[1] + amount), min(255, color[2] + amount))


def draw_player_car(braking):
    x = car.x
    y = car.y

    # wheels (black)
    pygame.draw.rect(screen, BLACK, (x - 3, y + 10, 6, 14))
    pygame.draw.rect(screen, BLACK, (x + 37, y + 10, 6, 14))
    pygame.draw.rect(screen, BLACK, (x - 3, y + 46, 6, 14))
    pygame.draw.rect(screen, BLACK, (x + 37, y + 46, 6, 14))

    # car body
    pygame.draw.rect(screen, RED, car, border_radius=10)

    # front windshield
    pygame.draw.rect(screen, LIGHT_BLUE, (x + 6, y + 20, 28, 12))

    # roof
    pygame.draw.rect(screen, DARK_RED, (x + 7, y + 32, 26, 14))

    # rear window
    pygame.draw.rect(screen, LIGHT_BLUE, (x + 6, y + 46, 28, 10))

    # headlights (front)
    pygame.draw.rect(screen, YELLOW, (x + 4, y + 2, 9, 5))
    pygame.draw.rect(screen, YELLOW, (x + 27, y + 2, 9, 5))

    # taillights (back)
    if braking or speed == 0:                           # ON when braking or stopped
        pygame.draw.rect(screen, GLOW_RED, (x + 2, y + 62, 13, 8))
        pygame.draw.rect(screen, GLOW_RED, (x + 25, y + 62, 13, 8))
        pygame.draw.rect(screen, BRIGHT_RED, (x + 4, y + 64, 9, 4))
        pygame.draw.rect(screen, BRIGHT_RED, (x + 27, y + 64, 9, 4))
    else:                                               # lights OFF while driving normally
        pygame.draw.rect(screen, DARK_RED, (x + 4, y + 64, 9, 4))
        pygame.draw.rect(screen, DARK_RED, (x + 27, y + 64, 9, 4))


# a normal car (same shape as yours, but any color)
def draw_other_car(rect, color):
    x = rect.x
    y = rect.y

    # wheels
    for wheel_y in (y + 10, y + 46):
        pygame.draw.rect(screen, BLACK, (x - 3, wheel_y, 6, 14))
        pygame.draw.rect(screen, BLACK, (x + 37, wheel_y, 6, 14))

    pygame.draw.rect(screen, color, rect, border_radius=10)                  # body
    pygame.draw.rect(screen, LIGHT_BLUE, (x + 6, y + 20, 28, 12))            # windshield
    pygame.draw.rect(screen, darker(color, 50), (x + 7, y + 32, 26, 14))     # roof
    pygame.draw.rect(screen, LIGHT_BLUE, (x + 6, y + 46, 28, 10))            # rear window

    # side mirrors
    pygame.draw.rect(screen, BLACK, (x - 4, y + 22, 4, 6))
    pygame.draw.rect(screen, BLACK, (x + 40, y + 22, 4, 6))

    # headlights and taillights
    pygame.draw.rect(screen, YELLOW, (x + 4, y + 2, 9, 5))
    pygame.draw.rect(screen, YELLOW, (x + 27, y + 2, 9, 5))
    pygame.draw.rect(screen, DARK_RED, (x + 4, y + 64, 9, 4))
    pygame.draw.rect(screen, DARK_RED, (x + 27, y + 64, 9, 4))


# a bus seen from above (long roof with air vents)
def draw_bus(rect, color):
    x = rect.x
    y = rect.y
    w = rect.width
    h = rect.height

    # wheels at the sides
    for wheel_y in (y + 24, y + h - 40):
        pygame.draw.rect(screen, BLACK, (x - 3, wheel_y, 6, 16))
        pygame.draw.rect(screen, BLACK, (x + w - 3, wheel_y, 6, 16))

    pygame.draw.rect(screen, color, rect, border_radius=8)                                  # body
    pygame.draw.rect(screen, LIGHT_BLUE, (x + 5, y + 5, w - 10, 14), border_radius=3)       # windshield
    pygame.draw.rect(screen, lighter(color, 35), (x + 5, y + 24, w - 10, h - 46), border_radius=4)   # roof
    for vent_y in range(y + 36, y + h - 34, 26):                                            # roof air vents
        pygame.draw.rect(screen, (215, 215, 220), (x + 14, vent_y, w - 28, 12))
    pygame.draw.rect(screen, (70, 100, 130), (x + 6, y + h - 17, w - 12, 9))                # rear window

    # side mirrors
    pygame.draw.rect(screen, BLACK, (x - 5, y + 12, 5, 9))
    pygame.draw.rect(screen, BLACK, (x + w, y + 12, 5, 9))

    # headlights and taillights
    pygame.draw.rect(screen, YELLOW, (x + 4, y + 1, 10, 4))
    pygame.draw.rect(screen, YELLOW, (x + w - 14, y + 1, 10, 4))
    pygame.draw.rect(screen, DARK_RED, (x + 4, y + h - 5, 10, 4))
    pygame.draw.rect(screen, DARK_RED, (x + w - 14, y + h - 5, 10, 4))


# a truck seen from above (small cab and a big cargo box)
def draw_truck(rect, color):
    x = rect.x
    y = rect.y
    w = rect.width
    h = rect.height
    cab_h = 38

    # wheels: one pair under the cab, two pairs at the back
    for wheel_y in (y + 10, y + h - 42, y + h - 22):
        pygame.draw.rect(screen, BLACK, (x - 3, wheel_y, 6, 14))
        pygame.draw.rect(screen, BLACK, (x + w - 3, wheel_y, 6, 14))

    # cargo box
    box = pygame.Rect(x, y + cab_h + 3, w, h - cab_h - 3)
    pygame.draw.rect(screen, (225, 225, 230), box, border_radius=3)
    pygame.draw.rect(screen, (150, 150, 155), box, 2)
    for rib_y in range(box.y + 12, box.bottom - 4, 14):                      # ribs on the box roof
        pygame.draw.line(screen, (190, 190, 195), (box.x + 4, rib_y), (box.right - 4, rib_y), 2)

    # cab
    pygame.draw.rect(screen, color, (x + 2, y, w - 4, cab_h), border_radius=8)
    pygame.draw.rect(screen, LIGHT_BLUE, (x + 8, y + 6, w - 16, 12), border_radius=3)   # windshield
    pygame.draw.rect(screen, darker(color, 50), (x + 8, y + 22, w - 16, 10))            # cab roof

    # side mirrors
    pygame.draw.rect(screen, BLACK, (x - 4, y + 8, 4, 8))
    pygame.draw.rect(screen, BLACK, (x + w, y + 8, 4, 8))

    # headlights and taillights
    pygame.draw.rect(screen, YELLOW, (x + 5, y + 1, 9, 4))
    pygame.draw.rect(screen, YELLOW, (x + w - 14, y + 1, 9, 4))
    pygame.draw.rect(screen, DARK_RED, (x + 3, y + h - 4, 10, 4))
    pygame.draw.rect(screen, DARK_RED, (x + w - 13, y + h - 4, 10, 4))


# a motorbike with a rider, seen from above
def draw_bike(rect, color):
    x = rect.x
    y = rect.y
    w = rect.width
    h = rect.height
    cx = rect.centerx

    pygame.draw.rect(screen, BLACK, (cx - 2, y, 4, 13), border_radius=2)             # front wheel
    pygame.draw.rect(screen, BLACK, (cx - 3, y + h - 15, 6, 15), border_radius=2)    # rear wheel
    pygame.draw.rect(screen, color, (cx - 4, y + 10, 8, h - 22), border_radius=3)    # fuel tank and seat
    pygame.draw.line(screen, BLACK, (x, y + 10), (x + w, y + 10), 3)                 # handlebar
    pygame.draw.rect(screen, (50, 50, 60), (x + 2, y + 14, w - 4, 11), border_radius=4)   # rider's jacket
    pygame.draw.circle(screen, WHITE, (cx, y + 21), 5)                               # helmet

    pygame.draw.rect(screen, YELLOW, (cx - 2, y - 2, 4, 3))                          # headlight
    pygame.draw.rect(screen, DARK_RED, (cx - 2, y + h - 2, 4, 3))                    # taillight


# draws one vehicle by its kind (car, bus, truck or bike) at the given rectangle
def draw_kind(vehicle, rect):
    if vehicle["kind"] == "car":
        draw_other_car(rect, vehicle["color"])
    elif vehicle["kind"] == "bus":
        draw_bus(rect, vehicle["color"])
    elif vehicle["kind"] == "truck":
        draw_truck(rect, vehicle["color"])
    else:
        draw_bike(rect, vehicle["color"])


# vehicles coming towards you are drawn upside down (their front faces you)
def draw_vehicle(vehicle):
    global screen
    rect = vehicle["rect"]

    if vehicle["oncoming"]:
        # 1. draw the vehicle on a small empty picture
        real_screen = screen
        picture = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
        screen = picture
        draw_kind(vehicle, pygame.Rect(10, 10, rect.width, rect.height))
        screen = real_screen

        # 2. turn the picture upside down and put it on the screen
        turned = pygame.transform.rotate(picture, 180)
        screen.blit(turned, (rect.x - 10, rect.y - 10))
    else:
        draw_kind(vehicle, rect)

    if vehicle["crashed"]:
        draw_hazard_lights(rect)


# blinking emergency lights of a crashed vehicle
def draw_hazard_lights(rect):
    if (pygame.time.get_ticks() // 300) % 2 != 0:      # lights are off in this half of the blink
        return

    if rect.width < 30:                                # a bike has small lights
        spots = [(rect.x - 3, rect.y + 10), (rect.right + 3, rect.y + 10),
                 (rect.x + 3, rect.bottom - 3), (rect.right - 3, rect.bottom - 3)]
        for spot in spots:
            pygame.draw.circle(screen, GLOW_AMBER, spot, 6)
            pygame.draw.circle(screen, AMBER, spot, 3)
    else:                                              # cars, buses and trucks: four corners
        corners = [(rect.x - 3, rect.y + 2), (rect.right - 5, rect.y + 2),
                   (rect.x - 3, rect.bottom - 9), (rect.right - 5, rect.bottom - 9)]
        for corner in corners:
            pygame.draw.rect(screen, GLOW_AMBER, (corner[0] - 2, corner[1] - 2, 12, 11))
            pygame.draw.rect(screen, AMBER, (corner[0], corner[1], 8, 7))


# after a crash, move the other vehicle to the side of your car
# so you can drive forward and pass it
def push_aside(rect):
    if rect.centerx < car.centerx:
        rect.right = car.left - 5
    else:
        rect.left = car.right + 5

    # if that pushed it off the road, put it on the other side
    if rect.left < ROAD_LEFT:
        rect.left = car.right + 5
    if rect.right > ROAD_RIGHT:
        rect.right = car.left - 5


# draws a river with moving waves
def draw_river(x):
    pygame.draw.rect(screen, WATER, (x, 0, 50, 600))
    for y in range(-80, 600, 80):
        wave_y = y + line_y
        pygame.draw.line(screen, WAVE, (x + 10, wave_y), (x + 24, wave_y), 2)
        pygame.draw.line(screen, WAVE, (x + 26, wave_y + 40), (x + 40, wave_y + 40), 2)
    pygame.draw.rect(screen, BANK, (x - 4, 0, 4, 600))     # left bank
    pygame.draw.rect(screen, BANK, (x + 50, 0, 4, 600))    # right bank


# draws a building as seen from above (we see the roof)
def draw_building(rect, color, kind):
    x = rect.x
    y = rect.y
    w = rect.width
    h = rect.height

    # shadow on the ground
    pygame.draw.rect(screen, SHADOW, (x + 8, y + 8, w, h))

    if kind == "house":
        # pitched roof: one side lighter, one side darker
        light = (min(255, color[0] + 35), min(255, color[1] + 35), min(255, color[2] + 35))
        dark = (max(0, color[0] - 35), max(0, color[1] - 35), max(0, color[2] - 35))
        half = w // 2
        pygame.draw.rect(screen, light, (x, y, half, h))
        pygame.draw.rect(screen, dark, (x + half, y, w - half, h))

        # roof tile lines
        for ly in range(y + 10, y + h, 10):
            pygame.draw.line(screen, color, (x, ly), (x + w, ly), 1)

        # ridge line in the middle and outline
        pygame.draw.line(screen, BLACK, (x + half, y), (x + half, y + h), 3)
        pygame.draw.rect(screen, BLACK, rect, 2)

        # chimney
        pygame.draw.rect(screen, (90, 60, 50), (x + half + 8, y + 12, 10, 12))
    else:
        # flat roof of a tall building
        pygame.draw.rect(screen, CONCRETE, rect)
        pygame.draw.rect(screen, (110, 110, 115), rect, 4)           # edge of the roof

        pygame.draw.rect(screen, (95, 95, 100), (x + 10, y + 10, 22, 22))   # stair box

        # two air conditioner units with fans
        for i in range(2):
            pygame.draw.rect(screen, (200, 200, 205), (x + w - 30, y + 12 + i * 40, 18, 22))
            pygame.draw.circle(screen, (90, 90, 95), (x + w - 21, y + 23 + i * 40), 6)

        # skylight window
        pygame.draw.rect(screen, LIGHT_BLUE, (x + 12, y + h - 40, 30, 22))


running = True
while running:

    # 1. Check if the player closed the window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if not game_over:
        # Up arrow speeds up, Down arrow slows down
        if keys[pygame.K_UP]:
            speed += 0.5
        if keys[pygame.K_DOWN]:
            speed -= 1.5

        # keep the speed between 0 and max_speed
        if speed < 0:
            speed = 0
        if speed > max_speed:
            speed = max_speed

        # the road moves according to your speed (0 when stopped)
        road_speed = math.ceil(speed / 20)

        # 2. Move the car left and right (only when the car is moving)
        if speed > 0:
            if keys[pygame.K_LEFT]:
                car.x -= car_speed
            if keys[pygame.K_RIGHT]:
                car.x += car_speed

        # Keep the car on the road
        # touching the edge of the road damages the car
        if car.left < ROAD_LEFT:
            car.left = ROAD_LEFT
            damage += 0.3
        if car.right > ROAD_RIGHT:
            car.right = ROAD_RIGHT
            damage += 0.3

        # 3. Create new vehicles and buildings (only while moving)
        # CHANGED: half the traffic (1 in 300 chance, and never more than 2 at once)
        if speed > 0 and random.randint(1, 300) == 1 and len(obstacles) < 2:
            kind = random.choice(["car", "car", "bus", "truck", "bike"])   # cars are more common
            if kind == "car":
                w = 40
                h = 70
                color = random.choice(CAR_COLORS)
                forward_speed = random.randint(1, 4)
            elif kind == "bus":
                w = 50
                h = 130
                color = random.choice(BUS_COLORS)
                forward_speed = random.randint(1, 3)
            elif kind == "truck":
                w = 50
                h = 120
                color = random.choice(TRUCK_COLORS)
                forward_speed = random.randint(1, 3)
            else:
                w = 18
                h = 42
                color = random.choice(BIKE_COLORS)
                forward_speed = random.randint(2, 4)

            # half of the vehicles come towards you in the left lane
            oncoming = random.choice([True, False])
            if oncoming:
                x = random.randint(ROAD_LEFT, ROAD_MIDDLE - w)     # left half of the road
            else:
                x = random.randint(ROAD_MIDDLE, ROAD_RIGHT - w)    # right half of the road

            obstacles.append({"rect": pygame.Rect(x, -h, w, h), "speed": forward_speed,
                              "crashed": False, "kind": kind, "color": color,
                              "oncoming": oncoming, "passed": False})

        # create buildings beside the road
        if speed > 0 and random.randint(1, 50) == 1:
            kind = random.choice(["house", "tower"])
            if kind == "house":
                w = random.randint(60, 90)
                h = random.randint(70, 100)
                color = random.choice([ROOF_RED, ROOF_BROWN, ROOF_GRAY])
            else:
                w = random.randint(70, 100)
                h = random.randint(120, 180)
                color = CONCRETE

            if random.randint(1, 2) == 1:
                x = random.randint(5, 110 - w)     # left side, before the river
            else:
                x = random.randint(690, 795 - w)   # right side, after the river
            new_building = pygame.Rect(x, -h, w, h)

            # only add it if it does not touch another building
            free = True
            for b in buildings:
                if new_building.inflate(20, 20).colliderect(b[0]):
                    free = False
            if free:
                buildings.append([new_building, color, kind])

        # 4. Move vehicles and buildings down the screen
        for vehicle in obstacles[:]:
            rect = vehicle["rect"]
            if vehicle["crashed"]:
                rect.y += road_speed                       # a crashed vehicle stands still on the road
            elif vehicle["oncoming"]:
                rect.y += road_speed + vehicle["speed"]    # coming towards you, so it moves down faster
            else:
                rect.y += road_speed - vehicle["speed"]    # same direction, goes straight at its own speed

            if rect.y > 600 or rect.y < -150:              # remove vehicles that are off screen
                obstacles.remove(vehicle)
            elif car.colliderect(rect):
                if vehicle["crashed"]:
                    damage += 0.3                          # scraping a vehicle that is already crashed
                else:
                    damage += 20                           # first hit: big damage
                    vehicle["crashed"] = True              # the vehicle stops and turns on its emergency lights
                    speed = 0                              # your car stops too
                    push_aside(rect)                       # so you can drive past it
            elif speed > 0 and not vehicle["crashed"] and not vehicle["passed"] and rect.y > car.bottom:
                # the vehicle is now completely behind your car, so you passed it
                vehicle["passed"] = True
                score += 10

        for b in buildings[:]:                 # move buildings with the road
            b[0].y += road_speed
            if b[0].y > 600:
                buildings.remove(b)

        # the car keeps running until the damage reaches 100 percent
        if damage >= 100:
            damage = 100
            game_over = True

        # 5. Move the middle line
        # the score does not grow by distance, only when you pass a vehicle
        line_y = (line_y + road_speed) % 80

    # 6. Draw everything
    screen.fill(GROUND)

    pygame.draw.rect(screen, SIDEWALK, (170, 0, 30, 600))  # sidewalks next to the road
    pygame.draw.rect(screen, SIDEWALK, (600, 0, 30, 600))

    draw_river(LEFT_RIVER_X)                               # rivers beside the road
    draw_river(RIGHT_RIVER_X)

    for b in buildings:                                    # buildings
        draw_building(b[0], b[1], b[2])

    pygame.draw.rect(screen, ROAD, (ROAD_LEFT, 0, 400, 600))

    # guardrail barriers on both sides of the road
    pygame.draw.rect(screen, RAIL, (ROAD_LEFT - 8, 0, 8, 600))
    pygame.draw.rect(screen, GRAY, (ROAD_LEFT - 8, 0, 8, 600), 1)
    pygame.draw.rect(screen, RAIL, (ROAD_RIGHT, 0, 8, 600))
    pygame.draw.rect(screen, GRAY, (ROAD_RIGHT, 0, 8, 600), 1)

    for y in range(-80, 600, 80):              # posts with orange reflectors
        post_y = y + line_y
        pygame.draw.rect(screen, POST, (ROAD_LEFT - 13, post_y, 13, 7))
        pygame.draw.rect(screen, ORANGE, (ROAD_LEFT - 13, post_y + 1, 4, 5))
        pygame.draw.rect(screen, POST, (ROAD_RIGHT, post_y, 13, 7))
        pygame.draw.rect(screen, ORANGE, (ROAD_RIGHT + 9, post_y + 1, 4, 5))

    # two solid yellow lines in the middle separate the two directions
    pygame.draw.rect(screen, YELLOW, (ROAD_MIDDLE - 6, 0, 4, 600))
    pygame.draw.rect(screen, YELLOW, (ROAD_MIDDLE + 2, 0, 4, 600))

    for vehicle in obstacles:                  # draw cars, buses, trucks and bikes
        draw_vehicle(vehicle)

    draw_player_car(keys[pygame.K_DOWN])

    text = font.render("Score: " + str(score), True, WHITE)
    screen.blit(text, (10, 10))

    # show the speed in the top right corner
    speed_text = font.render(str(int(speed)) + " km/h", True, WHITE)
    screen.blit(speed_text, (800 - speed_text.get_width() - 10, 10))

    # damage bar under the speed meter
    damage_text = small_font.render("Damage: " + str(int(damage)) + "%", True, WHITE)
    screen.blit(damage_text, (800 - damage_text.get_width() - 10, 45))
    pygame.draw.rect(screen, GRAY, (640, 70, 150, 16))                  # empty bar
    pygame.draw.rect(screen, RED, (640, 70, int(damage * 1.5), 16))     # filled part
    pygame.draw.rect(screen, WHITE, (640, 70, 150, 16), 2)              # border

    if game_over:
        text = font.render("GAME OVER - Press R to restart", True, WHITE)
        screen.blit(text, (180, 280))
        if keys[pygame.K_r]:                   # restart the game
            obstacles = []
            buildings = []
            score = 0
            speed = 0                          # start stopped again
            road_speed = 0
            damage = 0                         # repair the car
            car.x = 480                        # back to the right lane
            game_over = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()