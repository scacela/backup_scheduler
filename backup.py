import os
import sys
import schedule
from time import sleep
import shutil
import datetime
import oci
import re

retry_strategy = oci.retry.DEFAULT_RETRY_STRATEGY

def create_os_credentials():
    # configure object storage credentials
    signer = oci.auth.signers.get_resource_principals_signer()
    os_client = oci.object_storage.ObjectStorageClient(config={}, signer=signer, retry_strategy=retry_strategy, timeout=60)
    os_namespace = os_client.get_namespace().data
    return os_client, os_namespace
    
os_client, os_namespace = create_os_credentials()

def get_suffix():
    date_suffix=datetime.datetime.today().strftime("%Y_%m_%d_%H:%M:%S")
    return date_suffix

def create_backups_object_storage(src_path, backups_dir, bucket_name):
    print(f"\nCREATE_BACKUPS_OBJECT_STORAGE: src_path='{src_path}', backups_dir='{backups_dir}', bucket_name='{bucket_name}'\n")
    date_suffix=get_suffix()

    basename=os.path.basename(src_path)
    # check if file
    if os.path.isfile(src_path):
      with open(src_path, "rb") as file:
          dest_file_path=f"{backups_dir}/{basename}/{basename}.{date_suffix}"
          try:
            os_client.put_object(namespace_name=os_namespace, bucket_name=bucket_name, object_name=dest_file_path, put_object_body=file)
            print(f"Successfully copied file '{src_path}' to remote destination object '{dest_file_path}' in bucket '{bucket_name}'.")
          except:
            print(f"Error: Failed to copy file '{src_path}' to remote destination object '{dest_file_path}' in bucket '{bucket_name}'.")

    # check if folder
    # todo: resolve BUG101: add ability to preserve middle directories. Middle directories are currently ignored, such that folder1/folder2/file.txt would get copied to folder1/file.txt
    elif os.path.isdir(src_path):
      for root, _, files in os.walk(src_path):
          try:
            for file_name in files:
                with open(os.path.join(root, file_name), "rb") as file:
                    dest_file_path=f"{backups_dir}/{basename}/{file_name}/{file_name}.{date_suffix}"
                    # remove consecutive slashes. Consecutive slashes would result in creation of a folder with no name
                    dest_file_path=re.sub(r'/+', '/', dest_file_path)
                    try:
                      os_client.put_object(namespace_name=os_namespace, bucket_name=bucket_name, object_name=dest_file_path, put_object_body=file)
                      print(f"Successfully copied nested file '{src_path}/{file_name}' to remote destination object '{dest_file_path}' in bucket '{bucket_name}'")
                    except:
                      print(f"Error: Failed to copy nested file '{src_path}/{file_name}' to remote destination object '{dest_file_path}' in bucket '{bucket_name}'")
                print(f"Successfully copied folder '{src_path}' to remote destination folder '{backups_dir}/{basename} in bucket '{bucket_name}'")
          except:
            print(f"Error: Failed to copy folder '{src_path}' to remote destination folder '{backups_dir}/{basename}' in bucket '{bucket_name}'")
    else:
      print(f"No remote copy performed. The specified path '{src_path}' is neither a file nor a folder.")
    return

