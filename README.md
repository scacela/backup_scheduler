# backup_scheduler
Always have a backup plan. Never lose quality work.

## Features
* Save timestamped backups of your files and folders on a scheduled basis to your local environment, or remotely to Oracle Object Storage
* Configure multiple backup profiles with custom parameters
* For local backups, specify the maximum number of backups to retain, so that as new backups are saved, the oldest files are dumped
* For Object Storage backups, choose api key or resource principal authentication and back up to a region of your choice
* Create weekly, daily, hourly, or minutely backups

    > **Recommendation:** Manage your Oracle Object Storage backups using Oracle Object Storage Lifecycle Policy Rules and Retention Rules.

## Prerequisites

1. Ensure that your environment is authorized to access Oracle Object Storage using either api keys and an OCI config file within the `~/.oci` directory, or resource principal authentication.

2. Ensure that the required Python packages (`scheduler` and `oci`) are installed to your environment by executing the following command:

    ```
    pip install scheduler oci
    ```

## Usage Instructions

1. Download this project:

    ```
    git clone https://github.com/scacela/backup_scheduler.git
    ```
    
2. Customize the `config.ini` file to configure your backup settings. Define unique backup profiles using sections with associated key-value pair attributes.

3. Change your directory to the folder containing the Python script `backup.py`:

    ```
    cd backup_scheduler
    ```

4. Run `backup.py` using a new background process by executing the below command. This script will run continuously to perform scheduled backups according to the configurations in `config.ini`.

    ```
    nohup python -u backup.py > backup_stdouterr.log 2>&1 &
    ```
    > **Note:**
    > * If you wish to track the process that your script is running on for monitoring and termination, make a note of the process id.
    > * You can adjust the configurations in `config.ini` as needed. After updates are made to `config.ini`, repeat this step to perform backups based on your updated configurations.

5. Check `backup_stdouterr.log` to monitor the logs associated with your latest process where `backup.py` is running.

6. Monitor details about the process(es) that your script is running on:

    ```
    ps aux | grep backup.py
    ```

7. To stop performing backups from a particular process, terminate the process by executing the following command, replacing `MY_PROCESS_ID` with your own process id.

    ```
    kill -9 MY_PROCESS_ID
    ```
