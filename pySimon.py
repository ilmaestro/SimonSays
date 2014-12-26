import RPi.GPIO as GPIO, time, random, math

class RPiManager:
    def __init__(self):
        self.outputPins = {"red": 4, "yellow": 17, "blue": 22, "green": 23}
        self.inputPins = {"red": 4, "yellow": 17, "blue": 22, "green": 23}
        self.inputRev = {v: k for k, v in self.inputPins.items()}
        # GPIO config
        GPIO.setmode(GPIO.BCM)        
        # outputs
        GPIO.setup(outputPins["red"], GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(outputPins["yellow"], GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(outputPins["blue"], GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(outputPins["green"], GPIO.OUT, initial=GPIO.LOW)
        # inputs
        GPIO.setup(inputPins["red"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(inputPins["yellow"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(inputPins["blue"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(inputPins["green"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # event detection
        GPIO.add_event_detect(inputPins["red"], GPIO.FALLING, callback=self.onInputEvent, bouncetime=300)
        GPIO.add_event_detect(inputPins["yellow"], GPIO.FALLING, callback=self.onInputEvent, bouncetime=300)
        GPIO.add_event_detect(inputPins["blue"], GPIO.FALLING, callback=self.onInputEvent, bouncetime=300)
        GPIO.add_event_detect(inputPins["green"], GPIO.FALLING, callback=self.onInputEvent, bouncetime=300)
    
    def setInputHandler(self, inputCallback):
        
        self.inputCallback = inputCallback
    
    def onInputEvent(self, channel):
        #get color from reversed list
        color = self.inputRev[channel]
        self.inputCallback(color)

    def bleep(self, color, beepTime):
        pin = self.outputPins[color]
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(beepTime)
        GPIO.output(pin, GPIO.LOW)
        
    def cleanup(self):
        GPIO.cleanup()
        
class RPiMock:
    def __init__(self):
        self.outputPins = {"red": 1, "yellow": 2, "blue": 3, "green": 4}
        self.inputPins = {"red": 5, "yellow": 6, "blue": 7, "green": 8}
        self.inputRev = rev = {v: k for k, v in self.inputPins.items()}
    
    def setInputHandler(self, inputCallback):
        self.inputCallback = inputCallback
    
    def onInputEvent(self, channel):
        #get color from reversed list
        color = self.inputRev[channel]
        self.inputCallback(color)

    def bleep(self, color, beepTime):
        pin = self.outputPins[color]
        print(color + " bleeep!")
        time.sleep(beepTime)
        
    def cleanup(self):
        time.sleep(1)
        #cleanup

class Gamestate:
    def __init__(self): 
        self.stack = []
        self.stackSize = 10
        self.isPlayerTurn = False
        self.currentRound = 0
        self.playerIndex = 0
        self.roundTime = 1
        self.roundTimeDecrease = 0.1
        self.playerTime = 0.5
        self.colors = ["red","green","blue","yellow"]

    def resetStack(self):
		self.stack = []
		for i in range(10):
			colorIndex = int(math.floor(random.random() * 4))
			self.stack.append(colorIndex)
            
    def hasPlayerWon(self):
        return (self.currentRound >= self.stackSize)

    def nextRound(self):
        self.currentRound += 1
        return self.currentRound
        
    def getRoundTime(self):
        beepTime = self.roundTime - (self.currentRound * self.roundTimeDecrease)
        return beepTime
        
    def getColorFromStack(self, index):
        return self.colors[self.stack[index]]

    def getScore(self):
        return self.currentRound
        
    def getPlayerTime(self):
        return self.playerTime
        
    def startPlayersTurn(self):
        self.playerIndex = 0
        self.isPlayerTurn = True

    def playerMove(self, color):
        isMatch = (self.colors[self.stack[self.playerIndex]] == color)
        self.playerIndex += 1
        return {
        	"succeeded": isMatch,
        	"roundIsOver": (self.playerIndex >= self.currentRound)
        }

    def reset(self):
        self.isPlayerTurn = False
        self.currentRound = 0
        self.playerIndex = 0
        self.resetStack()
    
class Game:
    def __init__(self,gamestate, pimanager):
        self.gs = gamestate
        self.pi = pimanager
        self.pi.setInputHandler(self.onButtonPushed)
        
    def startGame(self):
        self.gs.reset()
        self.newRound()
        
    def newRound(self):
        round = self.gs.nextRound()
        beepTime = self.gs.getRoundTime()
        if self.gs.hasPlayerWon():
            self.wonGame()
        else:
            self.playRound(round, beepTime)
            self.gs.startPlayersTurn()
            print("Players turn now...")

    def playRound(self, round, beepTime):
        print("Starting round " + str(round))
        for r in range(round):
            color = self.gs.getColorFromStack(r)
            self.pi.bleep(color,beepTime)
        
    def onButtonPushed(self, color):
        if self.gs.isPlayerTurn:
            print("player move: " + color)
            move = self.gs.playerMove(color)
            bleepTime = self.gs.getPlayerTime()
            if move["succeeded"] and not move["roundIsOver"]:
                self.pi.bleep(color, bleepTime)
            elif move["succeeded"] and move["roundIsOver"]:
                print("completed round")
                time.sleep(1)
                self.newRound()
            else:
                self.gameover()
        else:
            pass
    
    def wonGame(self):
        print("Won game!")
    def gameover(self):
        print("game over!")
        
def test1():
    gs = Gamestate()
    gs.stack = [0,1,2,3]
    print("1: " + str(gs.getRoundTime() == 0))
    print("2: " + str(gs.hasPlayerWon() == False))
    print("3: " + str(gs.nextRound() == 1))
    print("4: " + str(gs.getColorFromStack(0) == "red"))
    print("5: " + str(gs.getScore() == 1))
    
    print("6: " + str(gs.getPlayerTime() == 0.5))
    gs.startPlayersTurn()
    print("7: " + str(gs.isPlayerTurn == True))
    move = gs.playerMove("red")
    print("8: " + str(move["succeeded"] == True))
    
    gs.resetStack()
    return gs
    
def main():
    gs = Gamestate()
    #pi = RPiManager()
    pi = RPiMock()
    game = Game(gs, pi)
    game.startGame()
    return pi
    
    