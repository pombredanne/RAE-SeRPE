import map

class robot:
    location=''
    temp=map.map()
    def __init__(self,loc,currMap):
        self.location=loc
        self.temp=currMap

    def move(self,loc):
        print 'Moved from location: ' + self.location + ' to location : ' + loc
        self.location=loc

    def search(self,loc):
        if(self.temp.observeable(self.location,loc)):
            print 'Searched for Location: ' +loc + ' from location : ' + self.location + ' and found it!'
            return True
        else:
            print 'Searched for Location: ' + loc + ' from location : ' + self.location + ' and did not find it!'
            return False

    def enter(self,door):
        loc=self.temp.doors[door][0]
        print 'Exited Hallway : ' + self.location + ' and Entered Room : ' + loc
        self.location=loc

    def exit(self,door):
        loc=self.temp.doors[door][1]
        print 'Exited Room : ' + self.location + ' and Entered Hallway : ' +  loc
        self.location=loc

    def currLoc(self):
        print self.location

    def naivePath(self,start,goal):
        return min(list(self.naivePathHelper(start, goal)), key=len)

    def naivePathHelper(self,start, goal):
        graph=self.arena.observMatrix
        stack = [(start, [start])]
        while stack:
            (vertex, path) = stack.pop()
            for next in graph[vertex] - set(path):
                if next == goal:
                    yield path + [next]
                else:
                    pass
                stack.append((next, path + [next]))
