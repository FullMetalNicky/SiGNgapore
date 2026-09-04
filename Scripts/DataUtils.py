
import os
import cv2
from tqdm import tqdm
import json

def video_to_frames(video, path_output_dir):
   
    if not os.path.isdir(path_output_dir):
        os.makedirs(path_output_dir, exist_ok=True)

    vidcap = cv2.VideoCapture(video)

    total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    files = [f for f in os.listdir(path_output_dir) if os.path.isfile(os.path.join(path_output_dir, f))]
    #print(len(files), total_frames)
    if len(files) == total_frames - 1:
        print("Images already exported!")
        return


    count = 0
    total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))

    for count in tqdm(range(total_frames)):

    #while vidcap.isOpened():
        success, image = vidcap.read()
        if success:
            cv2.imwrite(os.path.join(path_output_dir, '%06d.png') % count, image)
            count += 1
        else:
            break
    #cv2.destroyAllWindows()
    vidcap.release()


def getMissionGoals(rootFolder, env):

    goals = []
    tasks = loadTasks(rootFolder, env)

    for task in tasks:
        goals.append(task["destination"])

    goals = set(goals)

    return goals


def matchGoal2Sign(goal, sign):

    locations = [loc for loc, dir in sign.items()]
    from thefuzz import process
    matches = process.extract(goal.lower(), locations, limit=3)
    #print(goal.lower(), matches[0][0], matches[0][1])

    if matches[0][1] >= 90:
        return True, matches[0][0]
    else:
        return False, None


def getTaskNumber(rootFolder, env):

    pattern = "^T(?!1b)(0|\d+)$"
    compiledRegex = re.compile(pattern)
    envPath = rootFolder + "E{}/".format(env)
    taskCnt = 0

    for dirpath, dirnames, filenames in os.walk(envPath):

        dirnames = sorted(dirnames)

        for dirname in dirnames:
            if compiledRegex.search(dirname):
                taskCnt += 1

    return taskCnt

def loadTasks(rootFolder, env):

    tasks = []
    taskNum = getTaskNumber(rootFolder, env)
    for t in range(1, taskNum + 1):
        tasks.append(loadTask(rootFolder, env, t))
    return tasks

def loadTask(rootFolder, env, t):

    taskJsonPath = "{}/E{}/T{}/".format(rootFolder, env, t)
    with open(taskJsonPath + "task.json", 'r') as f:
        task = json.load(f)
    return task

def loadTaskGT(rootFolder, env, t):

    taskJsonPath = "{}/E{}/T{}/".format(rootFolder, env, t)
    with open(taskJsonPath + "GT.json", 'r') as f:
        task = json.load(f)
    return task["GT"]

def loadGTs(rootFolder, env):

    tasks = []
    taskNum = getTaskNumber(rootFolder, env)
    for t in range(1, 1+taskNum):
        tasks.append(loadTaskGT(rootFolder, env, t))
    return tasks


def getScenarioGrounding(projectFolder, env, scenario, destination):

    responsePath = projectFolder + "/E{}/S{}/clustered/response.json".format(env, scenario)
    if not os.path.isfile(responsePath):
        return None
    with open(responsePath, 'r') as f:
        response = json.load(f)
    #print(response)

    if destination in response:
        return response[destination]

    return None

def getTaskLog(projectFolder, env, task):

    taskLogPath = projectFolder + "/E{}/T{}/task.json".format(env, task)
    if not os.path.isfile(taskLogPath):
        return None
    with open(taskLogPath, 'r') as f:
        taskLog = json.load(f)
    
    return taskLog