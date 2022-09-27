# Video acquisition

Caption is a small tool for video acquisition with a Picolo U16 H.264 board. It can record up to 10 video streams in parallel. 

After the start you have to select the camera sources and the destination folder. Then just press on start button to start the video recording.

The result is an MKV file with H.264 encoded video stream. Additionally, the acquisition software automatically started a new file every 6 hours (at 6, 12, 18 and 24 o'clock). This ensured that the size of individual files was easier to handle later. 

## Requirements
- Visual Studio 2022
- .NET 4.5
- NuGet package DirectShowLib
