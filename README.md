# SiGNgapore - An Interactive Dataset for Mapless Navigation with Visual Sign Grounding

Our dataset is available for download [here](https://drive.google.com/drive/folders/19mY5V9EvInMePndl342gCu6QuMp5SbQS?usp=sharing).

## Data Manipulation
We provide, `DatasetLoader.py`, a data loading class. 
```python
from DatasetLoader import DatasetLoader

path = "/Data/" # path to the location of the dataset
sdl = DatasetLoader(path)

frameCount = sdl.getFrameCount()
for i in tqdm(range(0, frameCount)):
    rgb, depth, confidence, pose, imu = sdl.loadFramebyIndex(i) 
```

For our VQA format, it can be processed in multiple ways to accomodate different approaches.
To get the action, pixel coordinate and frame information:
```python
from DataUtils import loadVQA
from DatasetLoader import DatasetLoader

rootFolder = "/Data/" # path to the location of the dataset
sdl = DatasetLoader(rootFolder)

env = 2
scenario = 12
scenarioFolder = "{}/E{}/S{}/".format(rootFolder, env, scenario)
vqaFolder = scenarioFolder + "{}/VQA/".format(scenarioFolder)
q = loadVQA(vqaFolder)

for answer in q["answers"]:
  action = list(answer.keys())[0]
  pixelCoords = list(answer.values())[0]["point"]
  frame_id = list(answer.values())[0]["frame_id"]
  rgb, depth, confidence, pose, imu = sdl.loadFramebyIndex(frame_id) 

  # given the sparse depth image, odometry and the pixel coordinates of the grounding,
  # it can also be converted in 3D points, i.e. using open3d
  # intrinsics = sdl.getCameraCalibration()
```

To use the annotated frames as input (i.e. for end-to-end approaches):
```python
from DataUtils import loadVQA
from DatasetLoader import load_rgb

rootFolder = "/Data/" # path to the location of the dataset
env = 2
scenario = 12
scenarioFolder = "{}/E{}/S{}/".format(rootFolder, env, scenario)
vqaFolder = scenarioFolder + "{}/VQA/".format(scenarioFolder)
q = loadVQA(vqaFolder)

for answer in q["answers"]:
  frame_id = list(answer.values())[0]["frame_id"]
  imgPath = "{}/images/{:06d}.png".format(scenarioFolder, frame_id)
  img = load_rgb(imgPath)
```

## Benchmark 

To plug in your approach into the evaluation pipeline, we provide the `MyAlgorithm.py` class.
Make sure that your approach inherits from this interface, and it can seamlessly be plugged in:

```python
from MyAlgorithm import MyAlgorithm
from DataUtils import loadVQA
from DatasetLoader import DatasetLoader

class YourAlgorithm(MyAlgorithm):

    def __init__(self, outputFolder:str ):
          
        self.outputFolder = outputFolder
    
    def SetGoal(self, destination: str):
         
        self.destination = destination


    def ProcessScenario(self, rootFolder: str, env: int, sequence: int):

      # do your own thing here
      # The data for the scenario can be found at 
      scenarioFolder = "{}/E{}/S{}/".format(rootFolder, env, sequence)
      sdl = DatasetLoader(scenarioFolder)
      
      # this is how you load the VQA query 
      vqaFolder = "{}/E{}/S{}/VQA/".format(rootFolder, env, sequence)
      q = loadVQA(vqaFolder)
      
      #  do your own computation and return valid action, which is:
      #  one of the VQA options
      #  "done" to declare you determined this scenario is the destination
      #  "back" if you wish to return to the previous scenario

      action = "meow"
      return action
         
    def Clear():

        # remove all task dependent fields/data/params

        pass
```

Each task is executed using the `TaskEngine.py`:
```python
from TaskEngine import TaskEngine

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
```

`BenchmarkEngine.py` is used to run the entire benchmark:
```python
from BenchmarkEngine import BenchmarkEngine

rootFolder = "/Data/" # path to the location of the dataset
outputFolder = "/output/" #path to output folder with algorithm result logs
algorithm = MyAlgorithm()
be = BenchmarkEngine(rootFolder, algorithm, outputFolder)
be.RunAll()
```

## Cite us!
```
@article{zimmerman2026arxiv,
  title={SiGNgapore - An Interactive Dataset for Sign-based Visual Navigationm},
  author={Nicky Zimmerman and Joel Loo and Zishuo Wang and David Hsu},
  journal = {arXiv preprint},
  eprint   = {2610.09488} ,
  year={2026}
}
```




