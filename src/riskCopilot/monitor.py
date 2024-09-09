from metaflow import FlowSpec, step, card, Parameter
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
import subprocess
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


extentions = [".pdf"]
modified_files = []


class FolderChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        file_path = event.src_path
        current_directory = os.getcwd()
        file_path = file_path.replace(current_directory + "/", "")
        file_extension = os.path.splitext(file_path)[1]
        if file_extension in extentions and event.event_type in ["created", "modified"]:
            modified_files.append(file_path)


def list_files_with_extensions(folder_path, extensions):

    matching_files = []

    # Ensure all extensions start with a dot
    extensions = [ext if ext.startswith(".") else "." + ext for ext in extensions]

    # Walk through the directory
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # Check if the file has one of the specified extensions
            if any(file.endswith(ext) for ext in extensions):
                matching_files.append(os.path.join(root, file))

    return matching_files


def monitor_folder(folder_path):

    global modified_files  # Declare modified_files as global

    # loading the exsisting files
    files = list_files_with_extensions(folder_path, extentions)

    input_list_str = ",".join(map(str, files))

    if len(files) > 0:
        command = [
            "python3",
            "./src/riskCopilot/pipeline.py",
            "run",
            "--files",
            input_list_str,
        ]
        subprocess.run(command)

    # Observing the files
    event_handler = FolderChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(5)  # Wait for an hour (3600 seconds)

            if len(modified_files) > 0:
                # making sure we have only the unique values
                modified_files = list(set(modified_files))

                print("Files modified in the last hour:")

                # convert to string
                input_list_str = ",".join(map(str, modified_files))

                # run data pipeline on the updated or newly added folders
                command = ["python", "./src/riskCopilot/pipeline.py", "run", "--files", input_list_str]
                subprocess.run(command)

                # Clear the list for the next hour
                modified_files.clear()

    except KeyboardInterrupt:
        observer.stop()
    observer.join()


# Specify the folder path to monitor
folder_path = "./data/raw"  # mention this in the '.env' file

# Start monitoring the folder
monitor_folder(folder_path)
