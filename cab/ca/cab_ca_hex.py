"""
This module contains the class for a CA with hexagonal cells in pointy top layout.
"""

from cab.ca.cab_cell import CellHex

import math
import cab.util.cab_rng

__author__ = 'Michael Wagner'


class CAHex:
    """
    For reference go to "http://www.redblobgames.com/grids/hexagons/"
    Hex CA parameters:
    - even-r horizontal layout
    - cube coordinates for algorithms
    - axial coordinates for storage
    """

    def __init__(self, cab_sys, proto_cell=None):
        """
        Initializes the cellular automaton. The grid has the form of a dictionary {(q, r) : cell}
        where the values are the cells with their q,r-coordinates as keys.
        """
        self.ca_grid = {}
        self.sys = cab_sys
        self.grid_height = self.sys.gc.GRID_HEIGHT
        self.grid_width = self.sys.gc.GRID_WIDTH
        self.height = int(self.grid_height / self.sys.gc.CELL_SIZE)
        self.width = int(self.grid_width / self.sys.gc.CELL_SIZE)
        self.cell_size = self.sys.gc.CELL_SIZE
        self.use_borders = self.sys.gc.USE_CA_BORDERS
        self.proto_cell = None

        if proto_cell is None:
            for j in range(0, self.height):
                for i in range(0, self.width):
                    # self.ca_grid[i, j] = CellHex(i, j, gc.CELL_SIZE, gc)
                    q = i - math.floor(j / 2)
                    self.ca_grid[q, j] = CellHex(q, j, self.sys.gc)
                    # print('x={0}, y={1}'.format(q, j))
                    if self.sys.gc.USE_CA_BORDERS and (i == 0 or j == 0 or i == (self.width - 1) or j == (self.height - 1)):
                        self.ca_grid[q, j].is_border = True
        else:
            self.proto_cell = proto_cell
            for j in range(0, self.height):
                for i in range(0, self.width):
                    # self.ca_grid[i, j] = proto_cell.clone(i, j, gc.CELL_SIZE)
                    q = i - math.floor(j / 2)
                    self.ca_grid[q, j] = proto_cell.clone(q, j)
                    # print('x={0}, y={1}'.format(q, j))
                    if self.sys.gc.USE_CA_BORDERS and (i == 0 or j == 0 or i == (self.width - 1) or j == (self.height - 1)):
                        self.ca_grid[q, j].is_border = True

        for cell in list(self.ca_grid.values()):
            self.set_cell_neighborhood(cell)

    # Common Interface for all CA classes

    def set_cell_neighborhood(self, cell):
        """
        Assign all neighboring cells of this cell to its neighbor list.
        :param cell: Cell which neighbor list to update.
        """
        cx, cy, cz = cell.get_cube()
        for d in self.sys.gc.HEX_DIRECTIONS:
            x = cx + d[0]
            y = cy + d[1]
            if (x, y) in self.ca_grid:
                cell.neighbors.append(self.ca_grid[x, y])
            elif not self.sys.gc.USE_CA_BORDERS:
                # If we don't have borders, overlap to the other side (left, right only) of the map.
                # Make sure we don't go too high or too low, because we only want to wrap around the "equator".
                if 0 <= y < self.height:
                    new_x = 0
                    min_x = 0 - math.floor(y / 2)
                    max_x = (self.width - 1) - math.floor(y / 2)
                    if x < min_x:
                        new_x = max_x
                    elif x > max_x:
                        new_x = min_x
                    cell.neighbors.append(self.ca_grid[new_x, y])
                    # print("neighbor {0},{1} becomes {2},{3}".format(x, y, new_x, y))

    # def draw_cells(self):
    #     """
    #     Iterate over all cells and call their draw() method.
    #     """
    #     draw = self.visualizer.draw_cell
    #     for cell in self.ca_grid.values():
    #         draw(cell)

    def cycle_automaton(self):
        """
        Update the cellular automaton.
        """
        self.update_cells_from_neighborhood()
        self.update_cells_state()

    def update_cells_from_neighborhood(self):
        """
        Call the neighborhood-update method of all cells in the cellular automaton.
        """
        for cell in self.ca_grid.values():
            cell.sense_neighborhood()

    def update_cells_state(self):
        """
        Calls the the state-update method of all cells in the cellular automaton.
        """
        for cell in self.ca_grid.values():
            cell.update()

    def get_cell_neighborhood(self, cell_x, cell_y, dist):
        """
        Creates a dictionary {'position': cell} where position is an (x,y) tuple
        for the given cell position to get an overview over the surrounding up to a given distance.
        """
        if dist is None:
            dist = 1
        # x = int(agent_x / self.cell_size)
        # y = int(agent_y / self.cell_size)
        neighborhood = {}

        # This is the new hexagonal neighborhood detection with variable range of vision.
        for dx in range(-dist, dist+1):
            for dy in range(max(-dist, -dx-dist), min(dist, -dx+dist) + 1):
                # dz = -dx-dy
                x = cell_x + dx
                y = cell_y + dy
                if (x, y) in self.ca_grid:
                    neigh_cell = self.ca_grid[x, y]
                    neighborhood[x, y] = neigh_cell
                elif not self.sys.gc.USE_CA_BORDERS and 0 <= y < self.height:
                    new_x = 0
                    min_x = 0 - math.floor(y / 2)
                    max_x = (self.width - 1) - math.floor(y / 2)
                    if x < min_x:
                        new_x = (max_x + 1) - (min_x - x)
                    elif x > max_x:
                        new_x = (min_x - 1) + (x - max_x)
                    neigh_cell = self.ca_grid[new_x, y]
                    neighborhood[new_x, y] = neigh_cell
        return neighborhood

    def get_agent_neighborhood(self, agent_x, agent_y, dist):
        """
        Creates a dictionary {'position': (cell, set(agents on that cell))} where position is an (x,y) tuple
        for the calling agent to get an overview over its immediate surrounding.
        """
        if dist is None:
            dist = 1
        # x = int(agent_x / self.cell_size)
        # y = int(agent_y / self.cell_size)
        neighborhood = self.get_cell_neighborhood(agent_x, agent_y, dist)
        new_neighborhood = {}
        other_agents = self.sys.abm.agent_locations

    # This is the slimmed down version that also considers wrapping around ca borders.
        for key, value in neighborhood.items():
            if key not in other_agents:
                agents_on_cell = False
            else:
                agents_on_cell = other_agents[key]
            new_neighborhood[key] = (value, agents_on_cell)

        return new_neighborhood

    def get_empty_agent_neighborhood(self, agent_x, agent_y, dist):
        """
        Creates a dictionary {'position': cell} where position is an (x,y) tuple
        for the calling agent to get an overview over its immediate surrounding.
        """
        if dist is None:
            dist = 1
        # x = int(agent_x / self.cell_size)
        # y = int(agent_y / self.cell_size)
        neighborhood = self.get_cell_neighborhood(agent_x, agent_y, dist)
        other_agents = self.sys.abm.agent_locations

        # This is the slimmed down version that also considers wrapping around ca borders.
        # print('neighborhood items: {0}'.format(list(neighborhood.items())))
        # print('other_agents items: {0}'.format(list(other_agents.items())))
        neighborhood = {key: value for key, value in neighborhood.items() if key not in other_agents}
        return neighborhood

    def get_random_valid_position(self):
        """
        Returns coordinates of a random cell position that is within the boundaries of the grid.
        :return: Coordinates in hex form.
        """
        return get_RNG().choice(list(self.ca_grid.keys()))

    @staticmethod
    def hex_round(q, r):
        """
        Round a hex coordinate to the nearest hex coordinate.
        :param q: Hex coordinate q.
        :param r: Hex coordinate r.
        :return: Rounded hex coordinate triple (x, y, z)
        """
        return CAHex.cube_to_hex(*CAHex.cube_round(*CAHex.hex_to_cube(q, r)))

    @staticmethod
    def cube_round(x, y, z):
        """
        Round a cube coordinate to the nearest hex coordinate.
        :param x: Cube coordinate x.
        :param y: Cube coordinate y.
        :param z: Cube coordinate z.
        :return: Rounded cube coordinate triple (x, y, z)
        """
        rx = round(x)
        ry = round(y)
        rz = round(z)
        dx = abs(rx - x)
        dy = abs(ry - y)
        dz = abs(rz - z)

        if dx > dy and dx > dz:
            rx = -ry - rz
        elif dy > dz:
            ry = -rx - rz
        else:
            rz = -rx - ry

        return rx, ry, rz

    @staticmethod
    def cube_to_hex(x, y, z):
        """
        Convert cube coordinate triple to hex coordinate tuple.
        :param x: Cube coordinate x.
        :param y: Cube coordinate y.
        :param z: Cube coordinate z.
        :return: Hex coordinate tuple (q, r)
        """
        return x, y

    @staticmethod
    def hex_to_cube(q, r):
        """
        Convert hex coordinate tuple into hex coordinate triple.
        :param q: Hex coordinate q.
        :param r: Hex coordinate r.
        :return: Cube coordinate triple (x, y, z)
        """
        z = -q - r
        return q, r, z

    @staticmethod
    def hex_distance(q1, r1, q2, r2):
        """
        Return hex distance between two cells. Equivalent to CAHex.cube_distance(cell_a, cell_b).
        :param q1: Q coordinate of first cell.
        :param r1: R coordinate of first cell.
        :param q2: Q coordinate of second cell.
        :param r2: R coordinate of second cell.
        :return: Distance between first and second cell.
        """
        return (abs(q1 - q2) +
                abs(q1 + r1 - q2 - r2) +
                abs(r1 - r2)) / 2

    @staticmethod
    def get_cell_in_direction(a, b):
        """
        Returns the first cell to go to when moving from cell a to cell b.
        :param a: Starting cell.
        :param b: Target cell.
        :return: Neighboring cell of cell a that leads towards cell b.
        """
        n = CAHex.cube_distance(a, b)
        # Consider the special case where a and b are identical.
        if n == 0:
            return b
        else:
            _x, _y, _z = CAHex.cube_interpolate(a, b, 1.0/n * 1)
            _q, _r = CAHex.cube_to_hex(*CAHex.cube_round(_x, _y, _z))
        return _q, _r

    @staticmethod
    def cube_distance(cell_a, cell_b):
        """
        Returns the cube distance between cell a and cell b. Equivalent to CAHex.hex_distance(q1, r1, q1, r1).
        :param cell_a: Starting cell.
        :param cell_b: Target cell.
        :return: Cube distance between both cells as integer.
        """
        return max(abs(cell_a.x - cell_b.x), abs(cell_a.y - cell_b.y), abs(cell_a.z - cell_b.z))

    @staticmethod
    def cube_interpolate(a, b, t):
        """
        Helper method for direction calculation.
        :param a: Starting cell.
        :param b: Target cell.
        :param t: Current step on the way between a and b.
        :return: Current cell on the way between a and b.
        """
        x = CAHex.float_interpolate(a.x, b.x, t)
        y = CAHex.float_interpolate(a.y, b.y, t)
        z = CAHex.float_interpolate(a.z, b.z, t)
        return x, y, z

    @staticmethod
    def float_interpolate(a, b, t):
        """
        Interpolate a coordinate between two cells and give step.
        :param a: Starting cell
        :param b: Target cell
        :param t: Current step on the way between a and b.
        :return: Interpolated coordinate between cell a and cell b.
        """
        return a + (b - a) * t
