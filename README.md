# EbSynth Project Editor

A command-line editor for EbSynth (EBS) project files, written in Python.

## Motivation

EbSynth is a fantastic tool for style transfer.
It is based on a [public domain implementation](https://github.com/jamriska/ebsynth) of various research papers.
It is accompagnied by a pre-compiled GUI version that you can download from [ebsynth.com](https://ebsynth.com/) which adds many useful options such as Adobe After Effects export.
Unfortunately, this version is not open-source and its interface is very limited when it comes to long sequences.

This script automates the creation of EbSynth project files to synthesize long sequences.

## Usage

The `main.py` script does not requires external dependencies, just Python 3.10+.

```
$ py -3 main.py --help

usage: main.py [-h] [-i INPUT] [-o OUTPUT] [-ai [ADD_INTERVALS ...]]
               [-fps FRAMES_PER_SECOND] [-kp KEY_IMAGES_PATH]
               [-vp VIDEO_IMAGES_PATH] [-mp MASK_IMAGES_PATH]
               [-kw KEY_IMAGES_WEIGHT] [-vw VIDEO_IMAGES_WEIGHT]
               [-mw MASK_IMAGES_WEIGHT]
               [-me | --mask-images-enabled | --no-mask-images-enabled]
               [-map MAPPING] [-dfl DE_FLICKER] [-div DIVERSITY]
               [-det {1,2,3,4}] [-gpu | --use-gpu | --no-use-gpu]

Command-line editor for EbSynth (EBS) project files.

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        path to the input EBS file; if there is none, the
                        default EbSynth project is used
  -o OUTPUT, --output OUTPUT
                        path to the output EBS file; if there is none, the
                        resulting project is just printed
  -ai [ADD_INTERVALS ...], --add-intervals [ADD_INTERVALS ...]
                        add overlapping frame intervals using the syntax
                        "first:final:step:output\{i%02}\[####].png"
  -fps FRAMES_PER_SECOND, --frames-per-second FRAMES_PER_SECOND
                        set the number of frames per second
  -kp KEY_IMAGES_PATH, --key-images-path KEY_IMAGES_PATH
                        set the path to the key images
  -vp VIDEO_IMAGES_PATH, --video-images-path VIDEO_IMAGES_PATH
                        set the path to the video images
  -mp MASK_IMAGES_PATH, --mask-images-path MASK_IMAGES_PATH
                        set the path to the mask images
  -kw KEY_IMAGES_WEIGHT, --key-images-weight KEY_IMAGES_WEIGHT
                        set the weight of the key images
  -vw VIDEO_IMAGES_WEIGHT, --video-images-weight VIDEO_IMAGES_WEIGHT
                        set the weight of the video images
  -mw MASK_IMAGES_WEIGHT, --mask-images-weight MASK_IMAGES_WEIGHT
                        set the weight of the mask images
  -me, --mask-images-enabled, --no-mask-images-enabled
                        set whether or not the mask images are enabled
  -map MAPPING, --mapping MAPPING
                        set the mapping value
  -dfl DE_FLICKER, --de-flicker DE_FLICKER
                        set the de-flicker value
  -div DIVERSITY, --diversity DIVERSITY
                        set the diversity value
  -det {1,2,3,4}, --synthesis-detail {1,2,3,4}
                        set the synthesis detail value
  -gpu, --use-gpu, --no-use-gpu
                        set whether or not to use the GPU for synthesis
```

If no argument is supplied, the script creates and prints a default project with no frame interval.

```
$ py -3 main.py

Project
-------
EbSynth version:   EBS05
Frames per second: 30.0

Image paths
-----------
Key images path:   keys\[#####].png
Video images path: video\[#####].png
Mask images path:  mask\[#####].png

Image weights
-------------
Key images weight:   1.0
Video images weight: 4.0
Mask images weight:  1.0
Mask images enabled: False

Advanced
--------
Mapping:    10.0
De-flicker: 1.0
Diversity:  3500.0

Performance
-----------
Synthesis detail: 2 (Medium)
Use GPU:          True

Intervals
---------
Start    ? | Key      | Final    ? | Output
```

You can add intervals to synthesize a sequence from frame 0 to 100 with a step of 10.

```
$ py -3 main.py --add-intervals "0:100:10:out\{i%02}\[####].png"

...

Intervals
---------
Start    ? | Key      | Final    ? | Output
       0 Y |       10 |       20 Y | out\01\[####].png
      10 Y |       20 |       30 Y | out\02\[####].png
      20 Y |       30 |       40 Y | out\03\[####].png
      30 Y |       40 |       50 Y | out\04\[####].png
      40 Y |       50 |       60 Y | out\05\[####].png
      50 Y |       60 |       70 Y | out\06\[####].png
      60 Y |       70 |       80 Y | out\07\[####].png
      70 Y |       80 |       90 Y | out\08\[####].png
      80 Y |       90 |      100 Y | out\09\[####].png
```

## License

This script is placed under the MIT License; see the corresponding license file.
