# backup_scheduler
Save timestamped backups of your files and folders on a scheduled basis to your local environment or remotely to Oracle Object Storage. For local backups, specify the maximum number of backups to retain, and automatically dump the oldest backups. Manage your Oracle Object Storage backups using Oracle Object Storage Lifecycle Policy Rules and Retention Rules.

## Prerequisites

1. Clone this repository.
	
 	```
	git clone https://github.com/scacela/backup_scheduler.git
	```

2. For use with Oracle Object Storage, ensure that your environment is authenticated for the Object Storage connection. This script leverages resource principal authentication by default.

## Usage Instructions

1. Edit the entries under the `my_schedule` function to include the file or directory for which you wish to save timestamped back-ups on a scheduled basis to your local environment or remotely to Oracle Object Storage.

2. Run this script in a background process. Make a note of the process ID that your process is using.
	
 	```
	nohup python -u backup.py > backup_stdouterr.log 2>&1 &
	```
 
3. Capture the process ID that the process is using, replacing the placeholder `MY_PROCESS_ID` with your own.
	
 	```
	export backup_pid=MY_PROCESS_ID
	```
 
4. Monitor the status of your process:
	
 	```
	ps aux | grep $backup_pid
	```
 
5. Monitor your backup location in Oracle Object Storage, or use the following command to monitor a backup location within your local environment. Replace the placeholder `MY_LOCAL_BACKUP_LOCATION` with your own.
	
 	```
	ls -a1 MY_LOCAL_BACKUP_LOCATION
	```
 
6. To stop creating and deleting backups, terminate the process:
	
 	```
	kill -9 $backup_pid
	```

7. To resume creating and deleting backups, repeat step 2.

8. To debug, review the contents of `backup_stdouterr.log`
	
 	```
	vi backup_stdouterr.log
	```
