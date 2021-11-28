
# GOAL: Code snake whilst keeping track of the snake using ONLY the head, tail-end, and bend points.
# World is a grid of some size and everything appears neatly on the grid and there is no such thing as a diagonal.

import sys
import pygame
import enum
from typing import List, Tuple
from collections import deque
from random import randint


# Directions for making the snake go
class Dir(enum.Enum):
    Up = 1
    Down = 2
    Left = 4
    Right = 5

    # Returns true if the given directions are opposites
    @classmethod
    def opposing(cls, dir1, dir2):
        if not type(dir1) is Dir or not type(dir2) is Dir:
            raise TypeError("Cannot compare things that aren't directions")
        return abs(dir2.value - dir1.value) == 1


# A thing which exists in the gameworld, which has a body defined by a series of points.
class Actor:
    def __init__(self, points: List[List[int]]):
        # we are very strict about that point list meeting our prerequisites.
        if not type(points) is list:
            raise TypeError("An actor's points must be in a list of type List[List[int]].")
        if not type(points[0]) is list:
            raise TypeError("An actor's points must be in a list of type List[List[int]].")
        if len(points[0]) > 2:
            raise TypeError("A point can contain only two coordinates - an x and a y.")
        if not type(points[0][0]) is int or not type(points[0][1]) is int:
            raise TypeError("A point's coordinates must be integers.")
        for x in range(len(points)-1):
            if not (points[x][0] == points[x+1][0] or points[x][1] == points[x+1][1]):
                raise TypeError("All of an actor's points must be aligned either vertically or horizontally with the "
                                "points adjacent to it in the list.")

        self.body = deque(points)

    # Returns true if this actor's body intersects with the given point.
    def intersects_with(self, point: List[int]) -> bool:
        # check prereqs
        if not type(point) is list:
            raise TypeError("A point must be in a list of integers.")
        if not type(point[0]) is int or not type(point[1]) is int:
            raise TypeError("A point's coordinates must be integers.")
        # check if this actor's body intersects the given point. can just check if the point is within the "rectangle"
        # made by every two points of the body, since there are no diagonals
        for x in range(len(self.body) - 1):
            if (min(self.body[x][0], self.body[x + 1][0]) <= point[0]) \
                    and (min(self.body[x][1], self.body[x + 1][1]) <= point[1]) \
                    and (max(self.body[x][0], self.body[x + 1][0]) >= point[0]) \
                    and (max(self.body[x][1], self.body[x + 1][1]) >= point[1]):
                return True
        return False


# A piece of food
class Food(Actor):
    def __init__(self, point: List[int]):
        super().__init__([point, point])
        self.eaten = False

    # If this food has been eaten, regenerate it in a new location which does not intersect with any of the obstacles.
    def regen(self, obstacles: List[Actor], gridwidth: int, gridheight: int):
        # prereq checks go here
        if not self.eaten:
            return
        # generate coords for food that are not anywhere the snake or walls are.
        valid = False
        newpos = 0
        while not valid:
            newpos = [randint(0, gridwidth-1), randint(0, gridheight-1)]
            valid = True
            for o in obstacles:
                if o.intersects_with(newpos):
                    valid = False
        self.body[0] = self.body[1] = newpos
        self.eaten = False


