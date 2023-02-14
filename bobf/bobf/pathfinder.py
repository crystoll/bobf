from collections import deque

class Node:
    def __init__(self, parent, pos, cost):
        self.parent = parent
        self.pos = pos
        self.cost = cost

class PathFinder:

    def __init__(self, map):
        self.map = map
        self.tiles = self.map['tiles']


    def getChildrenAstar(self, parent, tracker, goal):
        new_children = []
        #Defines the range of movement
        move = [[-1,0], # up
                [1,0], # down
                [0,-1], # left
                [0,1]] # right


        for i in range(0, len(move)):
            new_pos = move[i]

            #Move to next position
            next_pos = (parent.pos[0] + new_pos[0], parent.pos[1] + new_pos[1])

            # Check for valid position
            # print(f'Checking for valid position at ({next_pos[0]},{next_pos[1]})')
            if(next_pos[0] == -1 or next_pos[1] == -1 or next_pos[0] >= self.map['width'] or next_pos[1] >= self.map['height']):
                continue
            elif(self.tiles[next_pos[1]][next_pos[0]] == 'x'):
                continue
            elif(self.tiles[next_pos[1]][next_pos[0]] == '#'):
                continue
            elif(tracker[next_pos[0]][next_pos[1]] == True):
                continue
            else:
                g =  parent.cost + 1 # each node is equally easy to reach
                h = abs((next_pos[0] - goal[0])) + abs((next_pos[1] - goal[1]))
                f = g + h
                new_cost = f
                new_node = Node(parent, next_pos, new_cost)
                new_children.append(new_node)
        return new_children


    def sortkey(self, node):
        return node.cost


    # Give positions in format (y,x) to be compatible with map
    def find_route(self, pos1, pos2):
        print(f'Finding route from {pos1} to {pos2}')
        visited = []
        for i in range(0, self.map['width']):
            templist = []
            for j in range(0, self.map['height']):
                templist.append(False)
            visited.append(templist)
        start = Node("None", pos1, 0)
        current = start
        queue = deque([])
        visited[start.pos[0]][start.pos[1]] = True
        queue.append(start)
        found = False

        while queue:
            #Pop the current node
            current = queue.popleft()

            #Check is current is end
            if(current.pos == pos2):
                found = True
                break

            #Get the children of current
            children = self.getChildrenAstar(current, visited, pos2)

            #Sort children by cost
            children.sort(key=self.sortkey)

            #Mark as visited and add to queue
            for i in range(0, len(children)):
                visited[children[i].pos[0]][children[i].pos[1]] = True
                queue.append(children[i])

        # Step back through the map to update the shortest path
        
        if(found == True):
            route = deque([])
            while current.parent != "None":
                route.appendleft((current.pos[0],current.pos[1]))
                current = current.parent
            return route
        else:
            return None # No path

