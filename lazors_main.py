import random


def read_bff(filename):
    file = open(filename)
    content = file.read().splitlines()
    content = list(filter(None, content))

    grid = []
    grid_reader = False
    blocks = []
    lazors = []
    points = []

    for line in content:
        if line == "GRID START":
            grid_reader = True
        if line == "GRID STOP":
            grid_reader = False
        if grid_reader:
            if line != "GRID START":
                grid.append(line)
        if not grid_reader:
            if line[0] == 'A' or line[0] == 'B' or line[0] == 'C':
                blocks.append(line)

            if line[0] == 'L':
                lazors.append(line)

            if line[0] == 'P':
                points.append(line)

    return grid, blocks, lazors, points


def get_valid_positions(grid):
    splitlines = []
    valid_positions = []
    bounds = []
    fixed_blocks = []

    for line in grid:
        splitlines.append(line.split())
        bounds = [len(splitlines[0]) * 2, len(splitlines) * 2]

    for y in range(len(splitlines)):
        for x in range(len(splitlines[y])):

            if splitlines[y][x] == 'o':
                valid_positions.append([2 * x + 1, 2 * y + 1])

            if splitlines[y][x] == 'A' or splitlines[y][x] == 'B' or splitlines[y][x] == 'C':
                fblock = Block(splitlines[y][x], fixed=True)
                fblock.place_block(2 * x + 1, 2 * y + 1)
                fixed_blocks.append(fblock)

    return valid_positions, bounds, fixed_blocks


def get_blocks(blocks):
    splitlines = []
    blocks_objects = []

    for block in blocks:
        splitlines.append(block.split())

    for j in range(len(splitlines)):

        blocks_objects.append([])
        for i in range(int(splitlines[j][1])):
            blocks_objects[j].append(Block(splitlines[j][0]))

    return blocks_objects


def place_all(valid_positions, blocks, fixed_blocks=None):
    taken_positions = [[]]
    taken_surfaces = []
    styles = []
    single_positions = []

    for block in fixed_blocks:
        taken_positions[0].append(block.get_location())
        taken_surfaces.append(block.get_surfaces())
        styles.append(block.get_style())

    for i in range(len(blocks)):
        taken_positions.append([])
        for block in blocks[i]:
            placement = random.choice(valid_positions)
            while single_positions.count(placement) == 1:
                placement = random.choice(valid_positions)

            block.place_block(placement[0], placement[1])
            single_positions.append(placement)
            taken_positions[i + 1].append(placement)
            taken_surfaces.append(block.get_surfaces())
            styles.append(block.get_style())

    return taken_positions, taken_surfaces, styles


def get_lazors(lazors):
    splitlines = []
    lazor_list = []

    for lazor in lazors:
        splitlines.append(lazor.split())

    for lazor in splitlines:
        lazor.pop(0)
        new_lazor = Lazor([int(lazor[0]), int(lazor[1])], [int(lazor[2]), int(lazor[3])])
        lazor_list.append(new_lazor)
    return lazor_list


def get_points(points):
    splitlines = []
    point_str = []
    point_int = []

    for point in points:
        splitlines.append(point.split())

    for point in splitlines:
        point.pop(0)
        point_str.append(point)

    count = 0
    for point in splitlines:
        point_int.append([])
        for num in point:
            point_int[count].append(int(num))
        count += 1
    return point_int


