import noise
import numpy as np
import argparse
import sys
import time

from Settings import Settings
from PIL import Image


def RandomJittre(World,mu=1.0,sigma=0.03):
        RandomJittre = np.random.normal(mu,sigma,size=World.shape)
        World *= RandomJittre 
        World = World / np.max(World)
        return World

def CreateCircularFilter(Shape):

        #create grid with index position as value
        x = np.arange(0,Shape,1)
        y = np.arange(0,Shape,1)
        x,y = np.meshgrid(x,y)
        Filter = np.concatenate((x[:,:,np.newaxis],y[:,:,np.newaxis]),axis=2)

        #get center of grid
        Center = np.uint(Shape / 2)
        Center = np.array([Center,Center])

        #get distance to center
        Filter = np.abs(Filter - Center)

        #calculate distance
        Filter = np.sqrt(np.square(Filter[:,:,0]) + np.square(Filter[:,:,1]))

        #normalize
        Filter = Filter / np.max(Filter)

        #invert
        Filter = np.abs(Filter-1)

        #range -1 to 1
        Filter -= .5
        Filter *= 2.0

        #scale
        Filter[Filter>0] *= 20

        #remove zeros
        Filter = np.where(Filter>0,Filter,0)

        #normalize
        Filter = Filter / np.max(Filter)

        return Filter

def CreateNoiseMap(Settings,ImageSize,SetSeed = -1,Seedrange = 100):
    #GENERATE NOISE
    Time1 = time.time()

    Lacunarity = Settings.Data['Lacunarity']
    Persistence = Settings.Data['Persistence']
    Octaves = Settings.Data['Octaves']
    Scale = Settings.Data['ScalePP'] * ImageSize
    Shape = (ImageSize,ImageSize)

    if (SetSeed >= 0):
        seed = SetSeed
    else:
        seed = np.random.randint(0,Seedrange)

    World = np.zeros(Shape)

    def perlinnoise(x,y):
        point = noise.pnoise2(
                x/Scale,
                y/Scale,
                octaves = Octaves, 
                persistence = Persistence,
                lacunarity = Lacunarity, 
                repeatx=ImageSize,
                repeaty=ImageSize,
                base = seed)
        return point

    vfunc = np.vectorize(perlinnoise)

    Rows = []
    for y in range(ImageSize):
        Current = vfunc(np.arange(ImageSize),y)
        Rows.append(Current)

    World = np.array(Rows)

    #APPLY CIRCULAR FILTER
    CircleFilter = CreateCircularFilter(ImageSize)
    World *= CircleFilter
    World = World / np.max(World)

    #ADDING RANDOMNESS MAP
    SettingsSigma = Settings.Data['JittreData']['Sigma']
    SettingsMu = Settings.Data['JittreData']['Mu']
    World = RandomJittre(World,mu=SettingsMu,sigma=SettingsSigma)
    World = np.clip(World,0.0,1.0)

    Time2 = time.time()
    print('-- NOISE GENERATION COMPLETE -- [TIME(S): {}]'.format(Time2-Time1))
    return World
    


def CreateNoiseMapArgs(Settings,args,Seedrange = 100):
    return CreateNoiseMap(Settings,args.ImageSize,args.Seed,Seedrange)


def add_colour_np(world,Settings):
        #APPLY COLOUR
        Time1 = time.time()    

        Threshhold = Settings.Data['ColourData']['Data']['Treshhold']

        #GET LIST AND SORT FROM HIGH TO LOW
        Colours = list(Settings.Data['ColourData']['Colours'].values())
        Colours = sorted(Colours, key=lambda tup:(tup[3]),reverse=True)

        #MAKE MASK FOR EACH COLOUR AND APPLY TO NEW WORLD
        color_world = np.zeros(world.shape+(3,))
        for CData in Colours:

            Offset = CData[3]
            Colour = CData[0:3]

            Mask = world < Threshhold + Offset 
            color_world[Mask] = Colour

        
        Time2 = time.time()
        print('-- COLOURING IMAGE COMPLETE -- [TIME(S): {}]'.format(Time2-Time1))
        return color_world


def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--ImageSize',         default = 3000,      type=int)
    parser.add_argument('--CreateSettings',    default = False,     type=bool)
    parser.add_argument('--Seed',              default = -1,       type=int)
    args = parser.parse_args()
    
    GenPath = '../Settings.json'
    GenSettings = Settings(GenPath,args.CreateSettings)

    if(GenSettings.Initialized == True):

        NoiseMap = CreateNoiseMapArgs(GenSettings,args)
        color_world = add_colour_np(NoiseMap,GenSettings)

        img = Image.fromarray(color_world.astype(np.uint8))
        img.show()

        img.save('../GeneratedMap.PNG')
        print('-- COMPLETED MAP GENERATION --')
        
    else:
        print('-- INITIALIZING SETTINGS FAILED --')
    
    print('-- EXITING PROGRAM --')




if __name__ == '__main__':
    main()