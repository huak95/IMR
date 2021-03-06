import os

ROBOT_DISTANCE_ANGLES = list(range(0, 360, 45))
ROBOT_MAX_SENSOR_DISTANCE = 100
ROBOT_START_POS = (20, 560)

DEFAULT_MAP_DIRECTORY = './maps'
DEFAULT_MAP_NAME = 'default_map.kv'
DEFAULT_MAP_PATH = os.path.join(DEFAULT_MAP_DIRECTORY, DEFAULT_MAP_NAME)

SIMBOTMAP_SIZE = (700, 600)
SIMBOTMAP_BBOX = (
    ((0, 0), (SIMBOTMAP_SIZE[0], 0)),
    ((SIMBOTMAP_SIZE[0], 0), (SIMBOTMAP_SIZE[0], SIMBOTMAP_SIZE[1])),
    ((SIMBOTMAP_SIZE[0], SIMBOTMAP_SIZE[1]), (0, SIMBOTMAP_SIZE[1])),
    ((0, SIMBOTMAP_SIZE[1]), (0, 0)),
)