# PySimbot

PySimbot is a software for simple robot simulation

## Installation

- Require Python3 and pip [Python](https://www.python.org/downloads/)
- For Windows, install dependencies by run `pip install --pre --extra-index-url https://kivy.org/downloads/simple/ -r requirements_windows.txt`
- For MacOS, install dependencies by run `pip3 install --pre --extra-index-url https://kivy.org/downloads/simple/ -r requirements_macos.txt`
- For Linux, install dependencies by run `pip3 install --pre --extra-index-url https://kivy.org/downloads/simple/ -r requirements_linux.txt`

## Getting Started

- Running an example by `python example<i>_<example-name>.py` to understand the basic coding structure.
- The root class is PySimbotApp. The instance contains objects from the other classes by the following structure.
```lang-none
PySimbotApp
ㄴSimbot
  ㄴSimbotMap
    ㄴRobot
    ㄴObstacle
    ㄴObjective
```
- Create your own robot class by extends the pysimbotlib.core.Robot class. The robot class contains following properties and methods.

|     Property    |        Type       |                             Description                             |
|:---------------:|:-----------------:|:-------------------------------------------------------------------:|
| color           | Tuple(r, g, b, a) | color of the robot                                                  |
| eat_count       | int               | number of foods eaten                                               |
| collision_count | int               | number of collisions made by this robot                             |
| just_eat        | bool              | flag that would be True if the robot ate food in the last iteration |
| stuck           | bool              | flag that would be True when the robot is stuck to the wall         |

|     Method    |            Arguments           | Return Type |                                    Description                                   |
|:-------------:|:------------------------------:|-------------|:--------------------------------------------------------------------------------:|
| set_color     | r, g, b, a: float              | None        | set the robot color (r, g, b, a is between 0 to 1) (a is 1 if not specified)     |
| distance      | -                              | List[float] | get the 8 sensor distances in pixels from the sensors around the robot side      |
| smell         | index: int (Optional variable) | float       | get the distance to the food with the given index. (index is 0 if not specified) |
| smell_nearest | -                              | float       | get the distance to the nearest food                                             |
| turn          | degree: float                  | None        | turn the robot by the specifying degree                                          |
| move          | step: int                      | None        | move the robot forward by the specified step. The robot will not move if collide.|
| update        | None                           | None        | update the robot state for each simbot's iteration                               |

- Override the update() method to implement the robot's logic.
- Pass your robot's class as the parameter to the PySimbotApp to make a simulation.

## Advanced usages

You can configure the PySimbotApp in several ways by passing the parameters to the PySimbotApp's constructor.

- robot_cls: the robot class
- num_robots: the number of robots 
- num_objectives: the number of foods
- robot_default_start_pos: the start position of the robot in (x, y) tuple format
- obj_default_start_pos: the start position of the food in (x, y) tuple format
- interval: the time interval between each frame of simulation
- max_tick: the maximum frame for a simulation
- map: the name of the map. It could be ['default', 'no_wall'] 
- theme: the name of the map's theme. It could be ['default', 'dark', 'light']
- customfn_create_robots: the custom function that returns the list of robots.
- customfn_before_simulation: the custom function that would run before each simulation. It could use for logging purpose
- customfn_after_simulation: the custom function that would run after each simulation. It could use for logging purpose
- enable_wasd_control: the boolean flag that enables the WASD robot control
- simulation_forever: the boolean flag that enables the simulation with no stop.
- food_move_after_eat: the boolean flag that enables changing position of food after the robot eat.
- save_wasd_history: the boolean flag that enables the robot logging with WASD control.
- robot_see_each_other: the boolean flag that enables the robots to measure the distance of other robots.
