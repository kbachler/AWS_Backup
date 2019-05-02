import boto3, botocore  # AWS SDK for Python
import os               # Library for getting files from local computer
import getpass          # Used for hiding the AWS Secret Access Key when user enters for security
import time, datetime   # Used for time and datetime conversions
from datetime import timezone  

""" <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Kayla Bachler
2/10/2019
CSS490 Program #3

DESCRIPTION: 
This program recursively traverses the files of the user's current directory and 
makes a backup to AWS. The user is prompted for their AWS Access Key ID, AWS 
Secret Access Key, and the bucket name that they want their files backed up to.
If the user calls executes Backup.py with a bucket name that already contains the
current directory's files, only the modified files will be backed up to the bucket.

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
  9. Call 'python Backup.py' in the command prompt/terminal to build AND execute the program

NOTE: This program will handle bad bucket name input, but it requires that the user knows
their AWS credentials. Valid bucket names can be found here:
https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-s3-bucket-naming-requirements.html
<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< """

# Global variables
s3 = boto3.resource('s3')
baseDirectory = './'
curr = os.path.dirname(os.path.realpath(__file__))  # The current directory of the user
bucket_name = ''

""" -----------------------------------------------------------------------
backupFiles method:
Backs up all of the files in the current directory and the subfolders. This
method is called recursively to backup the subfolders for the user. Comparing
the last modified date of the local file and the AWS file we only upload
duplicate files if they were recently updated.
---------------------------------------------------------------------------
"""
def backupFiles(parentDirectory = ""):
  if (parentDirectory != ""):  # Add the directory if its not in the bucket
    s3.Object(bucket_name, parentDirectory).put()
  files = [f for f in os.listdir(baseDirectory + parentDirectory)]
  subDirectories = [d for d in os.listdir(baseDirectory + parentDirectory)]

  # For each file in the current directory, add it to the bucket
  for file in files:
    if (os.path.isfile(baseDirectory + parentDirectory + file)):
      # Get the last modified date of the local file and convert it to UTC:
      localLastMod = datetime.datetime.utcfromtimestamp(os.path.getmtime
                    (baseDirectory + parentDirectory + file)).replace(microsecond=0, tzinfo=timezone.utc)
      localLastMod = str(localLastMod.strftime('%Y-%m-%d %H:%M:%S')) + "+00:00"
      getDatetime = True  # Flag for if the file is in the cloud bucket already
      #print(file + "'s Local last modified="+ localLastMod) #Uncomment for testing date comparison
      
      try:   # If the file has not been backed up to the cloud back it up, else compare dates:
        cloudLastMod = str(s3.Object(bucket_name, parentDirectory + file).last_modified)
        #print(file + "'s Cloud last modified="+ cloudLastMod) #Uncomment for testing date comparison
      except:
        getDatetime = False  # The file doesn't exist in the cloud yet so continue
      # If the file isn't in the cloud bucket and it is a newer version, add it! Otherwise skip
      if (getDatetime == False or cloudLastMod < localLastMod):
        s3.Object(bucket_name, parentDirectory+file).put(Body=open(parentDirectory+file, 'rb')) # Add file

  # For each sub directory, recursively call the function to backup its files: 
  for subDir in subDirectories:
    if (os.path.isdir(baseDirectory + parentDirectory + subDir)):
      backupFiles(parentDirectory + subDir + "/") # Recursively call for sub directory
# End of backupFiles()

""" -----------------------------------------------------------------------
verifyBucket method:
This method checks the 'condition' of the bucket name our user entered.
If the bucket exists we continue to backup, if their is forbidden access to
the bucket, we return 1 and the user enters a new bucket name. Lastly, if 
the bucket name specified doesn't exist we create it then continue to backup.
---------------------------------------------------------------------------
"""
def verifyBucket(bucket_name):
  if (bucket_name.isupper()):
    print("Error: Invalid Bucket name '" + bucket_name + "'. Please try again!")
    return 1
  try:
    s3.meta.client.head_bucket(Bucket=bucket_name)
    return 0  # The bucket exists
  except botocore.exceptions.ClientError as e:
    # If a client error is thrown, check if it was 403 or 404
    error_code = int(e.response['Error']['Code'])
    if (error_code == 403):  # Forbidden Access
      print("Error: The bucket '" + bucket_name + "' has forbidden access. Please try a different bucket!")
      return 1
    elif error_code == 404:  # Bucket does not exist
      return 2
  except botocore.exceptions.ParamValidationError:
    # If the bucket name is invalid throw error
    print("Error: Invalid Bucket name '" + bucket_name + "'. Please try again!")
    return 1
