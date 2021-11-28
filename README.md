# Python-Snake

A clone of the classic game Snake. A coding exercise that started when I received an interesting prompt from a friend; code a clone of Snake in which the only parts of the snake that are tracked by the code are its ends and the points where it turned.

Currently just a quick prototype. More to come.

# To-do List

* [x] Create a working prototype.
* [ ] Decide on a project structure and split existing code into modules.
* [ ] Create a generalized FSM class and FSMState class. Currently thinking the states will work by having a list of actions (ie functions) to run every update, and a list of transitions to other states that will occur if a given condition of some kind is met. We'll see.
* [ ] Change the Actors in the prototype to function using FSMs instead of what they're currently doing.
* [ ] Begin implementing different screens using an FSM by swapping between the game screen and a game over screen. Will likely require some changes to how the main game loop is handled, particularly snake movement speed.
* [ ] Implement a few other screens; a title screen, a view controls screen, etc.
* [ ] Revise this readme into a more proper readme.
* [ ] Look into how one deploys a game made in python with pygame. Create a build.
* [ ] Consider adding more features to the to-do list, perhaps? (Ideas: picking between a few levels & loading levels from files; settings that save/load from file & corresponding screen; sprites & animations; sound effects & music; a few more kinds of actors with different behaviours, like moving food; different colour palettes; level editor)
