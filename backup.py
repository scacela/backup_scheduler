# Save backups of your files and folders on a scheduled basis to your local environment. Specify the maximum number of backups to retain, and automatically dump the oldest backups.

## Instructions

### 1. Edit entries under the my_schedule function to include the file or directory you wish to back-up, the directory to which you will save backups, and the maximum number of the most recent backups you wish to retain.

### 2. Run this script in a background process:

###    nohup python -u backup.py > .backups_stdouterr.log 2>&1 &

### 3. Capture the process ID that the process is using:

###    export backups_pid=YOUR_PROCESS_ID

### 4. Monitor the status of your process:

###    ps aux | grep $backups_pid

### 5. Monitor your backup directory for backups:

###    ls -a1 /path/to/your/backup/directory

### 6. To stop creating and deleting backups, terminate the process:

###    kill -9 $backups_pid

### 7. To resume creating and deleting backups, repeat step 2.

import os
import sys
import schedule
from time import sleep
import shutil
import datetime

def create_backup(filepath, backup_dir, max_num_backups=4):
    date_suffix=datetime.datetime.today().strftime("%Y_%m_%d_%H:%M:%S")

    if os.path.isfile(filepath):
      shutil.copyfile(filepath, f"{backup_dir}/{os.path.basename(filepath)}.{date_suffix}")
    elif os.path.isdir(filepath):
      shutil.copytree(filepath, f"{backup_dir}/{os.path.basename(filepath)}.{date_suffix}", dirs_exist_ok=True)
    
    delete_backup(filepath, backup_dir, max_num_backups)

def delete_backup(filepath, backup_dir, max_num_backups):
    
    list_of_files = os.listdir(backup_dir)
    full_path = ["{0}/{1}".format(backup_dir, x) for x in list_of_files]

    if len(list_of_files) > max_num_backups:
        
        oldest_file = min(full_path, key=os.path.getctime)
        
        if os.path.isfile(filepath):
          os.remove(oldest_file)
        elif os.path.isdir(filepath):
          shutil.rmtree(oldest_file)

def my_schedule():

    # Back-up a file or directory to directory_A at the first minute of every hour, and retain backups up to one week old.
    schedule.every().hour.at(":00").do(create_backup,"/path/to/file_or_directory/to/backup", "/path/to/backup/directory_A", 168)

    # Back-up a file or directory to directory_B every 12 minutes, and retain backups up to three days old.
    schedule.every(12).minutes.do(create_backup,"/path/to/file_or_directory/to/backup", "/path/to/backup/directory_B", 360)

def main():
    my_schedule()
    while True:
        schedule.run_pending()
        sleep(1)

if __name__ == '__main__':
    main()
