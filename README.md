# tw-helpers
scripts to facilitate work with tiddlywiki.

## tid-from-files

Tiddlywiki with no extensions writes to hard disk, but is not aware of updates made 
  to the files from outside of TW. Same goes for binary files, attachments.
  This script is part of these workflow:
  - copy files to selected directory 
    - 'files' for nodejs version, 
    (https://tiddlywiki.com/prerelease/static/Using%2520the%2520integrated%2520static%2520file%2520server.html)
    - any directory of choice for single file TW, served (in my case) vi local webdav.
  - run the script, feeding it with file names, like:
    ```bash
    tid-from-files files/* > ~/Downloads/files.json
    ```
    Output file comprises tiddlers for all files in source dir, in example above, 
    files/*
  - import output files.json via standard TW tools in web interface. Only new tiddlers
    will be imported.

 This is very first version, just to test the concept
