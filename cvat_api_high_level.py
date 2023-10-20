import cvat_sdk
import requests
import os
from cvat_sdk.api_client import Configuration, ApiClient, exceptions
from cvat_sdk.api_client.models import *
import time
import utils
from tqdm import tqdm
import json

class CVAT:
    def __init__(self, cvat_server, cvat_username, cvat_password):
        self.cvat_server = cvat_server
        self.cvat_username = cvat_username
        self.cvat_password = cvat_password

        # Http request
        self.auth_token = self._authenticate()
        self.configuration = Configuration(
            host=self.cvat_server,
            username=self.cvat_username,
            password=self.cvat_password,
        )

        # Low level api
        self._initialize_client()

    def _authenticate(self):
        auth = requests.post(
            f"{self.cvat_server}/api/auth/login",
            json={"username": self.cvat_username, "password": self.cvat_password},
        )

        return auth.json()["key"]

    def create_project(self, project_name):
        with ApiClient(self.configuration) as api_client:
            project_write_request = ProjectWriteRequest(
                name=project_name,
            )
            try:
                result, response = api_client.projects_api.create(
                    project_write_request=project_write_request,
                )
            except exceptions.ApiException as e:
                print("Exception when calling ProjectsApi.create(): %s\n" % e)
                return None

            return response.json()["id"]

    def add_labels_to_project(self, project_id, labels):
        headers = {"Authorization": f"Token {self.auth_token}"}
        url = f"{self.cvat_server}/api/projects/{project_id}"
        data_temp = [
            {
                "name": label["name"],
                "attributes": [],
                "color": label["color"],
                "multi_shapes": False,
                "type": label["type"],
            }
            for label in labels
        ]
        data_temp2 = {"labels": data_temp}
        response = requests.patch(url, headers=headers, json=data_temp2)
        return response.json()

    def create_task(self, project_id, task_name, assignee_id):
        with ApiClient(self.configuration) as api_client:
            task_write_req = TaskWriteRequest(
                name=task_name,
                project_id=project_id,
                assignee_id=assignee_id,
                source_storage=PatchedTaskWriteRequestTargetStorage(
                    LocationEnum="local"
                ),
            )
            try:
                (result, response) = api_client.tasks_api.create(
                    task_write_request=task_write_req
                )

            except exceptions.ApiException as e:
                print("Exception when calling TasksApi.create(): %s\n" % e)
                return None
        return response.json()["id"]

    def upload_images_to_task(self, task_id, image_path, image_ls):
        with ApiClient(self.configuration) as api_client:
            id = task_id  # Replace with the task ID where you want to upload the images
            upload_finish = True
            upload_multiple = True
            upload_start = True

            # List all image files in the specified directory
            image_files = [
                open(os.path.join(image_path, filename), "rb")
                for filename in image_ls
                if filename.endswith(".png")
            ]

            data_request = DataRequest(
                image_quality=100,
                compressed_chunk_type=ChunkType("imageset"),
                client_files=image_files,
            )

            try:
                result, response = api_client.tasks_api.create_data(
                    id,
                    upload_finish=upload_finish,
                    upload_multiple=upload_multiple,
                    upload_start=upload_start,
                    data_request=data_request,
                    _content_type="multipart/form-data",
                )
            except exceptions.ApiException as e:
                print("Exception when calling TasksApi.create_data(): %s\n" % e)
            return response.json()

    def import_annotations_to_task(self, task_id, annotations_file_path):
        self.task_var = self.client.tasks.retrieve(task_id)
        self.task_var.import_annotations("COCO 1.0", annotations_file_path)

    def _initialize_client(self):
        self.client = cvat_sdk.make_client(
            self.cvat_server,
            credentials=(self.cvat_username, self.cvat_password),
        )

    def check_uploaded_images_number(self, task_id):
        headers = {"Authorization": f"Token {self.auth_token}"}
        response = requests.get(f"{self.cvat_server}/api/tasks/{task_id}", headers=headers)

        if "size" in response.json().keys():
            return response.json()["size"]
        else:
            return None

def main():
    time_starting_api = time.time()
    # Initialize the task manager
    cvat_api = CVAT(cvat_server, cvat_username, cvat_password)

    # Create a project
    if create_project:
        project_id = cvat_api.create_project(project_config['name'])
        cvat_api.add_labels_to_project(project_id, project_config['labels'])
    else:
        print("Project id: ")
        project_id = input()

    ann_ls = utils.split_coco(annotations_file_path, annotations_dest ,segment_size)

    # Create tasks
    number_of_tasks = number_of_images//segment_size + 1
    print("Creating tasks according to segment size...")
    for file_id in tqdm(range(number_of_tasks)):
        if create_task:
            task_id = cvat_api.create_task(project_id, task_config['name'], task_config['assignee_id'])
        else:
            print("Task id to upload annotation: ")
            task_id = input()
            
        ann_file_in_this_iter = ann_ls[0]

        with open(ann_file_in_this_iter, "r") as f:
            ann_file = json.load(f)
        
        image_ls = [file["file_name"] for file in ann_file["images"]]

        # Upload data to the task
        response = cvat_api.upload_images_to_task(task_id, image_path, image_ls)
        start = time.time()
        while cvat_api.check_uploaded_images_number(task_id) != len(image_ls):
            time.sleep(1)
        end = time.time()
        print("Successfully uploaded {} images to task '{}' in {} seconds".format(len(image_ls), task_id, end - start))

        # Upload annotation to the task
        import_annotation_start_time = time.time()
        cvat_api.import_annotations_to_task(task_id, ann_file_in_this_iter)
        import_annotation_end_time = time.time()
        print("Successfully uploaded annotations to task '{}' in {} seconds".format(task_id, import_annotation_end_time - import_annotation_start_time))
    time_ending_api = time.time()

    print("Total time for API called: {} seconds".format(time_ending_api - time_starting_api))

if __name__ == "__main__":

     # User-defined parameters
    cvat_server = "http://10.80.42.221:8080"
    cvat_username = "george0725"
    cvat_password = "2CfN7evgFMsFU7g"
    image_path = "/home/yusuff/Desktop/Changi_Project/Changi_dataset/20230918_Dataset_Group1/test_imgs"
    annotations_file_path = "/home/yusuff/Desktop/Changi_Project/Changi_dataset/20230918_Dataset_Group1/gt.json"
    annotations_dest = "/home/yusuff/Desktop/Changi_Project/Changi_dataset/20230918_Dataset_Group1/gt_splits"
    project_config = {
        "name": "Changi_Project",
        "labels": [  
            {"name": "car", "color": "#2080c0", "type": "rectangle"},
            {"name": "person", "color": "#c06060", "type": "rectangle"},
            {"name": "truck", "color": "#906080", "type": "rectangle"},
            {"name": "special_automobile", "color": "#34d1b7", "type": "rectangle"},
        ],
    }
    task_config = {
        "name": "Testing_subset",
        "assignee_id": 3,
    }
    segment_size = 500
    number_of_images = len([img for img in os.listdir(image_path) if img.endswith(".png") or img.endswith(".jpg")])

    # If False, user needs to input proj/task_id
    create_project = True
    create_task = True

    main()