# A snake that can move, turn, eat, and hit things or itself. And also has a length.
class Snake(Actor):
    # CONSTRUCTORS
    def __init__(self, points):
        super().__init__(points)
        self.alive = True
        self.cur_dir = self.prev_dir = Dir.Up
        self.prev_tail_pos = self.body[-1].copy()
        # initial calculation of snake length, will be incremented in eat function as necessary from now on
        self.length = 0
        for i in range(len(self.body)-1):
            if self.body[i][0] == self.body[i + 1][0]:
                self.length += abs(self.body[i][1] - self.body[i + 1][1])
            elif self.body[i][1] == self.body[i + 1][1]:
                self.length += abs(self.body[i][0] - self.body[i + 1][0])

    # ACTIONS

    # called on player input to change snake direction
    def turn(self, new_dir: Dir):
        if not Dir.opposing(self.cur_dir, new_dir):
            self.cur_dir = new_dir

    # called every iteration of game loop to move snake.
    def move(self):
        # if there was a change in direction, insert a bend point just after the head.
        if self.cur_dir != self.prev_dir:
            self.body.insert(1, self.body[0].copy())
            self.prev_dir = self.cur_dir

        # move head in current direction
        if self.cur_dir == Dir.Up:
            self.body[0][1] -= 1
        elif self.cur_dir == Dir.Down:
            self.body[0][1] += 1
        elif self.cur_dir == Dir.Left:
            self.body[0][0] -= 1
        else:  # Right
            self.body[0][0] += 1

        # move tail towards the element preceding it in the list
        self.prev_tail_pos = self.body[-1].copy()
        if self.body[-1][1] > self.body[-2][1]:  # pre-tail is above, move up
            self.body[-1][1] -= 1
        elif self.body[-1][1] < self.body[-2][1]:  # pre-tail is below, move down
            self.body[-1][1] += 1
        elif self.body[-1][0] > self.body[-2][0]:  # pre-tail is to the left, move left
            self.body[-1][0] -= 1
        elif self.body[-1][0] < self.body[-2][0]:  # pre-tail is to the right, move right
            self.body[-1][0] += 1

        # if tail at same pos as preceding elt, pop the tail.
        if self.body[-1] == self.body[-2]:
            self.body.pop()

    # checks for end-of-game scenarios, ie collision with self or any of the walls.
    def collide(self, walls: List[Actor]):
        # body collision - all except segment right behind head, as that is impossible for the head to hit illegally.
        head = self.body.popleft()
        if self.intersects_with(head):
            self.alive = False
        self.body.appendleft(head)
        # wall collision
        for w in walls:
            if w.intersects_with(head):
                self.alive = False

    # increases length iff head is on top of a food.
    def eat(self, food: Food):
        if food.intersects_with(self.body[0]):
            self.body.append(self.prev_tail_pos)
            food.eaten = True
            self.length += 1


# For drawing a single point at the scale we want.
def draw_point(display, colour: Tuple[int, int, int], size_factor: int, point: List[int]):
    pygame.draw.rect(display, colour, (point[0] * size_factor, point[1] * size_factor, size_factor, size_factor))


# For drawing Actors at the scale we want
def draw_actor(display, colour: Tuple[int, int, int], size_factor: int, actor: Actor):
    for i in range(len(actor.body) - 1):
        left = min(actor.body[i][0], actor.body[i + 1][0]) * size_factor
        top = min(actor.body[i][1], actor.body[i + 1][1]) * size_factor
        width = abs(actor.body[i][0] - actor.body[i + 1][0]) * size_factor + size_factor
        height = abs(actor.body[i][1] - actor.body[i + 1][1]) * size_factor + size_factor
        pygame.draw.rect(display, colour, (left, top, width, height))


# plays the ding dang video game
def main():
    # init game logic vars
    grid_size = [20, 20]
    outerwall = Actor([[0, 0], [0, grid_size[1]-1], [grid_size[0]-1, grid_size[1]-1], [grid_size[0]-1, 0], [0, 0]])
    snake = Snake([[3, grid_size[0] - 4], [3, grid_size[0] - 3]])
    food = Food([10, 10])
    walls = [outerwall]
    actors = [food, snake, outerwall]

    # init pygame/drawing stuff
    sqr_size = 30
    pygame.init()
    DISPLAY = pygame.display.set_mode((grid_size[0] * sqr_size, grid_size[1] * sqr_size), 0, 32)
    FONT_SCORE = pygame.font.SysFont('Arial', 20, True)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN_HEAD = (0, 100, 0)
    GREEN_BODY = (0, 200, 0)
    RED = (200, 0, 0)

    # TODO figure out how to make the input and delay speed not feel like garbage to play
    while snake.alive:
        # get inputs
        dirr = 0
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evt.type == pygame.KEYDOWN:
                if evt.key == pygame.K_UP:
                    dirr = Dir.Up
                elif evt.key == pygame.K_DOWN:
                    dirr = Dir.Down
                elif evt.key == pygame.K_LEFT:
                    dirr = Dir.Left
                elif evt.key == pygame.K_RIGHT:
                    dirr = Dir.Right

        # do game logic
        if dirr != 0:
            snake.turn(dirr)
        snake.move()
        snake.collide(walls)
        snake.eat(food)
        food.regen(actors, grid_size[0], grid_size[1])

        # draw everything
        DISPLAY.fill(WHITE)
        for w in walls:
            draw_actor(DISPLAY, BLACK, sqr_size, w)
        draw_point(DISPLAY, RED, sqr_size, food.body[0])
        draw_actor(DISPLAY, GREEN_BODY, sqr_size, snake)
        draw_point(DISPLAY, GREEN_HEAD, sqr_size, snake.body[0])
        DISPLAY.blit(FONT_SCORE.render("Score: {0}".format(snake.length), False, WHITE), (10, 3))

        pygame.display.update()
        pygame.time.delay(250)

    # pause for a sec here
    pygame.time.delay(1000)
    pygame.quit()
    sys.exit()


main()
