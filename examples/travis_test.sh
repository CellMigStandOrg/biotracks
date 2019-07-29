#!/bin/bash
# Run the create_dpkg script on the examples

(cd $(dirname "$0")/ICY/example_1 && python ../../../scripts/create_dpkg.py track_processor_ICY.xls)
(cd $(dirname "$0")/ICY/example_2 && python ../../../scripts/create_dpkg.py track_processor_ICY.xls)
(cd $(dirname "$0")/Mosaic/example_1 && python ../../../scripts/create_dpkg.py mosaic_tracks.csv)