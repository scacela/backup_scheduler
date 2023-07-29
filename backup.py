# Initiate scheduled backups for your files and directories

## Instructions

### 1. Identify the file or directory you wish to back-up

### 2. Identify a backup directory, where you wish to save your backups. Note that if you are backing up a file, the backup directory must already exist. If you are backing up a directory, the backup directory will be created automatically.

### 3. Add an entry under my_schedule using your desired parameters and backup schedule.

### 4. Run this script in a background process:

###    nohup python -u .backup.py > .backups_stdouterr.log 2>&1 &

### 5. Make note of the process id that the process is using:

###    export backups_pid=<YOUR_PROCESS_ID>

### 6. Check your process:

###    ps aux | grep $backups_pid

### 7. Check your backup location:

###    ls -a1 <YOUR_BACKUP_LOCATION>

### 8. To stop creating and deleting backups, kill the process:

###    kill -9 $backups_pid

### 9. To resume creating and deleting backups, repeat step 4.

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
