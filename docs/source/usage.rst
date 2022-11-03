Usage
=====

The software is started by runnint the script:

.. code-block::

   sh EthoProfile.sh
   
After the main window is displayed, new videos can be added to be processed. 

There are two ways to add a video to the processing queue:


#. Add video: opens a dialog where a video can be selected, displayed, and then added.

#. Add multiple videos: allows the selection of several videos in a folder and adding them to the processing queue at once.

print screens & more

The results are stored for each video in the same location as a CSV file with the name corresponding to the one of the input.

Inside the CSV file, for every frame there is a row with the frame index, annotation code and the time elapsed since the beginning of the recording - in milliseconds. 
The meaning of the annotaion code is described on the first row. 
