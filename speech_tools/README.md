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
The names can be given as arguments (in case you don't want to overwrite any other files).
This attached folder is only used to read/write the files given as arguments.
All other files are kept within the container's temp storage.

```
docker run --rm -v $data_dir:/data danijel3/clarin-pl-speechtools:studio "/tools/Recognize/run.sh test.wav trans.txt"
```

To compute WER, we can use the standard built-in Kaldi utility:

```
docker run --rm -v $data_dir:/data danijel3/clarin-pl-speechtools:studio "/kaldi/src/bin/compute-wer ark:/data/test.txt ark:/data/trans.txt"
```

Now we can run the same image to align the recognized transcription to the original audio:

```
docker run --rm -v $data_dir:/data danijel3/clarin-pl-speechtools:studio "/tools/ForcedAlign/run.sh test.wav trans.txt ali.ctm"
```

For longer files we can use a more lenient alignment process:

```
docker run --rm -v $data_dir:/data danijel3/clarin-pl-speechtools:studio "/tools/SegmentAlign/run.sh long.wav long.txt ali.ctm"
```

To perform speech activity detection (SAD, aka VAD):

```
docker run --rm -v $data_dir:/data danijel3/clarin-pl-speechtools:studio "/tools/SpeechActivityDetection/run.sh switchboard.wav vad.ctm"
```

You might want to convert the file to a Praat TextGrid for analysis:

```
docker run --rm -v $data_dir:/data danijel3/clarin-pl-speechtools:studio "python /dist/local_utils/convert_ctm_tg.py /data/vad.ctm /data/vad.TextGrid"
```

We can also try speaker diarization:

```
docker run --rm -v $data_dir:/data danijel3/clarin-pl-speechtools:studio "/tools/SpeakerDiarization/run.sh switchboard.wav spk.ctm"
```

To perform keyword spotting, use this command:

```
docker run --rm -v $data_dir:/data danijel3/clarin-pl-speechtools:sejm "/tools/KeywordSpotting/run.sh sejm.wav keywords.txt sejm.kws"
```

To perform G2P on a wordlist, we have a small script:

```
docker run -it --rm -v $data_dir:/data danijel3/clarin-pl-speechtools:studio "/tools/misc/transcribe_word_list.sh wordlist lexicon"
```

You can retrain a G2P model using the following command (the new model can be used in the above command by overriding the `--model-path` switch):

```
docker run -it --rm -v $data_dir:/data danijel3/clarin-pl-speechtools "/tools/misc/train_g2p.sh lexicon model.fst"
```