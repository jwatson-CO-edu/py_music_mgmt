# sort-by-artist-type.py
# James Watson, 2013 November
# Sort mp3 by artist, sort all other files by type

# == DEPENDENCIES ==
# * eyed3 : module for reading MP3 ID3 tags

# == TODO ==
# * directory checker function?

import os, shutil, time, eyed3

srcStr = "/media/squarecrow/Gil Backup/var_backup/AllMusic"
foundSourcePath = os.path.exists(srcStr)
print foundSourcePath
if foundSourcePath:
    srcPath = os.path.abspath(srcStr)
    print "srcPath created"

dstStr = "/media/squarecrow/FILEPILE/Music"
foundDestinationPath = os.path.exists(dstStr)
print foundDestinationPath
if foundDestinationPath:
    dstPath = os.path.abspath(dstStr)
    print "dstPath created"

disallowedChars = "\\/><|:&; \r\t\n.\"\'?"

def proper_dir_name(trialStr):
    global disallowedChars
    rtnStr = ""
    if trialStr:
        for char in trialStr:
            if char not in disallowedChars:
                rtnStr += char
    return rtnStr

def strip_the(artistName):
    if artistName and artistName[:3].lower() == "the":
        return artistName[3:]
    else:
        return artistName

def proper_artist_dir(trialStr):
    return strip_the(proper_dir_name(trialStr))

processed = 0
processTime = time.clock()

def sort_all_songs(arg, dirname, names):
    global srcPath, dstPath, processed, processTime
    for i in names:
        processed += 1
        if processed % 100 == 0:
            print "Processed " + str(processed) + " files. Last 100 in " + str(time.clock() - processTime)
            processTime = time.clock()
        namePath = os.path.join(dirname, i)
        print "Processing " + str(namePath)
        extension = os.path.splitext(i)[1]
        if extension == '.mp3': # If found mp3
            audiofile = None
            try:
                audiofile = eyed3.load(namePath)
            except:
                print "Problem reading " + str(namePath) + " tags!"
            if audiofile and audiofile.tag:
                artName = proper_artist_dir(audiofile.tag.artist)
            else:
                artName = ""
            if len(artName) > 0:
                artistPath = os.path.join(dstPath, artName)
            else:
                artistPath = os.path.join(dstPath, "Various")
            targetPath = os.path.join(artistPath, i)
            if os.path.exists(artistPath):
                if not os.path.exists(targetPath): # this file does not exist
                    try: # Try to copy the file to the artist folder if exists
                        shutil.copy2(namePath, targetPath)
                        print "Copied " #+ str(targetPath)
                    except IOError:
                        print "Unable to copy " #+ str(namePath)
                # else this file exists, but not same size, assume new version
                elif os.path.getsize(namePath) != os.path.getsize(targetPath):
                    incVar = 0
                    while os.path.exists(targetPath): # rename until new!
                        incVar += 1
                        newName = os.path.splitext(i)[0] + str(incVar) + os.path.splitext(i)[1]
                        print "Attempt rename: " + newName
                        targetPath = os.path.join(artistPath, newName)
                    try: # Try to copy the file with a new name
                        shutil.copy2(namePath, targetPath)
                        print "Copied " #+ str(targetPath)
                    except IOError:
                        print "Unable to copy " #+ str(namePath)
                #else:
                    #print "File " + str(i) + " already exists in target dir, same size!"
            else: # else folder does not exist, try create dir then copy
                try: # else folder does not exist, try create dir then copy
                    os.mkdir(artistPath)
                    print "Created dir " #+ str(artistPath)
                    shutil.copy2(namePath, targetPath)
                    print "Copied " #+ str(targetPath)
                except IOError:
                    print "Unable to copy " + str(namePath)
        else: # else, file is not an mp3
            typePath = os.path.join(dstPath, extension[1:].upper())
            if os.path.exists(typePath):
                try: # Try to copy the file to the type folder if exists
                    shutil.copy2(namePath, os.path.join(typePath, i))
                    print "Copied " #+ str(targetPath)
                except IOError:
                    print "Unable to copy " #+ str(namePath)
            else:
                try: # else folder does not exist, try create dir then copy
                    os.mkdir(typePath)
                    shutil.copy2(namePath, os.path.join(typePath, i))
                    print "Copied " #+ str(os.path.join(typePath, i))
                except IOError:
                    print "Unable to copy " #+ str(namePath)
                
if not foundSourcePath:
    print "Source path " + str(srcStr) + " not found!"
elif not foundDestinationPath:
    print "Destination path " + str(dstStr) + " not found!"
else:
    os.path.walk(srcPath, sort_all_songs, False)
    print "Processed " + str(processed) + " files."


# == TESTING ==
##print os.path.getsize(os.path.join(srcPath, "07 - Winterland Suburban Houses.mp3"))
##audiofile = eyed3.load(os.path.join(srcPath, "07 - Winterland Suburban Houses.mp3"))
##print audiofile.tag.artist # Peter McConnell
##print proper_dir_name(audiofile.tag.artist) # PeterMcConnell
##print strip_the(proper_dir_name("Toad the Wet Sprocket"))
##print strip_the(proper_dir_name("The Presidents of the United Stated of America"))
##print os.path.exists(os.path.join(srcPath, "07 - Winterland Suburban Houses.mp3")) # True
##print os.path.exists(srcPath) # True
##try:
##    os.mkdir(os.path.join(dstPath, "testPath")) # created successfully!
##    #break
##except OSError:
##    print str(os.path.join(dstPath, "testPath")) + " already exists"
##os.path.exists(os.path.join(dstPath, "testPath"))

