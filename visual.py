#!/usr/bin/env python
import pygame, sys
from pygame.locals import *
from collections import defaultdict
from sys import maxsize
from getopt import GetoptError, getopt

WHITE = (255, 255, 255)
GRAY = (125, 125, 125)
BLACK = (35, 35, 35)
GREEN = (0, 204, 0)
DARK_GREEN = (0, 89, 0)
RED = (255, 0, 0)
ORANGE = (255, 69, 0)
BLUE = (52, 79, 235)
PURPLE = (103, 14, 227)

modes = {0: BLUE, 1: PURPLE, 2: BLACK, 3: WHITE}
edit_mode = -1
start_cell, end_cell = None, None
start_xy, end_xy = None, None
grid_size = 60
edited_squares = []


def print_usage():
    pass


def dijkstra(screen, grid, start, end, squares):
    global edited_squares
    
    gh, gw = len(grid), len(grid[0])
    heap_que = defaultdict(tuple)
    heap_que[start] = 0
    visited = set()
    minimums = defaultdict(lambda: maxsize)

    while heap_que:
        distance = min(heap_que.values())
        cur = list(heap_que.keys())[list(heap_que.values()).index(distance)]
        heap_que.pop(cur)

        if cur == end:
            print(f"distance: {str(distance)}")
            break
        elif cur in visited:
            continue
        else:
            visited.add(cur)
            if cur != start:
                pygame.draw.rect(screen, DARK_GREEN, squares[cur[0]][cur[1]])
                edited_squares.append(squares[cur[0]][cur[1]])

        # calculate weights for neighbours
        t, b = (cur[0]-1, cur[1]), (cur[0]+1, cur[1])
        l, r = (cur[0], cur[1]-1), (cur[0], cur[1]+1)
        tl, tr = (cur[0]-1, cur[1]-1), (cur[0]-1, cur[1]+1)
        bl, br = (cur[0]+1, cur[1]-1), (cur[0]+1, cur[1]+1)
        
        for n in [t, b, l, r, tl, tr, bl, br]:
            if n[0] < 0 or n[0] > gw-1:
                continue
            elif n[1] < 0 or n[1] > gh-1:
                continue
            elif n in visited:
                continue

            if n != end and grid[n[0]][n[1]] == 1:
                pygame.draw.rect(screen, GREEN, squares[n[0]][n[1]])
                edited_squares.append(squares[n[0]][n[1]])

            n_weigh = grid[n[0]][n[1]]
            n_distance = distance + n_weigh
            if n_distance < minimums[n]:
                minimums[n] = n_distance
                heap_que[n] = n_distance

            # update grid visuals
            pygame.display.update()

    # backtrack & visualize the path
    cur = end
    visited = []
    lowest = maxsize
    next = None

    while True:
        t, b = (cur[0]-1, cur[1]), (cur[0]+1, cur[1])
        l, r = (cur[0], cur[1]-1), (cur[0], cur[1]+1)
        tl, tr = (cur[0]-1, cur[1]-1), (cur[0]-1, cur[1]+1)
        bl, br = (cur[0]+1, cur[1]-1), (cur[0]+1, cur[1]+1)

        for n in [t, b, l, r, tl, tr, bl, br]:
            if gw-1 < n[0] < 0 or gh-1 < n[1] < 0:
                continue
            elif n in visited:
                continue
            elif n == start:
                pygame.draw.rect(screen, ORANGE, squares[cur[0]][cur[1]])
                return

            if minimums[n] < lowest:
                lowest = minimums[n]
                next = n

        if cur != end: 
            pygame.draw.rect(screen, ORANGE, squares[cur[0]][cur[1]])

        visited.append(cur)

        if next is None:
            print("no possible path found")
            return

        cur = next


def a_star(grid, start, end):
    # TODO add a*
    visited = set()
    open_nodes = set()
    open_nodes.add(start)
    minimums = defaultdict(maxsize)

    while len(open_nodes) > 0:
        pass


def setup_grid(grid_size, size, screen):
    margin = 1
    margin_removed = size - (grid_size + 1) * margin
    node_size = round(margin_removed / grid_size)
    squares = []
    for r in range(grid_size):
        sl = []
        for c in range(grid_size):
            x = margin + c * (margin + node_size)
            y = margin + r * (margin + node_size)
            rect = pygame.Rect(x, y, node_size, node_size)
            pygame.draw.rect(screen, WHITE, rect)
            sl.append(rect)
        squares.append(sl)
    return [[1 for i in range(grid_size)] for ii in range(grid_size)], squares


