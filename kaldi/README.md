# Kaldi Docker

The Dockerfile in this directory is used to create a version of Kaldi used by other Docker images for the purposes of
this project.

## Creation

The file was created using this command:
```
docker build -t danijel3/kaldi .
```

## Usage

Although not too useful on its own, you can run the docker using this command:
```
docker run -it danijel3/kaldi
```

This will open a command prompt where Kaldi will be installed in the path `/kaldi`. A more common use for this image is
to include it in other images.

## Todo

This image is somewhat optimized in size, although more optimizations can probably be done.

This image compiles a standard version of Kaldi, with some basic optimizations for speed. Some more Makefile changes
would be helpful.

This image uses the standard "easy-to-install" Atlas library. The greatest improvement can come from utilizing a better
math libary like OpenBlas.