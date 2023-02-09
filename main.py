# import urllib library1
import copy
from urllib.request import urlopen
import json
import os
import uuid
from hashlib import sha256
import threading
import multiprocessing as mp
import time
import numpy as np

# store the URL in url as
# parameter for urlopen
urlBase = "https://coe892.reev.dev/lab1/rover/"

# function to get rover moves
def get_rover_moves(rover_num):
    endpoint = urlBase + str(rover_num)

    # store the response of URL
    response = urlopen(endpoint)

    # convert and store response to JSON format
    data_json = json.loads(response.read())

    # assign values to rovers dict
    rover_moves = data_json['data']['moves']

    return rover_moves

# function to disarm the mines
def disarm_mine(serial_no):
    print(f'Starting to disarm: {serial_no}')

    # note: we increment pin instead of using random to make sure results are reproducible
    # i.e. same time pin is found vs. random time generating random pins
    pin = 0
    success_code = '0' * 4
    mine_key = str(pin) + serial_no
    while not (hash_ := sha256(f'{mine_key}'.encode()).hexdigest()).startswith(success_code):
        pin += 1
        mine_key = str(pin) + serial_no

    print(f'Found pin: {pin}; Temporary mine key: {hash_}')


# function to generate mine serial codes based on number of dig commands of rover
def generate_mines_serial_list(rover_num):
    endpoint = urlBase + str(rover_num)

    # store the response of URL
    response = urlopen(endpoint)

    # convert and store response to JSON format
    data_json = json.loads(response.read())

    # assign values to rovers dict
    rover_moves = data_json['data']['moves']

    # everytime a dig command is found, generate and append a serial number to list
    mine_list = list()
    for move in rover_moves:
        if move == 'D':
            mine_list.append(str(uuid.uuid4().hex))
    return mine_list

# function to write to file
def write_path_file(i, path):
    absolute_path = os.path.dirname(__file__)
    rover_folder_path = 'rover_paths'
    rover_dir = os.path.join(absolute_path, rover_folder_path)

    with open (os.path.join(rover_dir, "path_{}.txt".format(i)), 'w+') as txt_file:
        for line in path:
            txt_file.write(" ".join(line)+'\n')

# function to draw path to path_i
def draw_path(path_i, rover_num, row, col):
    # get rover moves for rover_i
    rover_moves = get_rover_moves(rover_num)

    # copy map to list -- this is so we don't have to write to map.txt directly
    rover_map = copy.deepcopy(path_i)

    # initialize path map for rover
    path = [['0' for x in range(col)] for j in range(row)]

    # dictionary to track rover position
    rover_pos = {'x': 0, 'y': 0, 'dir': 'S'}

    i = 0
    outer_bounds = len(path[0]) - 1
    x = rover_pos['x']
    y = rover_pos['y']
    path[x][y] = '*'

    # for loop and match-case statements that handle rover movement
    for move in rover_moves:

        # rover dies immediately if it steps on a mine and does not immediately dig
        if int(rover_map[x][y]) > 0 and move != 'D':
            return write_path_file(rover_num, path)

        match move:
            case 'M':  # move forward
                match rover_pos['dir']:
                    case 'S':
                        if rover_pos['x'] + 1 <= outer_bounds:
                            rover_pos['x'] += 1
                    case 'N':
                        if rover_pos['x'] - 1 >= 0:
                            rover_pos['x'] -= 1
                    case 'W':
                        if rover_pos['y'] - 1 >= 0:
                            rover_pos['y'] -= 1
                    case 'E':
                        if rover_pos['y'] + 1 <= outer_bounds:
                            rover_pos['y'] += 1
            case 'L':  # turn left
                match rover_pos['dir']:
                    case 'S':
                        rover_pos['dir'] = 'E'
                    case 'N':
                        rover_pos['dir'] = 'W'
                    case 'W':
                        rover_pos['dir'] = 'S'
                    case 'E':
                        rover_pos['dir'] = 'N'
            case 'R':  # turn right
                match rover_pos['dir']:
                    case 'S':
                        rover_pos['dir'] = 'W'
                    case 'N':
                        rover_pos['dir'] = 'E'
                    case 'W':
                        rover_pos['dir'] = 'N'
                    case 'E':
                        rover_pos['dir'] = 'S'
            case 'D':
                # if rover digs a mine, remove from map
                if int(rover_map[x][y]) > 0:
                    rover_map[x][y] = '0'

        x = rover_pos['x']
        y = rover_pos['y']
        path[x][y] = '*'
        i += 1


    write_path_file(rover_num, path)


