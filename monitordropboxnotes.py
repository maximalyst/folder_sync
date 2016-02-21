#!/usr/bin/env python3
import hashlib
import os
import shutil
import plistlib

class HashMe:
    '''Class for making hashed file objects and checksum files'''
    def __init__(self, fileName):
        self.file = fileName


    def hash_file(self): # method for generating hash of object's input file
        self.hashedbin = hashlib.md5() # generate binary hash object for file
        BUFFERSIZE = 65536*2 # buffer reads 32 bytes at a time, because read() will otherwise put
                             # the entire file in memory, and our PDFs may potentially be large.

        with open(self.file, 'rb') as self.testFile: #file opened in binary
            self.fileBuffer = self.testFile.read(BUFFERSIZE)

            # read BUFFERSIZE bytes at a time until end of file
            while len(self.fileBuffer) > 0:
                self.hashedbin.update(self.fileBuffer)
                self.fileBuffer = self.testFile.read(BUFFERSIZE)

            self.hashvalue = self.hashedbin.hexdigest()


    def printit(self): # printing method for debugging
        print(self.hashvalue)



def copyFile(sourceDirectory, targetDirectory):
    '''Copies a file from sourceDirectory to targetDirectory, making the
       necessary folders along the way'''

    if not(os.path.isdir(targetDirectory)):
        os.makedirs(targetDirectory, exist_ok=True)

    shutil.copy2(sourceDirectory, targetDirectory)


# Working on reading parent and target directories from settings plist file...
with open('/Library/LaunchAgents/com.bstudios.folder_sync.plist', mode='r') as settings:
    plistlib.load(settings,fmt=None)

originalParent = '/Users/brandon/Programming/testing'
originalParentName = originalParent.rsplit('/')[-1] # JUST the name of the parent folder
# Target directory for all files and subfolders to copy to:
targetParent = '/Users/brandon/Programming/testing2'
fileType = '.txt'

if not fileType.startswith('.'):
    fileType = '.' + fileType


checksumParentFolder = originalParent+'/checksums'
# Just in case there isn't a checksums folder in the directory we're following:
if not(os.path.isdir(checksumParentFolder)):
    os.makedirs(checksumParentFolder, exist_ok=True)
    # condition eliminates a possible race condition, so it's a bit safer. Better safe than sorry. Thanks Python 3.


# Generate lists of Directories and Subdirectories, and all files within:
dirList = [x[0] for x in os.walk(originalParent)]
# folderList = [x[1] for x in os.walk(originalParent)] # don't need this line
fileList = [x[2] for x in os.walk(originalParent)]

#Need to remove files that aren't of the type we're looking for
for subfileList in fileList:
    temp = subfileList.copy() # Python passes by reference; force pass by copy
    for file in temp:
        if not file.endswith(fileType):
            subfileList.remove(file)



for i, folder in enumerate(dirList):
    if folder.rsplit(checksumParentFolder)[0] == '': # Ignore the checksums folder!
        continue

    # looping through the files within each full path that we have.

    # strip off the path back to the parent folder name. It has a / at the front!!
    folderName = folder.rsplit(originalParentName)[-1]

    # Full path for the current folder's checksum folder
    checksumFolder = checksumParentFolder + folder.rsplit('/'+originalParentName)[-1]

    # make checksum folder for the current source folder
    if not(os.path.isdir(checksumFolder)):
        os.makedirs(checksumFolder, exist_ok=True)

    for file in fileList[i]:

        #hash each file
        hashedFile = HashMe(folder+'/'+file)
        hashedFile.hash_file()

        # If we're at this point, the file is definitely a .pdf.

        # save a file with hash function as the same name, different extension
        hashFileName = file[:len(fileType)] + '.md5' #remove filetype, add .md5


        if not(os.path.isfile(checksumFolder+'/'+hashFileName)):
        # New file since last check; need to generate md5 checksum file and copy
           #the file to the target directory
            with open(checksumFolder+'/'+hashFileName, 'w') as saveFile:
                saveFile.write(hashedFile.hashvalue)

                # Copy file to disk, making new directory if necessary
                #copyFile(folder+'/'+file, targetParent+folderName)
                if not(os.path.isdir(targetParent+folderName)):
                    os.makedirs(targetParent+folderName, exist_ok=True)
                shutil.copy2(folder+'/'+file, targetParent+folderName)

        else: # file already exists, so compare old sum to new sum
            with open(checksumFolder+'/'+hashFileName, 'r+') as readFile:

                md5check = readFile.read()

                if md5check != hashedFile.hashvalue:
                    # file is different than the last time we looked at it.
                    # insert the new hash value, truncate the old
                    readFile.seek(0)
                    readFile.write(hashedFile.hashvalue)
                    readFile.truncate()

                    # now save the new file locally, copying with metadata...
                    #copyFile(folder+'/'+file, targetParent+folderName)
                    if not(os.path.isdir(targetParent+folderName)):
                        os.makedirs(targetParent+folderName, exist_ok=True)
                    shutil.copy2(folder+'/'+file, targetParent+folderName)