# End of verifyBucket()

""" -----------------------------------------------------------------------
verifyAccessKeys method:
In this method we check the credentials that the user entered. If we get 
an exception we ask the user to re-enter their credentials, else we start
the session to the AWS account to do our file backup.
---------------------------------------------------------------------------
"""
def verifyAccessKeys(accesskeyID, secretAccessKey):
  if (accesskeyID == '' or secretAccessKey == ''):
    print("Error: The credentials you entered are invalid, please try again!")
    return False
  try:
    # Start session using users Access Key ID & Secret Access Key:
    session = boto3.Session(
      aws_access_key_id=accesskeyID,
      aws_secret_access_key=secretAccessKey
    )
    return True
  except:
    print("Error: The credentials you entered are invalid, please try again!")
    return False

""" -----------------------------------------------------------------------
Main method:
In this method we print instructions to the user for backing up the files,
then we ask for their credentials for AWS and the bucket name they want to
backup their files to. Then we validate the bucket name and backup the files
from their current directory using the backupFiles() method above.
--------------------------------------------------------------------------- 
"""
if __name__ == '__main__':
    # Display instructions to the user:
    print("--------------------------------------------------------------------------------")
    print("Hello there! This program backs up all the files in your current directory.")
    print("INSTRUCTIONS:")
    print(" 1) Build a bucket in S3 Management Console for your backup files.")
    print(" 2) Make sure you are in the directory you want to backup.")
    print("   b) If not, save Backup.py to that directory and re-run program.")
    print(" 3) Get ready to enter your AWS Access Key ID & AWS Secret Access Key...")
    print("--------------------------------------------------------------------------------")
    '''
    # Uncomment to hardcode credentials for easier testing:
    session = boto3.Session(
      aws_access_key_id='AWS_ACCESS_KEY_ID',
      aws_secret_access_key='AWS_SECRET_ACCESS_KEY'
    )'''

    # Get credentials for AWS and Bucket name:
    while True:
      accesskeyID = input("Enter your AWS Access Key ID: ")
      secretAccessKey = getpass.getpass(prompt="Enter your AWS Secret Access Key: ")  # getpass hides from screen
      # Verify that the credentials are valid, if not continue to loop:
      if (verifyAccessKeys(accesskeyID, secretAccessKey) == True):
        break

    # Loop to verify that we have a valid bucket name:
    while True:
      bucket_name = input("Please enter the bucket name you'd like to backup to: ")
      status = verifyBucket(bucket_name)
      if (status == 0 or status == 2):  # If the bucket name is invalid, continue to loop
        break   # Otherwise, we break this loop and continue

    # If we need to create a bucket then create it. Otherwise, we should exit the while 
    # loop immediately because we have a valid bucket already. Check status each loop
    while True:
      if status == 2:  # The bucket doesn't exist, so create one
        try:
          bucket = s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'us-west-2'})
          break
        except (botocore.exceptions.ClientError, botocore.exceptions.ParamValidationError) as e:
          if (e.response['Error']['Code'] == 'InvalidBucketName'):  # Invalid Bucket name, try again
            print("Error: The Bucket '" + bucket_name + "' is an invalid bucket name.")
            bucket_name = input("Please enter a different bucket name: ")
            if (verifyBucket(bucket_name) == True):
              break
          else:
            print("Error: The Bucket '" + bucket_name + "' is an invalid bucket name.")
            bucket_name = input("Please enter a different bucket name: ")
            if (verifyBucket(bucket_name) == True):
              break
      elif status == 1:  
        bucket_name = input("Please enter a different bucket name: ")
        if (verifyBucket(bucket_name) == True):
          break
      elif status == 0:  # Bucket is created so continue to backup
        break  
      status = verifyBucket(bucket_name)
    # End while loop
    
    # Backup files to bucket
    print("\nBacking up your files from '" + curr +"'...")
    no_error = None
    try:
      backupFiles()
      no_error = True
    except botocore.exceptions.ClientError as e:
      if (e.response['Error']['Code'] == 'AccessDenied'):  # Forbidden Access
        print("Error: The bucket '" + bucket_name + "' has forbidden access. Please try a different bucket!")
        exit()
    if (no_error):
        print("\nSuccess! Your files have been backed up!")
        exit()
    else:
      print("Error: There was an issue backing up your files, please reload the program")
# End of main
# End of program

