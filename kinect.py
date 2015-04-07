import socket, time, threading


class Skeleton:
    def __init__(self, skeletonID):
        self.skeleton = {}
        self.skeletonID = skeletonID

    """
    Takes the stream data sent from the C# code (and received by KinectStreamServer)
    and parses the data, setting the appropriate bone properties
    """
    def parseSkeletonStream(self, streamData):
        streamData = eval(streamData)
        if streamData["id"] == self.skeletonID:
            self.setJointPosition(streamData["joint"], (streamData["x"],streamData["y"],streamData["z"]))

    """
    Returns a tuple of the specified joint position
    """
    def getJointPosition(self, jointName):
        joint = self.skeleton[jointName]
        return joint["x"], joint["y"], joint["z"]

    """
    Sets the X,Y,Z position of specified joint.
    Also sets the lastUpdated timestamp
    """
    def setJointPosition(self, jointName, position):
        self.skeleton[jointName]["x"] = position[0]
        self.skeleton[jointName]["y"] = position[1]
        self.skeleton[jointName]["z"] = position[2]
        self.skeleton[jointName]["lastUpdated"] = time.time()

    """
    Prints the specified joint position
    """
    def printJointPosition(self, jointName):
        pos = self.getJointPosition(jointName)
        print("{}: X: {}, Y: {}, Z: {}".format(jointName, pos[0], pos[1], pos[2]))

    """
    Returns time since last joint update in ms
    """
    def getLastUpdated(self, jointName):
        return (time.time()-self.skeleton["lastUpdated"])*1000

class KinectStreamServer:
    def __init__(self, host):
        self.host = host
        
        self.recvBuffer = ""
        self.packetStarted = False
        
        self.listener = None
        self.running = False

        self.thread = None

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(self.host)
        self.socket.listen(1)
        print("Listening on {}".format(self.host))
        self.running = True

        self.thread = threading.Thread(target=self.loop)
        self.thread.setDaemon(True)
        self.thread.start()

    def stop(self):
        self.running = False

    def setListener(self, listener):
        self.listener = listener

    def callListener(self, arg):
        if not self.listener == None:            
            self.listener(arg)
        else:
            print("ERROR: Listener not defined.")

    def loop(self):
        self.conn, self.connAddr = self.socket.accept()
        print("Connection from {}".format(self.connAddr))
        while self.running:
            recv = self.conn.recv(1).decode("utf-8")
            if recv == "":
                print("Socket Closed.")
                self.stop()
                continue

            if self.packetStarted:
                self.recvBuffer = self.recvBuffer + recv
                if recv == "}":                    
                    self.callListener(self.recvBuffer)
                    self.recvBuffer = ""
                    self.packetStarted = False
            else:           
                if recv == "{":
                    self.packetStarted = True
                    self.recvBuffer = self.recvBuffer + recv

if __name__ == "__main__":
    skeleton = Skeleton(1)
    app = KinectStreamServer(("localhost", 1996))
    app.setListener(skeleton.parseSkeletonStream)
    app.start()
    while True:
        command = input(">>> ")
        if command == "stop":
            app.stop()
        elif command=="head":
            skeleton.printJointPosition("Head")
        else:
            print("""
            stop: Stops the thread.
            help: This command.
            head: Prints out head position
            """)