def create_backups_local(src_path, backups_dir, max_num_backups=4):
    print(f"\nCREATE_BACKUPS_LOCAL: src_path='{src_path}', backups_dir='{backups_dir}', max_num_backups='{max_num_backups}'\n")
    date_suffix=get_suffix()

    basename=os.path.basename(src_path)
    # Check if the following folder exists
    dest_folder_path=f"{backups_dir}/{basename}"
    if not os.path.exists(dest_folder_path):
      # If it doesn't exist, create the folder
      try:
        os.makedirs(dest_folder_path)
        print(f"Successfully created local destination folder '{dest_folder_path}'")
      except:
        print(f"Error: Local destination folder '{dest_folder_path}' could not be created")
    # check if file
    if os.path.isfile(src_path):
      dest_file_path=f"{dest_folder_path}/{basename}.{date_suffix}"
      try:
        shutil.copyfile(src_path, dest_file_path)
        print(f"Successfully copied file '{src_path}' to local destination file '{dest_file_path}'")
      except:
        print(f"Error: Failed to copy file '{src_path}' to local destination file '{dest_file_path}'")
      # remove old
      delete_backups_local(dest_folder_path, max_num_backups)

    # check if folder
    # todo: resolve BUG101
    elif os.path.isdir(src_path):
      for root, _, files in os.walk(src_path):
          try:
              for file_name in files:
                  dest_folder_path_2=f"{dest_folder_path}/{file_name}"
                  dest_file_path=f"{dest_folder_path_2}/{file_name}.{date_suffix}"
                  if not os.path.exists(dest_folder_path_2):
                    # If it doesn't exist, create the folder
                    try:
                      os.makedirs(dest_folder_path_2)
                      print(f"Successfully created nested local destination folder '{dest_folder_path_2}'")
                    except:
                     print(f"Error: Nested local destination folder '{dest_folder_path_2}' could not be created")
                  try:
                    shutil.copyfile(f"{src_path}/{file_name}", dest_file_path)
                    print(f"Successfully copied nested file '{src_path}/{file_name}' to local destination file '{dest_file_path}'")
                  except:
                    print(f"Error: failed to copy nested file '{src_path}/{file_name}' to local destination file '{dest_file_path}'")
                  # remove old
                  delete_backups_local(dest_folder_path_2, max_num_backups)
              print(f"Successfully copied folder '{src_path}' to local destination folder '{backups_dir}/{basename}'")
          except:
              print(f"Error: Failed to copy folder '{src_path}' to local destination folder '{backups_dir}/{basename}'")
    else:
      print(f"No local copy performed. The specified path '{src_path}' is neither a file nor a folder.")

def delete_backups_local(dest_folder_path, max_num_backups):
    print(f"\nDELETE_BACKUPS_LOCAL: src_path='{dest_folder_path}', max_num_backups='{max_num_backups}'\n")

    list_of_files = os.listdir(dest_folder_path)
    full_path = ["{0}/{1}".format(dest_folder_path, x) for x in list_of_files]

    if len(list_of_files) > max_num_backups:
        
        oldest_file = min(full_path, key=os.path.getctime)
        
        if os.path.isfile(oldest_file):
          try:
            os.remove(oldest_file)
            print(f"Successfully removed oldest file '{oldest_file}'")
          except:
            print(f"Error: Failed to remove oldest file '{oldest_file}'")
        else:
          print(f"No removal performed. The path representing the oldest item '{oldest_file}' is neither a file nor a folder")

def my_schedule():

    
    # Local Backup

    ## Back up a file ("/home/datascience/mynotebook.ipynb") at minute 00 of every hour to a local folder ("/home/datascience/mybackups"). Retain 336 backups, i.e. 2 weeks of hourly backups
    schedule.every().hour.at(":00").do(create_backups_local, src_path="/home/datascience/mynotebook.ipynb",backups_dir="/home/datascience/mybackups", max_num_backups=336)

    ## Back up a folder ("/home/datascience/myfolder") at minute 30 of every hour to a local folder ("/home/datascience/mybackups"). Retain 336 backups, i.e. 2 weeks of hourly backups
    schedule.every().hour.at(":30").do(create_backups_local, src_path="/home/datascience/myfolder",backups_dir="/home/datascience/mybackups", max_num_backups=336)
    
    
    # Remote Backup to Oracle Object Storage
    
    ## Back up a file ("/home/datascience/mynotebook.ipynb") at minute 00 of every hour to a remote folder ("mybackups") in an Object Storage bucket ("mybucket")
    schedule.every().hour.at(":00").do(create_backups_object_storage, src_path="/home/datascience/mynotebook.ipynb",backups_dir="mybackups",bucket_name="mybucket")
    
    ## Back up a folder ("/home/datascience/myfolder") at minute 30 of every hour to a remote folder ("mybackups") in an Object Storage bucket ("mybucket")
    schedule.every().hour.at(":30").do(create_backups_object_storage, src_path="/home/datascience/myfolder",backups_dir="mybackups",bucket_name="mybucket")

def main():
    my_schedule()
    while True:
        schedule.run_pending()
        sleep(1)

if __name__ == '__main__':
    main()
