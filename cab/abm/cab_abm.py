"""
This module contains all classes associated with the agent based system,
except for the agent classes themselves.
"""

__author__ = 'Michael Wagner'


# TODO: include choice between cells inhabitable by only one or multiple agents at once.
class ABM:
    def __init__(self, gc, visualizer, proto_agent=None):
        """
        Initializes an abm with the given number of agents and returns it.
        :param visualizer: Necessary for graphical output of the agents.
        :param gc: Global Constants, Parameters for the ABM.
        :return: An initialized ABM.
        """
        self.agent_set = set()
        self.agent_locations = dict()
        self.visualizer = visualizer
        self.gc = gc
        self.new_agents = []
        if not proto_agent is None:
            self.add_agent(proto_agent)

    def cycle_system(self, ca):
        """
        Cycles through all agents and has them perceive and act in the world
        """
        # Have all agents perceive and act in a random order
        # While we're at it, look for dead agents to remove
        changed_agents = []
        for a in self.agent_set:
            a.perceive_and_act(ca, self)
            if a.x != a.prev_x or a.y != a.prev_y:
                changed_agents.append(a)
        self.update_agent_positions(changed_agents)
        self.schedule_new_agents()
        self.agent_set = set([agent for agent in self.agent_set if not agent.dead])

    def update_agent_positions(self, changed_agents):
        for agent in changed_agents:
            if self.gc.ONE_AGENT_PER_CELL:
                self.agent_locations.pop((agent.prev_x, agent.prev_y))
                self.agent_locations[agent.x, agent.y] = agent
            else:
                self.agent_locations[agent.prev_x, agent.prev_y].remove(agent)
                try:
                    self.agent_locations[agent.x, agent.y].add(agent)
                except KeyError:
                    self.agent_locations[agent.x, agent.y] = set([agent])

    def add_agent(self, agent):
        self.new_agents.append(agent)

    def schedule_new_agents(self):
        """
        Adds an agent to be scheduled by the abm.
        """
        for agent in self.new_agents:
            pos = (agent.x, agent.y)
            self.agent_set.add(agent)
            if agent.x != None and agent.y != None:
                if self.gc.ONE_AGENT_PER_CELL:
                    if not pos in self.agent_locations:
                        self.agent_locations[pos] = agent
                    # Can't insert agent if cell is already occupied.
                else:
                    if pos in self.agent_locations:
                        self.agent_locations[pos].add(agent)
                    else:
                        self.agent_locations[pos] = set([agent])
        self.new_agents = list()

    def remove_agent(self, agent):
        """
        Removes an agent from the system.
        """
        a_index = -1
        if self.gc.ONE_AGENT_PER_CELL:
            if self.agent_locations[agent.x, agent.y].a_id == agent.a_id:
                del(self.agent_locations[agent.x, agent.y])
        else:
            for a in self.agent_locations[agent.x, agent.y]:
                if a.a_id == agent.a_id:
                    a_index = self.agent_locations[agent.x, agent.y].index(a)
                    break
            if a_index != -1:
                self.agent_locations[agent.x, agent.y].pop(a_index)
                if len(self.agent_locations[agent.x, agent.y]) == 0:
                    del(self.agent_locations[agent.x, agent.y])

    def draw_agents(self):
        """
        Iterates over all agents and hands them over to the visualizer.
        """
        draw = self.visualizer.draw_agent
        for a in self.agent_set:
            draw(a)