def setup_buttons(screen):
    start_label = pygame.font.SysFont("Ubuntu", 11).render("Set Start", 1, WHITE)
    end_label = pygame.font.SysFont("Ubuntu", 11).render("Set End", 1, WHITE)
    obs_label = pygame.font.SysFont("Ubuntu", 11).render("Set Obs.", 1, WHITE)
    clear_label = pygame.font.SysFont("Ubuntu", 11).render("Clear (1)", 1, WHITE)
    clean_label = pygame.font.SysFont("Ubuntu", 11).render("Clean", 1, WHITE)
    reset_label = pygame.font.SysFont("Ubuntu", 11).render("Reset", 1, WHITE)
    findpath_label = pygame.font.SysFont("Ubuntu", 11).render("Find Path", 1, WHITE)

    labels = [start_label, end_label, obs_label, clear_label, clean_label, reset_label, findpath_label]
    buttons = []
    margin = 3
    next = (2, 605)

    for l in labels:
        w, h = l.get_size()
        bg_button = pygame.Rect(next[0], next[1], w+8, h+4)
        pygame.draw.rect(screen, WHITE, bg_button, 1)
        buttons.append(bg_button)
        screen.blit(l, (next[0]+4, next[1]+2))
        next = (next[0]+w+8+margin, next[1])
    
    return buttons


def mark_cell(screen, rect, grid, xy, mode):
    global modes, start_cell, end_cell, start_xy, end_xy

    match mode:
        case 0:
            # start
            if start_cell:
                pygame.draw.rect(screen, WHITE, start_cell)
                pygame.draw.rect(screen, modes[mode], rect)
            else:
                pygame.draw.rect(screen, modes[mode], rect)
            start_cell = rect
            start_xy = xy
        case 1:
            # end
            if end_cell:
                pygame.draw.rect(screen, WHITE, end_cell)
                pygame.draw.rect(screen, modes[mode], rect)
            else:
                pygame.draw.rect(screen, modes[mode], rect)
            end_cell = rect
            end_xy = xy
        case 3:
            # clear
            pygame.draw.rect(screen, WHITE, rect)
            if rect == end_cell:
                end_cell, end_xy = None, None
            elif rect == start_cell:
                start_cell, start_xy = None, None
            elif grid[xy[0]][xy[1]] == maxsize:
                grid[xy[0]][xy[1]] = 1

    return grid


def paint_obstacle(screen, grid, squares):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if click[0] == True:
        for y, r in enumerate(squares):
            for x, s in enumerate(r):
                if s.collidepoint(mouse):
                    pygame.draw.rect(screen, BLACK, s)
                    grid[y][x] = maxsize

    return grid


def reset_grid(screen, squares, grid_size):
    for r in squares:
        for s in r:
            pygame.draw.rect(screen, WHITE, s)

    return [[1 for i in range(grid_size)] for ii in range(grid_size)]


def main(algo):
    global edit_mode, grid_size, edited_squares
    global start_cell, end_cell, start_xy, end_xy

    pygame.init()
    size = 600
    screen = pygame.display.set_mode([size+1, size+25])
    pygame.display.set_caption("visual-pathfinder")
    clock = pygame.time.Clock()
    
    # visual elements
    screen.fill((0, 0, 0))
    grid, squares = setup_grid(grid_size, size, screen)
    buttons = setup_buttons(screen)
       
    done = 0
    while not done:
        mouse = pygame.mouse.get_pos()

        if edit_mode == 2:
            grid = paint_obstacle(screen, grid, squares)
        
        for b in buttons:
            if b.collidepoint(mouse):
                pygame.draw.rect(screen, GRAY, b.copy(), 1)
            else:
                pygame.draw.rect(screen, WHITE, b.copy(), 1)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                done = 1

            elif e.type == pygame.MOUSEBUTTONDOWN:
                for i, b in enumerate(buttons):
                    if b.collidepoint(mouse):
                        match i:
                            case 4:
                                # clean
                                if edited_squares:
                                    for s in edited_squares:
                                        pygame.draw.rect(screen, WHITE, s)
                                    edited_squares = []
                            case 5:
                                # reset
                                grid = reset_grid(screen, squares, grid_size)
                                start_cell, start_xy = None, None
                                end_cell, end_xy = None, None
                            case 6:
                                # algo
                                if start_cell and end_cell:
                                    match algo:
                                        case 0:
                                            dijkstra(screen, grid, start_xy, end_xy, squares)
                                        case 1:
                                            a_star(screen, grid, start_xy, end_xy, squares)
                                else:
                                    print("ERROR: start/end missing")

                        print(f"edit_mode = {str(i)}")
                        edit_mode = i

                # choose cell to edit
                for i, r in enumerate(squares):
                    for j, s in enumerate(r):
                        if s.collidepoint(mouse):
                            print(f"collides [{str(edit_mode)}]")
                            if edit_mode not in [-1, 4, 5, 6]:
                                grid = mark_cell(screen, s, grid, (i, j), edit_mode)
            
        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    try:
        opts, args = getopt(sys.argv[1:], "ha:", ["algo="])
    except GetoptError:
        print_usage()
        sys.exit(2)

    # default to dijkstra
    algo = 0

    for opt, arg in opts:
        if opt == "-h":
            print_usage()
            sys.exit()
        elif opt in ("-a", "--algo"):
            algo = arg

    main(algo)
