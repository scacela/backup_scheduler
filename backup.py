import os
import shutil
import datetime
import configparser
import sched
import time
import oci
from pathlib import Path

# Initialize the scheduler
scheduler = sched.scheduler(time.time, time.sleep)

# Initialize the config path location
configParser = configparser.ConfigParser
config.read("config.ini")

def get_time():
    return datetime.datetime.now().strftime("%Y%m%dT%H%M%S")

def delete_oldest_files(directory, n):
    # Get a list of all files in the directory and its subdirectories
    all_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            all_files.append((file_path, os.path.getmtime(file_path)))

    # Group files by their directory
    files_by_directory = {}
    for file_path, _ in all_files:
        dir_path = os.path.dirname(file_path)
        if dir_path not in files_by_directory:
            files_by_directory[dir_path] = []
        files_by_directory[dir_path].append(file_path)

    # Iterate over directories and delete the oldest files if there are more than n files
    for dir_path, files in files_by_directory.items():
        if len(files) > n:
            # Sort by file creation time
            files.sort(key=lambda x: os.path.getctime(x))
            files_to_delete = files[:len(files) - n]
            for file_to_delete in files_to_delete:
                try:
                    os.remove(file_to_delete)
                    print(f"Deleted: {file_to_delete}")
                except Exception as e:
                    print(f"Deletion of file {file_to_delete} failed: {str(e)}")

    # Delete empty folders
    for root, dirs, _ in os.walk(directory, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if not os.listdir(dir_path):
                try:
                    os.rmdir(dir_path)
                    print(f"Deleted empty folder: {dir_path}")
                except Exception as e:
                    print(f"Deletion of empty folder {dir_path} failed: {str(e)}")

# Function to perform local backup
def perform_local_backup(source_path, destination_path, max_num_backups):
    print(f"{get_time()}: perform_local_backup(source_path={source_path}, destination_path={destination_path}")
    try:
        # Create the destination directory if it doesn't exist
        os.makedirs(destination_path, exist_ok=True)
        
        # Generate a timestamp
        timestamp = get_time()

        # Backup the file or folder
        if os.path.isfile(source_path):
            # Backup a file
            file_name = os.path.basename(source_path)
            destination_path_2 = os.path.join(destination_path, file_name)
            # Create the destination directory if it doesn't exist
            os.makedirs(destination_path_2, exist_ok=True)
            destination_path_file = os.path.join(destination_path_2, f"{timestamp}_{file_name}")            
            shutil.copy2(source_path, destination_path_file)
        elif os.path.isdir(source_path):
            folder_name = os.path.basename(source_path)
            # Upload a folder and its contents while preserving the structure
            for root, _, files in os.walk(source_path):
                for file_name in files:
                    relative_path = os.path.relpath(root, source_path)
                    destination_path_2 = os.path.join(destination_path, folder_name, relative_path, file_name)
                    # Create the destination directory if it doesn't exist
                    os.makedirs(destination_path_2, exist_ok=True)
                    destination_path_file = os.path.join(destination_path_2, f"{timestamp}_{file_name}")
                    source_file = os.path.join(root, file_name)
                    shutil.copy2(source_file, destination_path_file)
        
        print(f"{get_time()}: Local backup completed: {source_path} -> {destination_path}")
    except Exception as e:
        print(f"{get_time()}: Local backup failed: {str(e)}")
    delete_oldest_files(destination_path, max_num_backups)
    
# Function to perform Oracle Object Storage backup
def perform_object_storage_backup(source_path, object_storage_path, bucket_name, use_api_keys=True, region="us-phoenix-1", config_file_path="~/.oci/config"):
    print(f"{get_time()}: perform_object_storage_backup(source_path={source_path}, object_storage_path={object_storage_path}, bucket_name={bucket_name}, use_api_keys={use_api_keys}, region={region})")
    try:
        retry_strategy = oci.retry.DEFAULT_RETRY_STRATEGY

        if use_api_keys:
            # Load the OCI configuration from the config file
            config = oci.config.from_file(config_file_path)
            
            object_storage = oci.object_storage.ObjectStorageClient(config=config, retry_stratefy=retry_strategy, timeout=60)
        else:
            signer = oci.auth.signers.get_resource_principals_signer()
            object_storage = oci.object_storage.ObjectStorageClient(config={}, signer=signer, retry_strategy=retry_strategy, timeout=60)
        
        namespace_name = object_storage.get_namespace().data

        # Generate a timestamp
        timestamp = get_time()
        
        object_name = None
        # Upload file or folder to Object Storage
        if os.path.isfile(source_path):
            # Upload a file
            file_name = os.path.basename(source_path)
            object_name = os.path.join(object_storage_path, file_name, f"{timestamp}_{file_name}")
            with open(source_path, "rb") as file:
                object_storage.put_object(namespace_name, bucket_name, object_name, file)
        elif os.path.isdir(source_path):
            folder_name = os.path.basename(source_path)
            # Upload a folder and its contents while preserving the structure
            for root, _, files in os.walk(source_path):
                for file_name in files:
                    relative_path = os.path.relpath(root, source_path)
                    object_name = os.path.join(object_storage_path, folder_name, relative_path, file_name, f"{timestamp}_{file_name}")
                    source_file = os.path.join(root, file_name)
                    with open(source_file, "rb") as file:
                        object_storage.put_object(namespace_name, bucket_name, object_name, file)
        
        print(f"{get_time()}: Object Storage backup completed: {source_path} -> {bucket_name}:{object_name}")
    except Exception as e:
        print(f"{get_time()}: Object Storage backup failed: {str(e)}")

# Function to schedule backups
def handle_backups(section):
    print(f"{get_time()}: handle_backups(section={section})")
        
    source_path = config.get(section, "source_path")
    destination_path = config.get(section, "destination_path")
    backup_to_object_storage = config.getboolean(section, "backup_to_object_storage")
    bucket_name = config.get(section, "bucket_name")
    region = config.get(section, "region")
    use_api_keys = config.getboolean(section, "use_api_keys")
    max_num_backups = int(config.get(section, "max_num_backups"))

    if backup_to_object_storage:
        perform_object_storage_backup(source_path, destination_path, bucket_name, use_api_keys, region)
    else:
        perform_local_backup(source_path, destination_path, max_num_backups)

    schedule_type = config.get(section, "schedule_type")
    schedule_value = config.get(section, "schedule_value")            

    # Calculate the next occurrence time
    next_occurrence = get_next_occurrence(schedule_type, schedule_value)

    # Schedule the next backup
    scheduler.enterabs(next_occurrence, 1, handle_backups, (section,)) # the reason for the comma after the single element is that it makes it so that the action args are the tuple, rather than the single element inside it

# Calculate the next occurrence time based on schedule type and value
def get_next_occurrence(schedule_type, schedule_value):
    now = datetime.datetime.now()
    
    if schedule_type == "weekly":
        day_map = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6
        }
        day_of_week = day_map.get(schedule_value.lower(), 0)
        next_occurrence = now.replace(hour=0, minute=0, second=0, microsecond=0)
        next_occurrence += datetime.timedelta(days=(day_of_week - now.weekday()) % 7)
    elif schedule_type == "daily":
        hour = int(schedule_value)
        next_occurrence = now.replace(minute=0, second=0, microsecond=0, hour=hour)
        if now >= next_occurrence:
            next_occurrence += datetime.timedelta(days=1)
    elif schedule_type == "hourly":
        minute = int(schedule_value)
        next_occurrence = now.replace(second=0, microsecond=0, minute=minute)
        if now >= next_occurrence:
            next_occurrence += datetime.timedelta(hours=1)
    elif schedule_type == "minutely":
        second = int(schedule_value)
        next_occurrence = now.replace(microsecond=0, second=second)
        if now >= next_occurrence:
            next_occurrence += datetime.timedelta(minutes=1)
    
    return time.mktime(next_occurrence.timetuple())

def main():
    # Schedule the initial backup
    for section in config.sections():
        
        schedule_type = config.get(section, "schedule_type")
        schedule_value = config.get(section, "schedule_value")            
            
        # Calculate the next occurrence time
        next_occurrence = get_next_occurrence(schedule_type, schedule_value)
        
        # Schedule the next backup
        scheduler.enterabs(next_occurrence, 1, handle_backups, (section,)) # the reason for the comma after the single element is that it makes it so that the action args are the tuple, rather than the single element inside it
    
    print(f"{get_time()}: About to start the scheduler")
    
    scheduler.run()

    print("All jobs completed.")

if __name__ == "__main__":
    main()
