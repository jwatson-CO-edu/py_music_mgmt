# temp_player.py
# A music player for when both your Windows machine and your youtube are tied up

# https://linuxconfig.org/how-to-play-audio-with-vlc-in-python
import vlc , getpass , os , sys , time
from random import choice

SOURCEDIR = os.path.dirname( os.path.abspath( '__file__' ) ) # URL, dir containing source file: http://stackoverflow.com/a/7783326
PARENTDIR = os.path.dirname( SOURCEDIR )
# ~~ Path Utilities ~~
def prepend_dir_to_path( pathName ): sys.path.insert( 0 , pathName ) # Might need this to fetch a lib in a parent directory
prepend_dir_to_path( SOURCEDIR )
from marchhare.marchhare import get_EXT , first_valid_dir

_DEBUG = False

if __name__ == '__main__':
    if _DEBUG: print "Script called with arguments: ", sys.argv
    
    # Set the number of tracks to play to the number specified by the user or the default value
    try:
        N_tracks = int( sys.argv[1] )
    except:
        N_tracks = 20
    
    # Construct the music directory
    MUSICDIR = first_valid_dir( [
        os.path.join( "/media/" , getpass.getuser() , "MUSIC/Music" ) ,
        os.path.join( "/media/" , getpass.getuser() , "MAINBACKUP/corsair_backup/Music" ) ,
    ] )
    valiDir = os.path.isdir( MUSICDIR )
    print "The music directory is" , MUSICDIR , "but is it valid?" , valiDir
    
    if valiDir:
        # Walk the directory and build a list of all playable music files
        tracklist = []
        # https://www.pythoncentral.io/how-to-traverse-a-directory-tree-in-python-guide-to-os-walk/
        for dirName , subdirList , fileList in os.walk( MUSICDIR ):
            for fName in fileList:
                if get_EXT( fName ) == "MP3":
                    tracklist.append( os.path.join( dirName , fName ) )
                    
        print "Found" , len( tracklist ) , "playable files! For example" , choice( tracklist )
        
        # For each track, pick a random song, print title, and play it while printing status dots
        for i in range( N_tracks ):
            track = choice( tracklist )
            print i+1 , "of" , N_tracks , ", Now playing" , track , 
            player = vlc.MediaPlayer( track )
            print ", Duration:" , player.get_length() / 1000.0 , 
            player.play()
            time.sleep( 0.5 )
            Ended = 6
            current_state = player.get_state()
            # Check that the song is still playing at intervals, if so, print a status dot
            while current_state != Ended:
                print '.',
                sys.stdout.flush()
                time.sleep( 1.0 )
                current_state = player.get_state() 
            # Song over, choose next 
            print
        else:
            print "ERROR: No songs to play!"
        
    print "End!"
