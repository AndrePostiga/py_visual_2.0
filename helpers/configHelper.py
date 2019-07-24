import json

class configHelper:

    def __init__(self):

        self.configNumber = 1
        self.configMaxNumber = self.maxNumber()
        self.currentConfig = self.selectConfig()


    def proxConfig(self):

        if (self.configNumber < self.configMaxNumber):
            self.configNumber += 1
        elif (self.configNumber == self.configMaxNumber):
            self.configNumber = 1
        else:
            self.configNumber = 1
        
        self.currentConfig = self.selectConfig()
       
    
    def selectConfig(self):        
        return self.importConfig()["{}".format(self.configNumber)]
    

    def maxNumber(self):
        return len(self.importConfig())
       

    def importConfig(self):
        configFile = ""

        with open('./config.json') as config_file:
            configFile = json.load(config_file)
        
        return configFile
    
        

        

        

            

    


