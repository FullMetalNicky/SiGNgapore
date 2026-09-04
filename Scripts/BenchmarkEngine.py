
import os 
import re 
from MyAlgorithm import MyAlgorithm
from TaskEngine import TaskEngine
            

class BenchmarkEngine():
     
    def __init__(self, rootFolder: str, algorithm: MyAlgorithm, outputFolder: str, forceRun: bool = True):

        self.rootFolder = rootFolder
        self.algorithm = algorithm
        self.outputFolder = outputFolder
        self.forceRun = forceRun

        print("BenchmarkEngine::Ready!")

    def RunAll(self):

        envPattern = "^E(?!1b)(0|\d+)$"
        envCompiledRegex = re.compile(envPattern)

        taskPattern = "^T(?!1b)(0|\d+)$"
        taskCompiledRegex = re.compile(taskPattern)

        taskCountPerEnv = []
        taskSuccessPerEnv = []
        taskLengthsPerEnv = []
        taskOptimalLengthsPerEnv = []

        for name in os.listdir(self.rootFolder):

            if os.path.isdir(os.path.join(self.rootFolder, name)) and envCompiledRegex.search(name):
                # that's an environment folder
                envFolder = os.path.join(self.rootFolder, name)
                env = int(name.replace("E", ""))

                taskCount, taskSuccess, taskLengths = self.Run4Env(env)

                taskCountPerEnv.append(taskCount)
                taskSuccessPerEnv.append(taskSuccess)
                taskLengthsPerEnv.append(taskLengths)


    def Run4Env(self, env):

        taskCount = 0
        taskSuccess = 0
        taskLengths = []

        taskPattern = "^T(?!1b)(0|\d+)$"
        taskCompiledRegex = re.compile(taskPattern)

        envFolder = os.path.join(self.rootFolder, "E{}".format(env))

        print("BenchmarkEngine::Running benchmark for env {}".format(env))

        for dir in os.listdir(envFolder):
            if os.path.isdir(os.path.join(envFolder, dir)) and taskCompiledRegex.search(dir):
                        # that's a task folder
                    taskFolder = os.path.join(envFolder, dir)
                    task =  int(dir.replace("T", ""))

                    result = self.Run4Task(env, task)
                    taskCount += 1

                    if result != -1:
                        taskSuccess += 1
                        taskLengths.append(result)
                    else:
                        taskLengths.append(-1)


        # print("Task success rate {}/{}".format(taskSuccess, taskCount))
        # print("Task Length:" + ["{}/{}".format(taskLength[i], taskOptimalLength[i]) for i in range(taskCount)])

        return taskCount, taskSuccess, taskLengths


    def Run4Task(self, env, task):

        #print("Running Env {}, Task {}:".format(env, task))

        te = TaskEngine(self.rootFolder, env, task, self.algorithm, self.outputFolder, self.forceRun)
        result = te.Run()

        return result



def main():

    rootFolder = "/Data/" # path to the location of the dataset
    outputFolder = "/output/" #path to output folder with algorithm result logs
    algorithm = MyAlgorithm()
    be = BenchmarkEngine(rootFolder, algorithm, outputFolder)
    be.RunAll()


if __name__ == "__main__":
    main()