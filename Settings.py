import os
import json


class Settings():
    def CreateJittreDict(self):
        JittreValues = {}

        JittreValues['Mu'] = 1.0
        JittreValues['Sigma'] = 0.03

        return JittreValues

    def CreateColourDict(self):
        Colours = {}
        Data = {}

        #[ R, G, B, OFFSET(range 0->1) ]
        Colours['blue'] = [0,62,178, 0.03]
        Colours['lightblue'] = [9, 82, 198, 0.05]
        Colours['sandy'] = [194, 178, 129, 0.055]
        Colours['beach'] = [164, 148, 99, 0.1]
        Colours['green'] = [90, 127, 50, 0.25]
        Colours['darkgreen'] = [0,100,0, 0.6]
        Colours['mountain'] = [140, 142, 123,0.7]
        Colours['snow'] = [255, 250, 250, 1.0]

        #misc data
        Data['Treshhold'] = 0.0
        
        #combine because python
        Combined = {}
        Combined['Colours'] = Colours
        Combined['Data'] = Data
        return Combined

    def CreateSettings(self):
        Values = {}

        #STANDARD VALUES
        Values['ScalePP'] = 0.1
        Values['Octaves'] = 7
        Values['Lacunarity'] = 2
        Values['Persistence'] = 0.5

        Values['ColourData'] = self.CreateColourDict()
        Values['JittreData'] = self.CreateJittreDict()

        return Values

    def __init__(self,Path,RegenFile = False):

        abspath = os.path.abspath(Path)

        self.Path = Path
        self.Data = {}
        self.Initialized = False

        try:
            #OPEN SETTINGS FILE ON DRIVE
            with open(abspath,mode='r') as f:
                fdata = json.load(f)
                self.Data = fdata
            self.Initialized = True

        except Exception as e:
            print("-- Error: {} --".format(e))
            if(RegenFile):
                print('-- CREATING NEW SETTINGS FILE --')
                NewSettings = self.CreateSettings()
                self.Data = NewSettings
                with open(abspath,mode='w') as f:
                    json.dump(NewSettings,f,indent=2)
                self.Initialized = True

