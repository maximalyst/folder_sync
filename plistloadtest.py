import plistlib

with open('/Users/brandon/Programming/folder_sync/com.bstudios.folder_sync.plist', "rb") as settng:
    foo = plistlib.load(settng)
    originalTarget = foo["syncTargetNames"]
    print(originalTarget)