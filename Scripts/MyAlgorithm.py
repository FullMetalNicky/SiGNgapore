
import json 
import os


class MyAlgorithm():

    def __init__(self):
          
        pass
    
    def SetGoal(self, destination: str):
         
        self.destination = destination

    def ProcessScenario(self, rootFolder: str, env: int, sequence: int):
         
        scenarioFolder = "{}/E{}/S{}/".format(rootFolder, env, sequence)
        vqaFolder = "{}/E{}/S{}/VQA/".format(rootFolder, env, sequence)
         
        # process the raw data to build your representation 

        scenarioJson = vqaFolder + "query.json"
        q = {}
        with open(scenarioJson, 'r') as f:
            q = json.load(f)


        # use the VQA information and the destination to determine the next action
        action = "D"

        # actions must be a letter from the possible VQA query file, "back" when backtracking or "done" when detecting the destination 

        return action
    
    def Clear(self):

        # remove all task dependent fields/data/params

        pass




