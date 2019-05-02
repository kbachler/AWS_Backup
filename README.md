# AWS_Backup
NOTE:   This program makes a backup to the AWS cloud of the current directory and sub-directories of which Backup.py resides.
	Assumes that user knows their AWS Credentials for the AWS Access Key ID and AWS Secret Access Key 

*** IMPORTANT -->> PLEASE RUN IN WINDOWS. ***
This program was Built and Tested in a Windows enviornment. It relies on formatting of 
Windows last modified date and time in order to successfully update modified files.

SOFTWARE/TOOLS USED: AWS CLI, Python 3.7.2, and boto3 library. 

---------------------------------------------------------------------------------------------
   INSTRUCTIONS:
----------------------------------------------------------------------------------------------
  1. Check if pip and python 3.7 are already installed & enviornment variables path are set.
  	(See webpage for help: https://docs.python.org/3/using/windows.html)
  2. Run command 'pip install boto3' if boto3 is not installed already
  3. Make sure AWS CLI is downloaded (https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)
  4. Run 'aws configure' command on terminal (https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)
  5. Create a bucket in your AWS S3 Management Console for backup files
  6. Save Backup.py to the location/folder you want to backup
  7. Open the command prompt/terminal
  8. Change directory 'cd' to the location of Backup.py 
HOW TO BUILD & EXECUTE:
  9. Call 'python Backup.py' in the command prompt/terminal to build & execute the program

Building an EXE:
  First install the python library called PyInstaller by typing 'pip install pyinstaller' into command prompt. 
  1. Open the command prompt/terminal
  2. Change directory 'cd' to the location of Backup.py 
  3. Type 'pyinstaller -F --debug all Backup.py'. Folders 'build', 'dist' and '__pycache__' will be created.
  4. Open the folder called 'dist'. Backup.exe will be there