def solve(text):
    solved_points = []
    solved_count = 0
    counter = 0
    position_list = []

    text = read_bff(text)
    positions, bounds, fixed_blocks = get_valid_positions(text[0])
    blocks = get_blocks(text[1])
    lazors = get_lazors(text[2])
    points = get_points(text[3])

    while solved_count < len(points) and counter < 50000:
        taken_positions = None
        taken_surfaces = None
        lazor_paths = None
        lazor_paths = []
        taken_positions, taken_surfaces, styles = place_all(positions, blocks, fixed_blocks)
        sorted_positions = []

        for blocktype in taken_positions:
            sorted_blocks = blocktype.copy()
            sorted_blocks.sort()
            sorted_positions.append(sorted_blocks)
        internal_count = 0
        while position_list.count(sorted_positions) > 0:

            taken_positions, taken_surfaces, styles = place_all(positions, blocks, fixed_blocks)
            sorted_positions = []

            for blocktype in taken_positions:
                sorted_blocks = blocktype.copy()
                sorted_blocks.sort()
                sorted_positions.append(sorted_blocks)
            internal_count += 1

            if internal_count % 100 == 0 and internal_count > 10000000:
                position_list.sort()
                return position_list, sorted_positions, counter

        # print(taken_positions, sorted_positions)

        position_list.append(sorted_positions)

        for lazor in lazors:
            one_path = lazor.path(taken_surfaces, bounds, styles)

            lazor_paths.append(one_path)

        # print(lazor_paths)
        # print(sorted_positions)
        for pointlist in lazor_paths:
            for path in pointlist:
                for point in points:
                    if path.count(point) > 0:
                        if solved_points.count(point) == 0:
                            solved_points.append(point)
                            solved_count += 1
                            # print(solved_points)
                            # print(lazor_paths)

                    if solved_count == len(points) and len(solved_points) == len(points):
                        print('real success')

                        return sorted_positions, lazor_paths

        if sorted_positions == [[], [[1, 5], [3, 3], [3, 5]]]:
            print('this is the catch')
            return lazor_paths

        solved_count = 0
        solved_points = []

        lazors = get_lazors(text[2])
        counter += 1
        # if counter % 10 == 0 and counter > 1500:
        # print(counter)

    position_list.sort()
    # print(sorted_positions)
    return sorted_positions, lazor_paths
    # return taken_positions, lazor_paths, points


