# File-sync Python script

## One-way folder backup Python script where a replica folder is modified to exactly match the content of a source folder

This Python script performs a backup of a source folder to a replica folder, both defined by the user. The user also specifies the synchronization interval to meet the requirements of their RPO as well as the destination folder of the log file. The features of this script include:
* One-way synchronization
* Periodic execution with a configurable interval
* All paths and the synchronization interval are defined by the user
* Log path can point to a folder or the log file
* Detects and updates changed files using hashing
* Deletes files and folders that no longer exist in the source
* Ensures nested folders are deleted correctly
* Ignores files that already exist in the replica folder and have not changed in the source folder
* Logs all operations to a file and console
* Error protection

Error Handling features:
* Missing Source/Replica Folder Handling
  * If the source folder doesn’t exist, the script logs an error and exits
  * If the replica folder doesn’t exist, it automatically creates it
* Safe Hash Comparison
  * Uses SHA-256 to compare files, avoiding unnecessary copies, and to check the integrity of files in the replica folder
  * If a file cannot be read, the script returns an empty hash (""), preventing comparison errors
* Checks all paths defined by the user
  * If the source folder does not exist, the script logs that error and exits
  * If either the replica or the log folders do not exist they are created
* Folders deleted while script is running
  * Ensures that if the source folder is deleted the script does not crash. Instead, it logs an error and exits
  * Ensures that if either the replica or the log folder is deleted they are created again and the backups keep running normally
* Ensures files that can not be copied due to some error or lack of permission are ignored and do not crash the script

To run use the command:

python file_sync.py --source "path/to/source" --replica "path/to/replica" --interval 60 --log_file "path/to/log.txt"

Arguments can be provided in any order and are the following:
* source → Path to the source folder (original)
* replica → Path to the replica folder (copy)
* interval → Sync interval in seconds
* log_file → Path to the log file
