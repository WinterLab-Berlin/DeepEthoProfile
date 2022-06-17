# Video Annotation Viewer

The application can load a video file and a .csv annotation file and view the annotations at different speeds. 
The *Modify* mode gives the user the possibility to edit the annotations. Enabling this mode will prompt for selecting a file where the manual annotation output will be stored. This file is a copy of the original file, where all the frames viewed on *Modify* mode are overwritten with the currently selected annotation.

### Other features
 - play video frame by frame
 - jump to specific frame


### Requirements:
 * The installation of the FFME 3.4+ NuGet package will be requested and is required
 * Running the software requires some FFMPEG binaries to be stored on the *ffmpeg* folder.