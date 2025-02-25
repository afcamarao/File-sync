import os
import shutil
import hashlib
import argparse
import time
import sys
from datetime import datetime

def log_message(log, message):
    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    entry = f'[{timestamp}] {message}' #log message
    print(entry)
    with open(log, 'a') as log:
        log.write(entry + '\n')

def check_interval(interval, log):
    if interval < 1:
        log_message(log, "Sync interval must be a positive number. Exiting.")
        sys.exit()

def check_log_path(log): #check log folder
    if log.endswith('.txt'): #log path is a file
        folder_path = os.path.dirname(log)
        if not os.path.exists(folder_path) and folder_path != '':
            os.makedirs(folder_path, exist_ok=True)
    else: #log path is a folder
        if not os.path.exists(log):
            os.makedirs(log, exist_ok=True)
        log = os.path.join(log, "log.txt")

    return log

def check_folders(source, destination, log):
    #check source folder
    if not os.path.exists(source):
        log_message(log, f"Source folder does not exist: {source}")
        return 0
    elif not os.path.isdir(source):
        log_message(log, f"Source path is not a directory: {source}")
        return 0
    
    #check destination folder
    if not os.path.exists(destination):
        os.makedirs(destination, exist_ok=True)
        log_message(log, f'Destination folder created: {destination}')

def calculate_hash(file_path, log_path, algorithm='sha256'):
    hash_func = hashlib.new(algorithm)
    try:
        with open(file_path, 'rb') as file:
            while chunk := file.read(8192):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        log_message(log_path, f'Error hashing {file_path}: {e}')
        return ""

def delete_files(source, destination, log):
    if not os.path.exists(source):
        log_message(log, "Source folder was deleted. Exiting.")
        return 0
    source_items = set(os.listdir(source))
    destination_items = set(os.listdir(destination))

    for item in destination_items:
        if item not in source_items:
            item_path = os.path.join(destination, item)
            if os.path.isdir(item_path): #delete a folder
                shutil.rmtree(item_path)
                log_message(log, f"Folder {item} deleted: {item_path}")
            elif os.path.isfile(item_path): #delete a file
                os.remove(item_path)
                log_message(log, f"File {item} deleted: {item_path}")

def copy_files(source, destination, log):
    source_items = set(os.listdir(source))

    for item in source_items:
        source_path = os.path.join(source, item)
        destination_path = os.path.join(destination, item)    
        if os.path.isdir(source_path): #nested folder
            if not os.path.exists(destination_path): #nested folder does not exist in replica folder
                os.makedirs(destination_path, exist_ok=True)
                log_message(log, f'Destination folder created: {destination_path}')
            delete_files(source_path, destination_path, log)
            copy_files(source_path, destination_path, log)
        elif os.path.isfile(source_path): #file
            try:
                if not os.path.exists(destination_path) or calculate_hash(file_path=source_path, log_path=log) != calculate_hash(file_path=destination_path, log_path=log): #does not exist in replic or was changed in source
                    shutil.copy2(source_path, destination_path)
                    log_message(log, f'File {item} copied to destination: {destination_path}')
            except PermissionError:
                log_message(log, f'Permission denied: {source_path} (Skipping)')
            except OSError as e:
                log_message(log, f"Error copying {source_path}: {e}. Exiting")
                sys.exit()
            except Exception as e:
                log_message(log, f'Error copying {source_path}: {e}')

def main():
    parser = argparse.ArgumentParser(description="Folder Synchronization Script")
    parser.add_argument("--source", required=True, help="Path to the source folder")
    parser.add_argument("--replica", required=True, help="Path to the replica folder")
    parser.add_argument("--interval", type=int, required=True, help="Synchronization interval in seconds")
    parser.add_argument("--log_file", required=True, help="Path to the log file")
    args = parser.parse_args()

    log_folder_final = check_log_path(args.log_file)
    log_message(log_folder_final, '----------------File synchronization script started----------------')
    if (check_folders(args.source, args.replica, log_folder_final) == 0): #source folder does not exist or is not a directory
        return None
    check_interval(args.interval, log_folder_final)
    
    try:
        while True:
            check_log_path(log_folder_final)
            log_message(log_folder_final, "STARTING NEW SYNCHRONIZATION CYCLE")
            if check_folders(args.source, args.replica, log_folder_final) == 0: #sorce folder no longer exists
                log_message(log_folder_final, "Source folder was deleted. Exiting.")
                return None
            delete_files(args.source, args.replica, log_folder_final) #delete items that are in replica but not in source
            copy_files(args.source, args.replica, log_folder_final) #copy new or changed files to replica
            log_message(log_folder_final, f"SYNCHRONIZATION CYCLE COMPLETE. Next run in {args.interval} seconds.\n")
            time.sleep(args.interval) #sync interval
    except KeyboardInterrupt:
        log_message(log_folder_final, "Synchronization stopped by user.\n")

if __name__ == "__main__":
    main()