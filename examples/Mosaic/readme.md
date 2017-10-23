## Mosaic example

The example in the *Mosaic* directory was generated using the [MosaicSuite plugin](http://mosaic.mpi-cbg.de/?q=downloads/imageJ) for ImageJ/Fiji.

Version used: `MosaicSuite-1.0.8`.

### Example 1
The dataset used in this example is the same used in the [TrackMate](../TrackMate) and other examples. The images were both detected and tracked using the Mosaic Particle Tracker tool.

#### The test dataset
The test dataset used can be uploaded in ImageJ:

`File  ▶ Open Samples  ▶ Tracks for TrackMate (807K)`

You can then open and run the Mosaic plugin selecting:

`Plugins  ▶ Mosaic  ▶ Particle Tracker 2D/3D `

Alternatively, you can download the data from this [link](http://fiji.sc/samples/FakeTracks.tif).

#### Settings to reproduce the two examples
To reproduce the example in this directory, you need to choose the following settings

- Detection settings:
    - Kernel radius: 5
    - Cutoff radius: 0.01
    - Percentile: 0.4
- Tracking settings:
    - Displacement: 10.0
    - Linkrange: 3

Once you run the tracking, you can select **All Trajectories to Table**, which opens an ImageJ table that you can save to disk.


#### Running the data_package library
Move to the example directory and run the data package creation script:

```
cd examples/Mosaic/example_1
python ../../../scripts/create_dpkg.py mosaic_tracks.csv
```