# backup_scheduler
Always have a backup plan. Never lose quality work.

## Features
* Save timestamped backups of your files and folders on a scheduled basis to your local environment, or remotely to Oracle Object Storage
* Configure multiple backup profiles with custom parameters
* For local backups, specify the maximum number of backups to retain, so that as new backups are saved, the oldest files are dumped
* For Object Storage backups, choose api key or resource principal authentication and back up to a region of your choice
* Create weekly, daily, hourly, or minutely backups

    > **Recommendation:** Manage your Oracle Object Storage backups using Oracle Object Storage Lifecycle Policy Rules and Retention Rules.

## Usage Instructions

1. Download this project:

    ```
    git clone https://github.com/scacela/backup_scheduler.git
    ```
    
2. Ensure that your environment is authorized to access Oracle Object Storage using either api keys and an OCI config file within the `~/.oci` directory, or resource principal authentication.

3. Customize the `config.ini` file to configure your backups. Use a `[section]` or multiple to specify unique backup profiles.

4. Ensure that the required Python packages (`scheduler` and `oci`) are installed using the following command:

    ```
    pip install scheduler oci
    ```

5. Change your directory to the folder containing the Python script `backup_script.py`:

    ```
    cd backup_scheduler
    ```

6. Run `backup_script.py` using a new background process by executing the below command. This script will run continuously to perform scheduled backups according to the configurations in `config.ini`.

    ```
    nohup python -u backup.py > backup_stdouterr.log 2>&1 &
    ```
    > **Note:** Make a note of the process id that your script is running on.

7. Check `backup_stdouterr.log` to monitor the logs associated with your latest process where `backup_script.py` is running.

8. You can adjust the configurations in `config.ini` as needed. After updates are made to `config.ini`, repeat step 6 to perform backups based on your updated configurations.

9. Monitor details about the process(es) that your script is running on:

    ```
    ps aux | grep backup.py
    ```

10. To stop the script from producing backups from a particular process, terminate the process by running the following command, replacing `MY_PROCESS_ID` with your own.

    ```
    kill -9 MY_PROCESS_ID
    ```
