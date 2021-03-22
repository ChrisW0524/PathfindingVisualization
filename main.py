import pygame
import math
from queue import PriorityQueue
import sys

# Initialize pygame variables -----------------------------------------------------------------------------------------#
pygame.init()
clock = pygame.time.Clock()
WINDOW_SIZE = [800, 1000]
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Pathfinding visualization")

# Initialize colors (colors control state of cell) --------------------------------------------------------------------#
RED = (255, 0, 0)  # Closed node
GREEN = (0, 255, 0)  # Open node
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)  # Barrier node
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)  # Start node
GREY = (128, 128, 128)
TURQUOISE = (64, 244, 208)  # End node

font = pygame.font.SysFont(None, 15)
large_font = pygame.font.SysFont(None, 20)
text_font = pygame.font.SysFont('comicsans', 36)
enable_numbers = True


f_score = {}
g_score = {}
h_score = {}
buttons = []

visited = 0
length_path = 0

# Node class ----------------------------------------------------------------------------------------------------------#
class Node:
    def __init__(self, row, col, size, total_rows):
        self.row = row
        self.col = col
        self.x = row * size
        self.y = col * size
        self.color = WHITE
        self.neighbors = []
        self.size = size
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_start(self):
        self.color = ORANGE

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))

    def update_neighbors(self, grid):
        self.neighbors = []
        # Check if node is in the grid              check if node is barrier
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():  # Check down
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # Check up
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():  # Check right
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # Check left
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False

# Button class --------------------------------------------------------------------------------------------------------#
class button():
    def __init__(self, color, x, y, width, height, text=''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
    def draw(self, window, outline=None):
        #outline is rgb value
        if outline: #If outline is not None
            pygame.draw.rect(window, outline, (self.x-2, self.y-2, self.width+4,self.height+4),0) #2 pixel border
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height), 0)

        if self.text != '':
            font = pygame.font.SysFont('comicsans', 36)
            text = font.render(self.text, True, (0,0,0))
            window.blit(text, (self.x+(self.width/2-text.get_width()/2), (self.y+(self.height/2-text.get_height()/2))))

    def isOver(self, pos):
        x, y = pos
        return x > self.x and x < self.x + self.width and y > self.y and y < self.y + self.height


# Functions -----------------------------------------------------------------------------------------------------------#
def h(p1, p2):  # estimates distance of 2 points
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def make_grid(rows, size):
    grid = []
    gap = size // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return grid


def draw_grid(screen, rows, size):  # draws only gridlines
    gap = size // rows
    for i in range(rows):
        pygame.draw.line(screen, GREY, (0, i * gap), (size, i * gap))
        for j in range(rows):
            pygame.draw.line(screen, GREY, (j * gap, 0), (j * gap, size))


def draw(screen, grid, rows, size):
    screen.fill(WHITE)
    for row in grid:
        for spot in row:
            spot.draw(screen)
            if not(not f_score) and enable_numbers:
                if str(f_score[spot]) != 'inf':
                    text = large_font.render(str(f_score[spot]), True, BLACK)
                    screen.blit(text, [spot.x+spot.size/2-text.get_width()/2, spot.y+spot.size-text.get_height()-1])

                    text = font.render(str(g_score[spot]), True, BLACK)
                    screen.blit(text, [spot.x+3, spot.y+3])

                    text = font.render(str(h_score[spot]), True, BLACK)
                    screen.blit(text, [spot.x + spot.size-text.get_width()-3, spot.y+3])

     # When hovering over button, change color
    for i in buttons:
         if i.isOver(pygame.mouse.get_pos()):
            i.color = GREY
         else:
            i.color = WHITE
    text = text_font.render("Nodes accessed: "+ str(visited), True, BLACK)
    if visited != 0:
        screen.blit(text, (0,1000-text.get_height()))

    if length_path != 0:
        text = text_font.render("Distance of path: " + str(length_path), True, BLACK)
        screen.blit(text, (0, 1000 - text.get_height()*2))

    draw_grid(screen, rows, size)
    for button in buttons:
        button.draw(screen, (0,0,0))
    pygame.display.update()


def get_clicked_pos(pos, rows, size):
    gap = size // rows
    y, x = pos
    row = y // gap
    col = x // gap
    return row, col


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


