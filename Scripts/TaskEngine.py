
from DatasetLoader import DatasetLoader
from DataUtils import video_to_frames
import json
from networkx.readwrite import json_graph
import networkx as nx
import os
from collections import deque

from MyAlgorithm import MyAlgorithm



class TaskEngine():
     
    def __init__(self, rootFolder: str, env: int, task: int, algorithm: MyAlgorithm, outputFolder: str, forceRun: bool = True):
    
        self.taskJsonPath = "{}/E{}/T{}/".format(rootFolder, env, task)
        with open(self.taskJsonPath + "task.json", 'r') as f:
            self.task = json.load(f)

        self.destination = [self.task["destination"]]
        self.algorithm = algorithm
        self.env = env
        self.taskID = task
        self.outputFolder = outputFolder
        self.taskLogFolder = "{}/E{}/T{}/".format(self.outputFolder, self.env, self.taskID)

        self.taskLog = []
        self.forceRun = forceRun

        self.rootFolder = rootFolder
        self.G = json_graph.node_link_graph(self.task["graph"])
        print("TaskEngine::Ready for task {}!".format(self.taskID))
       

    def verifyAction(self, env: int , scenario: int, answer: str):

        vqaFolder = "{}/E{}/S{}/VQA/".format(self.rootFolder, env, scenario)
        scenarioJson = vqaFolder + "query.json"
        q = {}
        with open(scenarioJson, 'r') as f:
            q = json.load(f)

        possibleAnswers = [list(a.keys())[0] for a in q["answers"]]
        possibleAnswers.append("done")
        possibleAnswers.append("back")

        if answer in possibleAnswers:
            return True
        else:
            return False
        

    def logTask(self, scenario: int, action: str):

        self.taskLog.append({scenario : action})
        if not os.path.exists(self.taskLogFolder):
            os.makedirs(self.taskLogFolder)

        with open(self.taskLogFolder + "log.json", 'w') as json_file:
            json.dump(self.taskLog, json_file, indent=4)

    def Run(self):

        stardID = self.task["startID"]
        endID = self.task["endID"]
        currID = stardID
        stepCnt = 1

        if not self.forceRun and os.path.exists(self.taskLogFolder + "log.json"): # task log already exists and we are happy with it, we can just load it
            with open(self.taskLogFolder + "log.json", 'r') as f:
                taskLog = json.load(f)

            if (taskLog.keys()[-1] == endID) and (taskLog.values()[-1] == "done"):
                stepCnt = len(taskLog)
                return stepCnt
            else:
                return -1
        else:
            scenarioStack = deque()

            # init your algo with the destination
            self.algorithm.SetGoal(self.destination)
            scenarioStack.append(currID)

            while True:

                if currID == 666: # these are deadend nodes
                    print("TaskEngine::Task {} failed due to wrong action, dead end!".format(self.taskID ))
                    return -1
                
                if "type" in self.G.nodes[currID] and self.G.nodes[currID]["type"] == "terminal": # these are terminal nodes without scenario
                    if currID == endID:
                        self.logTask(currID, "done")
                        print("TaskEngine::Task {} finished successfully with {} steps!".format(self.taskID, stepCnt ))
                        self.done = True
                        return stepCnt

                if stepCnt > 50:
                    print("TaskEngine::Task {} failed due to lengthy execution!".format(self.taskID ))
                    return -1
                
                action = self.algorithm.ProcessScenario(self.rootFolder, self.env, currID)
                self.logTask(currID, action)
            
                if not self.verifyAction(self.env, currID, action):
                    print("TaskEngine::Task {} failed due to invalid action!".format(self.taskID ))
                    return -1

                if action == "done":
                    if currID == endID:
                        print("TaskEngine::Task {} finished successfully with {} steps!".format(self.taskID, stepCnt ))
                        self.done = True
                        return stepCnt
                    else:
                        print("TaskEngine::Task {} failed due to incorrect termination!".format(self.taskID ))
                        return -1
                elif action == "back":
                    currID = scenarioStack.pop()
                    continue
                else:
                    currID = [v for u, v, data in self.G.edges(currID, data=True) if (data["action"] == action)][0]
                    scenarioStack.append(currID)
                    
                stepCnt += 1

               
                





def main():


    rootFolder = "/Data/" # path to the location of the dataset
    outputFolder = "/output/" #path to output folder with algorithm result logs
    env = 2


    algorithm = MyAlgorithm()

    for task in range(1, 5):
        te = TaskEngine(rootFolder, env, task, algorithm, outputFolder)
        try:
            te.Run()  
        except Exception as e:
            print(e)

    

    




if __name__ == "__main__":
    main()

