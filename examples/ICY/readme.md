## ICY examples

The examples in the *ICY* directory were generated using the [ICY platform](http://icy.bioimageanalysis.org/).
See the descriptions below for more information on each example.

#### Example 1
The dataset used in this example was generated through the [Particle tracking benchmark generator](http://icy.bioimageanalysis.org/plugin/Particle_tracking_benchmark_generator) plugin for ICY - `version 1.0.1.0`.

##### Settings for the Particle_tracking_benchmark_generator plugin
The [configuration file](example_1/particle_tracking_config.txt) contains the settings used to run the plugin.

!! Do not forget to **change the `saveDir` property from `'/Users/me/Desktop/benchmark'` to something meaningful** !!

In the interface of the `Particle_tracking_benchmark_generator` plugin load this file, and the settings will be automatically imported.
Then `run` the file, and the sequence of images/tracks generated will be both visualized and saved in the `'/Users/me/Desktop/benchmark'` directory you chose.

##### The TrackManager plugin and the Track_Processor_export_track_to_Excel
Once the data are generated, the [TrackManager](http://icy.bioimageanalysis.org/plugin/Track_Manager) plugin starts, showing the identified tracks.
In the **TrackManager** interface, click on  `add Track Processor...` and selct the [`Track Processor export track to Excel`](http://icy.bioimageanalysis.org/plugin/Track_Processor_export_track_to_Excel).

You will need to point to an Excel file (best if you use a `.xls` instead of `.xlsx` extension), and the tracks will be exported to this file.
The file will look like the [track_processor_ICY.xls](example_1/track_processor_ICY.xls) file.

##### Running the data_package library
The library will run a set of intermediate steps:
- first create a plain CSV file from the Excel file: [`track_processor_ICY.csv`](example_1/track_processor_ICY.csv)
- then, because the formatting of the resulting CSV is pretty strange, an extra reformatting is performed, writing the tracks to the [`track_processor_ICY_clean.CSV`](example_1/track_processor_ICY_clean.csv)
- this last file is eventually used to create the  `data_package` format.
