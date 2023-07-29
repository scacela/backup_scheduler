# backup_scheduler
Save backups of your files and folders on a scheduled basis to your local environment. Specify the maximum number of backups to retain, and automatically dump the oldest backups.

## Instructions
1. Clone this repository.
	```
	git clone https://github.com/scacela/backup_scheduler.git
	```
2. Edit `backup.py`, adding an entry under the `my_schedule` function using your desired parameters and backup schedule. Consider this example:
	```
	# Back-up a file or directory to directory_A at the first minute of every hour, and retain backups up to one week old.
	schedule.every().hour.at(":00").do(create_backup,"/path/to/file_or_directory/to/backup", "/path/to/backup/directory_A", 168)
	```
	a. Identify the file or directory you wish to back-up, and replace `/path/to/file_or_directory/to/backup` with the path to this file or directory.
	
	b. Identify a directory to which you wish to save your backups, and replace `/path/to/backup/directory_A` with the path to this directory. Be sure to use a different backup directory than any others specified for other files or folders you are backing up in this script.

	*Note*: If you are backing up a file, the backup directory must already exist. If you are backing up a directory, the backup directory will be created automatically by this script.
	
	c. Adjust the schedule to your requirements. Refer to the documentation for the [scheduler](https://pypi.org/project/schedule/) library, which this script leverages.
	
	d. Adjust the number (168, in the example shown) to the maximum number of backups you wish to retain in your backup directory. As more backups are created, older backups are automatically deleted so that the maximum number of backups you specify is not exceeded.

3. Run `backup.py` in a background process. Make note of the process ID that prints to the console after running the command.
	```
	nohup python -u backup.py > .backups_stdouterr.log 2>&1 &
	```
4. Store the process ID of the process you created in an environment variable for easier access. Be sure to replace `YOUR_PROCESS_ID` with your own process ID.
	```
	export backups_pid=YOUR_PROCESS_ID
	```
5. Monitor the status of your process using the process ID you captured:
	```
	ps aux | grep $backups_pid
	```
6. Monitor your backup directory for backups:
	```
	ls -a1 /path/to/your/backup/directory
	```
7. To stop creating and deleting backups, terminate the process you created:
	```
	kill -9 $backups_pid
	```
8. To resume creating and deleting backups, repeat `step 3`.