class Lazor:

    def __init__(self, startpoint, direction):
        self.start = startpoint
        self.points = [startpoint]
        self.directions = [direction]
        self.in_bounds = True
        self.cont_in_bounds = True
        self.cont_points = []
        self.cont_directions = []

    def next_point(self):
        return [self.points[-1][0] + self.directions[-1][0], self.points[-1][1] + self.directions[-1][1]]

    def get_lazor(self):
        return [self.points[-1], self.directions[-1]]

    def propogate(self):
        self.points.append([self.points[-1][0] + self.directions[-1][0], self.points[-1][1] + self.directions[-1][1]])
        self.directions.append(self.directions[-1])

    def cont_propogate(self):
        self.cont_points.append([self.cont_points[-1][0] + self.cont_directions[-1][0],
                                 self.cont_points[-1][1] + self.cont_directions[-1][1]])
        self.cont_directions.append(self.cont_directions[-1])

    def flip_y(self):
        removed = self.directions.pop(-1)
        self.directions.append([removed[0], -1 * removed[1]])

    def flip_x(self):
        removed = self.directions.pop(-1)
        self.directions.append([-1 * removed[0], removed[1]])

    def contflip_y(self):
        removed = self.cont_directions.pop(-1)
        self.cont_directions.append([removed[0], -1 * removed[1]])

    def contflip_x(self):
        removed = self.cont_directions.pop(-1)
        self.cont_directions.append([-1 * removed[0], removed[1]])

    def reset(self, startpoint, direction):
        self.points = [startpoint]
        self.directions = [direction]

    def out_of_bounds(self):
        self.in_bounds == False

    def cont_out_of_bounds(self):
        self.cont_in_bounds == False

    def path(self, surfaces, bounds, styles):
        count = 0
        start_count = 0
        if surfaces.count(self.points[0]) > 0:
            return [self.points, self.cont_points]

        for surface in surfaces:
            if surface.count(self.start) == 1:
                start_count += 1

        if start_count > 1:
            return [self.points, self.cont_points]

        while self.in_bounds == True and self.cont_in_bounds == True:
            if self.in_bounds == True:
                self.propogate()

            if self.cont_points != [] and self.cont_in_bounds == True:
                self.cont_propogate()

            if len(self.points) == 2:
                for i in range(len(surfaces)):
                    if surfaces[i].count(self.points[0]) == 1 & surfaces[i].count(self.points[1]) == 1:
                        if styles[i] == 'Reflective':
                            # print('reflect next to it')
                            self.points.pop(-1)
                            self.directions.pop(-1)
                            if self.points[0][0] % 2 == 0:
                                self.flip_x()
                                self.propogate()
                                # print(self.points)
                                break
                            else:
                                self.flip_y()
                                self.propogate()
                                # print(self.points)
                                break
                        if styles[i] == 'Opaque':
                            self.points.pop(-1)
                            self.directions.pop(-1)

                            return [self.points, self.cont_points]

                        if styles[i] == 'Refractive':
                            # print('refract next to it')
                            self.cont_points = self.points.copy()
                            self.cont_directions = self.directions.copy()
                            # self.cont_propogate()

                            self.points.pop(-1)
                            self.directions.pop(-1)
                            if self.points[0][0] % 2 == 0:
                                self.flip_x()
                                self.propogate()
                                # print(self.points)
                                break
                            else:
                                self.flip_y()
                                self.propogate()
                                # print(self.points)
                                break
            # print(self.cont_points)

            for i in range(len(surfaces)):
                if surfaces[i].count(self.points[-1]) > 0:

                    if self.points[-1][0] % 2 == 0:
                        if styles[i] == 'Reflective':
                            self.flip_x()
                            # print('flipx', surface)

                        if styles[i] == 'Refractive':
                            self.cont_points = self.points.copy()
                            self.cont_directions = self.directions.copy()
                            self.cont_propogate()
                            self.flip_x()

                        if styles[i] == 'Opaque':
                            # print(self.points)
                            # print(2)
                            # self.points.pop(-1)
                            # self.directions.pop(-1)
                            self.in_bounds = False
                    else:
                        if styles[i] == 'Reflective':
                            self.flip_y()
                            # print('flipy', surface)

                        if styles[i] == 'Refractive':
                            self.cont_points = self.points.copy()
                            self.cont_directions = self.directions.copy()
                            self.cont_propogate()
                            self.flip_y()

                        if styles[i] == 'Opaque':
                            # print(self.points)
                            # print(3)
                            self.points.pop(-1)
                            self.directions.pop(-1)
                            self.in_bounds = False

                if len(self.cont_points) > 0:
                    if surfaces[i].count(self.cont_points[-1]) > 0:

                        if self.cont_points[-1][0] % 2 == 0:
                            if styles[i] == 'Reflective':
                                self.contflip_x()
                                # print('flipx', surfaces[i], self.cont_points[-1])

                            # if styles[i] == 'Refractive':
                            # self.cont_points = self.points.copy()
                            # self.cont_directions = self.directions.copy()
                            # self.cont_propogate()
                            # self.flip_x()

                            if styles[i] == 'Opaque':
                                self.cont_points.pop(-1)
                                self.cont_directions.pop(-1)
                                self.cont_in_bounds = False
                        else:
                            if styles[i] == 'Reflective':
                                self.contflip_y()
                                # print('flipy fract', surfaces[i])

                            # if styles[i] == 'Refractive':
                            # self.cont_points = self.points.copy()
                            # self.cont_directions = self.directions.copy()
                            # self.cont_propogate()
                            # self.flip_y()

                            if styles[i] == 'Opaque':
                                self.points.pop(-1)
                                self.directions.pop(-1)
                                self.cont_in_bounds = False
            # print(self.points)
            if self.points[-1][0] > bounds[0] or self.points[-1][0] < 0:
                self.in_bounds = False
            if self.points[-1][1] > bounds[1] or self.points[-1][1] < 0:
                self.in_bounds = False

            if self.in_bounds == False and len(self.cont_points) == 0:
                return [self.points, self.cont_points]

            # print('new')
        return [self.points, self.cont_points]


class Block:

    def __init__(self, style, x=None, y=None, fixed=False):
        if style == 'A':
            self.style = 'Reflective'
        elif style == 'B':
            self.style = 'Opaque'
        else:
            self.style = 'Refractive'

        self.fixed = fixed
        self.x = x
        self.y = y

    def __str__(self):
        return 'Block Style: ' + str(self.style) + '\nBlock Location: (' + str(self.x) + ',' + str(self.y) + ')'

    def place_block(self, x, y):
        self.x = x
        self.y = y
        self.surfaces = [[x, y - 1], [x + 1, y], [x, y + 1], [x - 1, y]]

    def get_style(self):
        return self.style

    def is_fixed(self):
        return self.fixed

    def get_location(self):
        return [self.x, self.y]

    def get_surfaces(self):
        return self.surfaces


print(solve('showstopper_4.bff'))
