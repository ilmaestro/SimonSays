/*
simon says game
client-side
minimal, css-based
sound support
javascript
---
attempt #1 reqs:
- 10 rounds
- each round takes 2 seconds
- each round plays starts from the beginning and plays up to the next round
--
GameState

Controller
 - init gamestate
 - hookup buttons
 - gameloop
 	- Computer: play round
 	- Player: play round
 		- succes: next round
 		- fail: game over

*/
SimonSays = {};

function $(selector, container) {
	return (container || document).querySelector(selector);
}

(function(){
	var _ = SimonSays.GameState = function() {
		this.stack = [];
		this.stackSize = 10;
		this.isPlayerTurn = false;
		this.currentRound = 0;
		this.playerIndex = 0;
		this.roundTime = 4000; // ms
		this.colors = ["red","green","blue","yellow"];
	};

	_.prototype = {
		resetStack: function () {
			this.stack = [];
			for(i = 0; i<10; i++){
				var colorIndex = Math.floor(Math.random() * 4);
				this.stack.push(colorIndex);
			}
		},
		nextRound: function(){
			this.currentRound++;
			return this.currentRound;
		},
		hasPlayerWon: function(){
			return (this.currentRound >= this.stackSize);
		},
		getRoundTime: function(){
			return (this.roundTime / this.currentRound);
		},
		getColorFromStack: function(index){
			return this.colors[this.stack[index]];
		},
		getScore: function(){
			return this.currentRound;
		},
		startPlayersTurn: function() {
			this.playerIndex = 0;
			this.isPlayerTurn = true;
		},
		playerMove: function(color){
			var isMatch = this.colors[this.stack[this.playerIndex]] === color;
			this.playerIndex++;
			return {
				succeeded: isMatch,
				roundIsOver: (this.playerIndex >= this.currentRound)
			};
		},
		reset: function(){
			this.isPlayerTurn = false;
			this.currentRound = 0;
			this.playerIndex = 0;
			this.resetStack();
		}
	};
}());


(function(){
	var _ = SimonSays.Game = function() {
		var self = this;
		this.gamestate = new SimonSays.GameState();
		this.isButtonBleeping = false;

		this.buttons = {
			red: $('div.r'),
			green: $('div.g'),
			blue: $('div.b'),
			yellow: $('div.y'),
			newGame: $('button.newGame')
		};
		this.buttons.red.addEventListener('click', function() {
			self.onPlayerButton('red');
		});
		this.buttons.green.addEventListener('click', function() {
			self.onPlayerButton('green');
		});
		this.buttons.blue.addEventListener('click', function() {
			self.onPlayerButton('blue');
		});
		this.buttons.yellow.addEventListener('click', function() {
			self.onPlayerButton('yellow');
		});
		this.buttons.newGame.addEventListener('click', function() {
			self.gamestate.reset();
			self.newRound();
		});
	};

	_.prototype = {
		newRound: function(){
			var self = this;
			var round = this.gamestate.nextRound();
			var time = this.gamestate.getRoundTime();
			if(this.gamestate.hasPlayerWon()){
				this.wonRound();
			} else {
				this.playRound(round, time, function(){
					//start players turn
					self.gamestate.startPlayersTurn();
					console.log("players turn now...");
				});
			}
		},
		playRound: function (round, time, callback) {
			console.log("Starting round: " + round);
			var self = this;
			var playStack = function(index){
				if(index >= round){
					callback();
				}
				else {
					var color = self.gamestate.getColorFromStack(index);
					self.bleepButtonOn(color, time, function(){
						playStack(index+1);
					});
				}
			}			
			playStack(0);
		},
		onPlayerButton: function(color){
			var self = this;
			if(this.gamestate.isPlayerTurn && !this.isButtonBleeping){
				console.log("Player move: " + color);
				var move = this.gamestate.playerMove(color);
				if(move.succeeded){
					//continue
					this.bleepButtonOn(color, 500, function(){
						//check for next round
						if(move.roundIsOver){
							self.newRound();
						}
					});

				} else {
					//game over
					this.bleepButtonOn("red", 2000, function(){
						self.gameOver();	
					});					
				}
				
			}
		},
		bleepButtonOn: function(button, time, callback){
			var self = this;
			this.isButtonBleeping = true;
			var newClassName = this.buttons[button].className.replace("inactive", "active");
			this.buttons[button].className = newClassName;
			
			//console.log("BLEEP ON: " + button);
			var ignore = setTimeout(function(){
					self.bleepButtonOff(button);
					callback();
				},time);
		},
		bleepButtonOff: function(button){
			this.isButtonBleeping = false;
			var newClassName = this.buttons[button].className.replace("active", "inactive");
			this.buttons[button].className = newClassName;
			//console.log("BLEEP OFF");
		},
		gameOver: function(){
			console.log("Score: " + this.gamestate.getScore());
		},
		wonRound: function(){
			console.log("You won!");
		}

	};
}());
