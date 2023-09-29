# backup_scheduler
Save timestamped backups of your files and folders on a scheduled basis to your local environment or remotely to Oracle Object Storage. For local backups, specify the maximum number of backups to retain, and automatically dump the oldest backups. Manage your Oracle Object Storage backups using Oracle Object Storage Lifecycle Policy Rules and Retention Rules.

## Prerequisites

1. Clone this repository to the environment from which you will be taking backups.
	
 	```
	git clone https://github.com/scacela/backup_scheduler.git
	```

2. For use with Oracle Object Storage, ensure that your environment is authenticated for the Object Storage connection. This script leverages resource principal authentication by default.

3. For use with Oracle Object Storage, ensure that your environment is able to access Oracle Object Storage via either the public internet, or if you will be taking backups from within your Oracle Cloud environment, you may use a Service Gateway to access Oracle Object Storage over the Oracle Services Network (OSN).

4. Install `scheduler` to your environment.

	```
	pip install scheduler
 	```

## Usage Instructions

1. In `backup.py`, edit the entries under the `my_schedule` function to include the file or directory for which you wish to save timestamped backups on a scheduled basis to your local environment or remotely to Oracle Object Storage.

	```
 	# Change directory to the folder you downloaded, containing the backup script.
 	cd backup_scheduler
 	```
	```
 	# Open the backup script using an editor. In this example, vi is used.
 	vi backup.py
 	```

3. Execute `backup.py` in a background process. Make a note of the process ID that your process is using.
	
 	```
	nohup python -u backup.py > backup_stdouterr.log 2>&1 &
	```
 
4. Capture the process ID that the process is using, replacing the placeholder `MY_PROCESS_ID` with your own.
	
 	```
	export backup_pid=MY_PROCESS_ID
	```
 
5. Monitor the status of your process:
	
 	```
	ps aux | grep $backup_pid
	```
 
6. Monitor your backup location in Oracle Object Storage, or use the following command to monitor a backup location within your local environment. Replace the placeholder `MY_LOCAL_BACKUP_LOCATION` with your own.
	
 	```
	ls -a1 MY_LOCAL_BACKUP_LOCATION
	```
 
7. To stop creating and deleting backups, terminate the process:
	
 	```
	kill -9 $backup_pid
	```

8. To resume creating and deleting backups, repeat step 2.

9. To monitor logs, review the contents of `backup_stdouterr.log`.
	
 	```
	vi backup_stdouterr.log
	```