# function to disarm all the mines in the rover path sequentially
def rover_disarm_mines(mine_list, rover_num, row, col):
    # get rover moves for rover_i
    rover_moves = get_rover_moves(rover_num)

    # copy over list
    path = [['0' for x in range(row)] for j in range(col)]

    # variable to track rover position
    rover_pos = {'x': 0, 'y': 0, 'dir': 'S'}

    i = 0
    outer_x_bounds = row-1
    outer_y_bounds = col-1
    x = rover_pos['x']
    y = rover_pos['y']
    path[x][y] = '*'
    mine_counter = 0

    # we don't take into account mines on the map
    # as soon as rover has a dig move, we disarm a mine
    for move in rover_moves:
        match move:
            case 'M':  # move forward
                match rover_pos['dir']:
                    case 'S':
                        if rover_pos['x'] + 1 <= outer_y_bounds:
                            rover_pos['x'] += 1
                    case 'N':
                        if rover_pos['x'] - 1 >= 0:
                            rover_pos['x'] -= 1
                    case 'W':
                        if rover_pos['y'] - 1 >= 0:
                            rover_pos['y'] -= 1
                    case 'E':
                        if rover_pos['y'] + 1 <= outer_x_bounds:
                            rover_pos['y'] += 1
            case 'L':  # turn left
                match rover_pos['dir']:
                    case 'S':
                        rover_pos['dir'] = 'E'
                    case 'N':
                        rover_pos['dir'] = 'W'
                    case 'W':
                        rover_pos['dir'] = 'S'
                    case 'E':
                        rover_pos['dir'] = 'N'
            case 'R':  # turn right
                match rover_pos['dir']:
                    case 'S':
                        rover_pos['dir'] = 'W'
                    case 'N':
                        rover_pos['dir'] = 'E'
                    case 'W':
                        rover_pos['dir'] = 'N'
                    case 'E':
                        rover_pos['dir'] = 'S'
            case 'D':
                i += 1
                x = rover_pos['x']
                y = rover_pos['y']
                path[x][y] = 'D'

                # instead of mines.txt, we reference a serial_no list of mines
                # and increment the index every dig command
                serial_no = mine_list[mine_counter]
                disarm_mine(serial_no)
                mine_counter += 1
                continue

        x = rover_pos['x']
        y = rover_pos['y']
        path[x][y] = '*'
        i += 1


#function to disarm all the mines in the rover path in parallel
def rover_disarm_mines_parallel(mine_list, rover_num, row, col):
    # get rover moves for rover_i
    rover_moves = get_rover_moves(rover_num)

    # copy over list
    path = [['0' for x in range(col)] for j in range(row)]

    # variable to track rover position
    rover_pos = {'x': 0, 'y': 0, 'dir': 'S'}

    #define list of processes
    processes = list()

    i = 0
    outer_bounds = len(path[0]) - 1
    x = rover_pos['x']
    y = rover_pos['y']
    path[x][y] = '*'
    mine_counter = 0
    for move in rover_moves:
        match move:
            case 'M':  # move forward
                match rover_pos['dir']:
                    case 'S':
                        if rover_pos['x'] + 1 <= outer_bounds:
                            rover_pos['x'] += 1
                    case 'N':
                        if rover_pos['x'] - 1 >= 0:
                            rover_pos['x'] -= 1
                    case 'W':
                        if rover_pos['y'] - 1 >= 0:
                            rover_pos['y'] -= 1
                    case 'E':
                        if rover_pos['y'] + 1 <= outer_bounds:
                            rover_pos['y'] += 1
            case 'L':  # turn left
                match rover_pos['dir']:
                    case 'S':
                        rover_pos['dir'] = 'E'
                    case 'N':
                        rover_pos['dir'] = 'W'
                    case 'W':
                        rover_pos['dir'] = 'S'
                    case 'E':
                        rover_pos['dir'] = 'N'
            case 'R':  # turn right
                match rover_pos['dir']:
                    case 'S':
                        rover_pos['dir'] = 'W'
                    case 'N':
                        rover_pos['dir'] = 'E'
                    case 'W':
                        rover_pos['dir'] = 'N'
                    case 'E':
                        rover_pos['dir'] = 'S'
            case 'D':
                i += 1
                x = rover_pos['x']
                y = rover_pos['y']
                path[x][y] = 'D'

                #spawn process to disarm mine and continue
                serial_no = mine_list[mine_counter]
                process = mp.Process(target=disarm_mine, args=(serial_no,))
                processes.append(process)
                process.start()

                mine_counter += 1
                continue

        print(x, y)
        path[x][y] = '*'
        print(np.matrix(path))
        i += 1

    #wait for all processes to finish before continuing
    for process in processes:
        process.join()



# clear rover_paths directory
def clear_rover_dir():
    absolute_path = os.path.dirname(__file__)
    rover_folder_path = 'rover_paths'
    rover_dir = os.path.join(absolute_path, rover_folder_path)
    for file_name in os.listdir(rover_dir):
        # construct full file path
        file = os.path.join(rover_dir, file_name)
        if os.path.isfile(file):
            os.remove(file)



if __name__ == '__main__':

    # process map.txt
    map_name = 'map.txt'
    map_file = open(map_name, 'r')
    map_raw = [line.split() for line in map_file.readlines()]
    map_file.close()
    row = int(map_raw[:1][0][0])
    col = int(map_raw[:1][0][1])
    map_list = map_raw[1:][:]



    # <------------- Part 1 ------------->
    print('------ Part 1 ------')

    # reset rover_paths directory
    clear_rover_dir()

    # start timing for sequential
    start_time = time.time()
    for i in range(10):
        draw_path(map_list, i+1, row, col)
    serial_total_time = round(time.time() - start_time, 8)
    print('Serial time:', serial_total_time)


    # Parallel
    clear_rover_dir()  #reset rover directory again
    threads = list()    #make thread list

    #start timing for parallel
    p_start_time = time.time()
    for i in range(10):
        thread = threading.Thread(target=draw_path, args=(map_list, i+1, row, col,))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    parallel_total_time = round(time.time() - p_start_time, 8)
    print('Parallel time:', parallel_total_time)


    # <------------- Part 2 ------------->
    print('------ Part 2 ------')

    # generate mine_list
    rover_num = 1
    mine_list = generate_mines_serial_list(rover_num)

    # Sequential
    start_time = time.time()
    rover_disarm_mines(mine_list, rover_num, row, col)
    serial_total_time = round(time.time() - start_time, 8)
    print('Serial time:', serial_total_time)

    # Parallel
    p_start_time = time.time()
    rover_disarm_mines_parallel(mine_list, rover_num, row, col,)
    parallel_total_time = round(time.time() - p_start_time, 8)
    print('Parallel time:', parallel_total_time)