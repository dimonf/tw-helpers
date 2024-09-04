# tw-helpers
scripts to facilitate work with tiddlywiki.

## json-files.sh

Tiddlywiki with no extensions writes to hard disk, but is not aware of updates made 
  to the files from outside of TW. Same goes for binary files, attachments. If the 
  mountain won't come to Muhammad then Muhammad must come to the mountain. Script is
  part of these procedure:
  - copy files to selected directory 
    - 'files' for nodejs version, 
    (https://tiddlywiki.com/prerelease/static/Using%2520the%2520integrated%2520static%2520file%2520server.html)
    - any directory of choice for single file TW, served (in my case) vi local webdav.
  - run the script, feeding it with file names, like:
    json-files.sh files/* > ~/Downloads/files.josn
    Output file comprises tiddlers for all files in source dir, in example above, 
    files/*
  - import output files.json via standard TW tools in web interface. Only new tiddlers
    will be imported.

 This is very first version, just to test the concept
