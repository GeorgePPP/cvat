# CVAT Object Detection Project Automation

### This Python script automates the process of setting up and managing tasks in the Computer Vision Annotation Tool (CVAT) for an object detection project. It includes functionalities to create projects, add labels, create tasks, upload images, and import annotations.

## Dependencies
- cvat_sdk
    - Server version: 2.6.2

    - Core version: 11.0.3

    - Canvas version: 2.17.5

    - UI version: 1.56.0
- requests
- os
- pathlib
- time
- utils
- tqdm
- json

## How it works
1. Create a project
2. Upload labels to the project
3. Partition images into n files 
4. Create a task
5. Upload images to the task
6. Upload annotations to the task
7. Repeat 4-7 for each file

## A few facts about CVAT server
1. Project_id - The project_id is assigned based on the order of creation. The first project created gets project_id 1, the second gets project_id 2, and so on. If you create a project with project_id 5, delete it, and then create another, the new one will be assigned project_id 6.
2. The same rule in 1 applies to task creation
3. In Task Creation, segmentation can create multiple jobs, but each job can only be assigned to one annotator at a time.
4. The segmentation function is not available for Project creation.

## User-defined parameters
### Authentication 
```python
cvat_server = "http://10.80.42.221:8080"
cvat_username = "george0725"
cvat_password = "2CfN7evgFMsFU7g"
```

### Project Creation
```python
create_project = True
project_config = {
        "name": "Changi_Project",
        "labels": [  
            {"name": "car", "color": "#2080c0", "type": "rectangle"},
            {"name": "person", "color": "#c06060", "type": "rectangle"},
            {"name": "truck", "color": "#906080", "type": "rectangle"},
            {"name": "special_automobile", "color": "#34d1b7", "type": "rectangle"},
        ],
    }
```
When you create a new project, this code will automatically generate a project ID and return it for task creation. For semi-annotation, you need to provide labels for project. When you upload annotations to the server, it will use the label names and their corresponding bounding box colors based on the information you've provided. This code only provides two config options for project creation, **name** and **labels**.

### Task Creation
```python
create_task = True
task_config = {
    "name": "Testing_subset",
    "assignee_id": 3,
}
```

### Upload dataset to task
```python
segment_size = 500
image_path = "/home/yusuff/Desktop/Changi_Project/Changi_dataset/20230918_Dataset_Group1/test_imgs"
```
* "segment size" refers to the number of images you want to include in each task when splitting them. 
* "image_path" refers to the directory where all the images are stored  

### Upload annotation to task
```python
annotations_file_path = "/home/yusuff/Desktop/Changi_Project/Changi_dataset/20230918_Dataset_Group1/gt.json"
annotations_dest = "/home/yusuff/Desktop/Changi_Project/Changi_dataset/20230918_Dataset_Group1/gt_splits"
```
* "annotations_file_path" is the location or directory where your **COCO** annotation file is stored.
* "annotations_dest" is the directory where you want to cache your annotation file while it is being split into different annotation files, each containing annotation information for different images.


## Reference
https://app.cvat.ai/api/docs/  
https://opencv.github.io/cvat/docs/api_sdk/sdk/highlevel-api/