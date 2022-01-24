import pygame
import math

class buildEnvironment:
    def __init__(lidar, MapDimensions):
        pygame.init()
        lidar.pointCloud = []
        lidar.externalMap = pygame.image.load('map2.png')
        lidar.maph, lidar.mapw = MapDimensions
        lidar.MapWindowName = 'Anotonomous Path'
        pygame.display.set_caption(lidar.MapWindowName)
        lidar.map = pygame.display.set_mode((lidar.mapw, lidar.maph))
        lidar.map.blit(lidar.externalMap,(0,0))

        #Colors
        lidar.black = (0,0,0)
        lidar.gray = (70,70,70)
        lidar.blue = (0,0,255)
        lidar.green = (0,255,0)
        lidar.red = (255,0,0)
        lidar.white = (255,255,255)

        
    
    def AD2pos (lidar,distance,angle,robotPosition):
        x = distance * math.cos(angle) + robotPosition[0]
        y = -distance * math.sin(angle) + robotPosition[1]
        return (int(x),int(y))

    def dataStorage(lidar, data):
        #print(len(lidar.pointCloud))
        if data!=False:
            for element in data:
                point = lidar.AD2pos(element[0],element[1],element[2])
                if point not in lidar.pointCloud:
                    lidar.pointCloud.append(point)



    def show_sensorData(lidar):
        lidar.infomap = lidar.map.copy()
        for point in lidar.pointCloud:
            lidar.infomap.set_at((int(point[0]),int(point[1])),(255,0,0))
