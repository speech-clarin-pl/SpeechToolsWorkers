# Speech tool scripts

These are the scripts for the speech tools used in the project.

The models for the scripts are available elsewhere. There are tags on dockerhub with images that contain specific models.

You also need to choose a folder where the input and output files will be located.

## Usage example

We'll take the file from within the root of the repo. First let's define the data directory:
```
data_dir=$(readlink -f ../work)
```

Next we can run ASR on the file within the data folder. To do this, we need to attach the data folder to the container.
The container will then read the file and from the data folder and save the output to the same folder.
The names can be given as arguments (in case you don't want to overrite any other files).
This attached folder is only used to read/write the files given as arguments.
All other files are kept within the containers temp storage.

```
docker run --rm -v $data_dir:/data danijel3/clarin-pl-speechtools:studio "/tools/Recognize/run.sh test.wav trans.txt"
```

Now we can run the same image to align the recognized transcription to the original audio:

```
docker run --rm -v $data_dir:/data danijel3/clarin-pl-speechtools:studio "/tools/ForcedAlign/run.sh test.wav trans.txt ali.ctm"
```

For longer files we can use a more lenient alignment process:

```
docker run --rm -v $data_dir:/data danijel3/clarin-pl-speechtools:studio "/tools/SegmentAlign/run.sh long.wav long.txt ali.ctm"
```