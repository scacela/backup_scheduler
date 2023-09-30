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

def get_time():
    return datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

def delete_oldest_files(directory, n):
    # Get a list of all files in the directory and its subdirectories
    all_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            all_files.append((file_path, os.path.getmtime(file_path)))

    # Sort the files by modification time in ascending order
    all_files.sort(key=lambda x: x[1])

    # Delete the oldest n files
    for i in range(n):
        if i < len(all_files):
            file_to_delete = all_files[i][0]
            try:
                os.remove(file_to_delete)
                print(f"{get_time()}: Deleted: {file_to_delete}")
            except Exception as e:
                print(f"{get_time()}: Local deletion of top {n} oldest files {file_to_delete} failed: {str(e)}")
                
    # Delete empty folders
    for root, dirs, _ in os.walk(directory, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if not os.listdir(dir_path):
                try:
                    os.rmdir(dir_path)
                    print(f"{get_time()}: Deleted empty folder: {dir_path}")
                except Exception as e:
                    print(f"{get_time()}: Local deletion of empty folder {dir_path} failed: {str(e)}")

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
            destination_path_file = os.path.join(destination_path_2, f"{file_name}.{timestamp}")            
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
                    destination_path_file = os.path.join(destination_path_2, f"{file_name}.{timestamp}")
                    source_file = os.path.join(root, file_name)
                    shutil.copy2(source_file, destination_path_file)
        
        print(f"{get_time()}: Local backup completed: {source_path} -> {destination_path}")
    except Exception as e:
        print(f"{get_time()}: Local backup failed: {str(e)}")
    delete_oldest_files(destination_path, max_num_backups)
    
# Function to perform Oracle Object Storage backup
def perform_object_storage_backup(source_path, object_storage_path, bucket_name, use_api_keys=True, region="us-phoenix-1"):
    print(f"{get_time()}: perform_object_storage_backup(source_path={source_path}, object_storage_path={object_storage_path}, bucket_name={bucket_name}, use_api_keys={use_api_keys}, region={region})")
    try:
        retry_strategy = oci.retry.DEFAULT_RETRY_STRATEGY

        if use_api_keys:
            # Specify the path to your OCI config file
            config_file = "/home/datascience/.oci/config"  # Update with the actual path to your config file

            # Load the OCI configuration from the config file
            config = oci.config.from_file(config_file)
            
            object_storage = oci.object_storage.ObjectStorageClient(config=config, retry_stratefy=retry_strategy, timeout=60)
        else:
            signer = oci.auth.signers.get_resource_principals_signer()
            object_storage = oci.object_storage.ObjectStorageClient(config={}, signer=signer, retry_strategy=retry_strategy, timeout=60)
        
        namespace_name = object_storage.get_namespace().data

        # Generate a timestamp
        timestamp = get_time()
        
        # Upload file or folder to Object Storage
        if os.path.isfile(source_path):
            # Upload a file
            file_name = os.path.basename(source_path)
            object_name = os.path.join(object_storage_path, file_name, f"{file_name}.{timestamp}")
            with open(source_path, "rb") as file:
                object_storage.put_object(namespace_name, bucket_name, object_name, file)
        elif os.path.isdir(source_path):
            folder_name = os.path.basename(source_path)
            # Upload a folder and its contents while preserving the structure
            for root, _, files in os.walk(source_path):
                for file_name in files:
                    relative_path = os.path.relpath(root, source_path)
                    object_name = os.path.join(object_storage_path, folder_name, relative_path, file_name, f"{file_name}.{timestamp}")
                    source_file = os.path.join(root, file_name)
                    with open(source_file, "rb") as file:
                        object_storage.put_object(namespace_name, bucket_name, object_name, file)
        
        print(f"{get_time()}: Object Storage backup completed: {source_path} -> {bucket_name}:{object_name}")
    except Exception as e:
        print(f"{get_time()}: Object Storage backup failed: {str(e)}")

# Function to schedule backups
def handle_backups(section):
    print(f"{get_time()}: handle_backups(section={section})")
    # Read configuration from a config file
    config = configparser.ConfigParser()
    config.read("config.ini")  # Adjust the config file path as needed
        
    source_path = config.get(section, "source_path")
    destination_path = config.get(section, "destination_path")
    backup_to_object_storage = config.getboolean(section, "backup_to_object_storage")
    bucket_name = config.get(section, "bucket_name")
    region = config.get(section, "region")
    use_api_keys = config.getboolean(section, "use_api_keys")
    max_num_backups = config.get(section, "max_num_backups")

    if backup_to_object_storage:
        params = (source_path, destination_path, bucket_name, use_api_keys, region)
        perform_object_storage_backup(source_path, destination_path, bucket_name, use_api_keys, region)
    else:
        perform_local_backup(source_path, destination_path, max_num_backups)

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

# Main function to start the scheduler and set the backup schedule
def schedule_and_run_jobs():
    try:
        # Read schedule configuration from a config file
        config = configparser.ConfigParser()
        config.read("config.ini")  # Adjust the config file path as needed
        
        print(f"{get_time()}: About to configure schedules for each config section")

        next_occurrences=[]
        
        # Schedule backups based on user configuration
        for section in config.sections():
            schedule_type = config.get(section, "schedule_type")
            schedule_value = config.get(section, "schedule_value")            
            
            # Calculate the next occurrence time
            next_occurrence = get_next_occurrence(schedule_type, schedule_value)

            next_occurrences.append(next_occurrence)
            
            # Schedule the next backup
            scheduler.enterabs(next_occurrence, 1, handle_backups, (section,)) # the reason for the comma after the single element is that it makes it so that the action args are the tuple, rather than the single element inside it
        
        # Get the soonest next occurrences so that this function doesn't get called more often than necessary
        soonest_next_occurrence = min(next_occurrences)
        print(f"{get_time()}: soonest_next_occurrence: {soonest_next_occurrence}")
            
        # Schedule the next backup
        scheduler.enterabs(soonest_next_occurrence, 1, schedule_and_run_jobs, ())
            
    except Exception as e:
        print(f"{get_time()}: An error occurred: {str(e)}")

def main():
    
    # Schedule the initial backup
    scheduler.enter(0, 1, schedule_and_run_jobs, ())

    print(f"{get_time()}: About to start the scheduler")
    
    scheduler.run()

    print("All jobs completed.")

if __name__ == "__main__":
    main()
