import pygame
import math
import numpy as np

def uncertainty_add ( distance, angle, sigma):
    mean = np.array([distance, angle])
    covariance = np.diag(sigma ** 2)
    distance, angle = np.random.multivariate_normal(mean, covariance)
    distance = max(distance, 0)
    angle = max(angle, 0)
    return [distance, angle]



class LaserSensor:



    def __init__(lidar,Range,map,uncertainty):
        lidar.Range = Range
        lidar.speed = 4 # RPS
        lidar.sigma = np.array([uncertainty[0],uncertainty[1]])
        lidar.position = (0,0)
        lidar.map = map
        lidar.W,lidar.H = pygame.display.get_surface().get_size()
        lidar.sensedObstacles = []

    def distance(lidar, obstaclePosition):
        px = (obstaclePosition[0]-lidar.position[0])**2
        py = (obstaclePosition[1]-lidar.position[1])**2
        return math.sqrt(px+py)


    def sense_obstacles(lidar) :
        data = []
        x1, y1 = lidar.position[0], lidar.position[1]
        
        for angle in np.linspace(0,2*math.pi,60,False):
            x2,y2 = (x1 + lidar.Range * math.cos(angle), y1 - lidar.Range * math.sin(angle))
            for i in range(0,100):
                u = i/100
                x = int(x2 * u + x1 * (1-u))
                y = int(y2 * u + y1 * (1-u))
                if 0<x<lidar.W and 0<y<lidar.H:
                    color = lidar.map.get_at((x,y))
                    if (color[0],color[1],color[2]) == (0,0,0):
                        distance = lidar.distance((x,y))
                        output = uncertainty_add(distance, angle, lidar.sigma)
                        output.append(lidar.position)
                        #store the measurements
                        data.append(output)
                        #print (data)
                        break
                        
        if len(data)>0:
            return data
        else:
            print('FALSE SENSE')
            return False