# Algorithm -----------------------------------------------------------------------------------------------------------#
def algorithm(draw, grid, start, end):
    global visited
    global length_path

    count = 0  # Keep count of when nodes are inserted into the open set
    open_set = PriorityQueue()  # Priority queue similar to array
    open_set.put((0, count, start))  # add starting node to open set .put is .append
    came_from = {}  # dict to keep track of where each node came from
    # g_score is the distance from start node to a node
    g_score.update({spot: float("inf") for row in grid for spot in row})  # assign all g_score of nodes = infinity
    g_score[start] = 0  # distance from start node to start node is 0

    # f_score is the distance from end node to a node
    h_score.update({spot: float("inf") for row in grid for spot in row})  # assign all g_score of nodes = infinity
    h_score[start] = h(start.get_pos(), end.get_pos())  # distance from start node to start node is 0

    # f_score is the sum of g_score and h_score
    f_score.update({spot: float("inf") for row in grid for spot in row})  # assign all f_score of nodes = infinity
    f_score[start] = h(start.get_pos(), end.get_pos())  # f_score of start node = 0 + h_score

    # keeps track of all items in the priority queue. Priority queue cant check if an item is in the queue
    open_set_hash = {start}

    while not open_set.empty():  # if open set is empty then all possible nodes are considered

        # If algorithm runs for too long provides user a way to exit the loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        current = open_set.get()[2]  # index 2 because thats where nodes are stored (f_score, count, node)
        open_set_hash.remove(current)

        if current == end:  # If the current node is the end node, then shortest path has been found. Reconstruct path
            reconstruct_path(came_from, end, draw)
            end.make_end()
            start.make_start()
            length_path = g_score[end]
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                h_score[neighbor] = h(neighbor.get_pos(), end.get_pos())
                f_score[neighbor] = temp_g_score + h_score[neighbor]

                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()
        draw()

        if current != start:
            current.make_closed()
            visited += 1

    return False


# Main game loop ------------------------------------------------------------------------------------------------------#
def main(screen, size, clock):
    global visited
    global length_path
    global enable_numbers

    ROWS = 25
    grid = make_grid(ROWS, size)

    start = None
    end = None

    run = True
    runButton = button(WHITE, 50, size+50, 125, 50, 'Run')
    buttons.append(runButton)

    clearButton = button(WHITE, size-125-50, size+50, 125, 50, 'Clear')
    buttons.append(clearButton)

    numberButton = button(WHITE, size/2 - 125, size + 50, 250, 50, 'Hide Calculations')
    buttons.append(numberButton)
    started = False  # If algorithm has started

    while run:
        draw(screen, grid, ROWS, size)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if pygame.mouse.get_pressed()[0]:  # left mouse mutton
                if pygame.mouse.get_pos()[1] < 800:

                    row, col = get_clicked_pos(pygame.mouse.get_pos(), ROWS, size)
                    spot = grid[row][col]
                    if not start and spot != end:
                        start = spot
                        start.make_start()
                    elif not end and spot != start:
                        end = spot
                        end.make_end()
                    elif spot != end and spot != start:
                        spot.make_barrier()

                if runButton.isOver(pygame.mouse.get_pos()) and start and end:
                    visited = 0
                    length_path = 0
                    for row in grid:
                        for spot in row:
                            if spot.color == RED or spot.color == GREEN or spot.color == PURPLE:
                                spot.reset()
                            spot.update_neighbors(grid)
                    algorithm(lambda: draw(screen, grid, ROWS, size), grid, start, end)

                if clearButton.isOver(pygame.mouse.get_pos()):
                    start = None
                    end = None
                    length_path = 0
                    visited = 0
                    f_score.clear()
                    g_score.clear()
                    h_score.clear()
                    grid = make_grid(ROWS, size)

                if numberButton.isOver(pygame.mouse.get_pos()):
                    enable_numbers = not enable_numbers
                    if enable_numbers:
                        numberButton.text = "Hide calculations"
                    else:
                        numberButton.text = "Show calculations"

            elif pygame.mouse.get_pressed()[2]:  # right mouse button
                if pygame.mouse.get_pos()[1] < 800:
                    row, col = get_clicked_pos(pygame.mouse.get_pos(), ROWS, size)
                    spot = grid[row][col]
                    spot.reset()
                    if spot == start:
                        start = None
                    elif spot == end:
                        end = None

        clock.tick(60)

    pygame.quit()
    sys.exit()

main(screen, WINDOW_SIZE[0], clock)

