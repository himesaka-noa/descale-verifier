# descale-verifier
Verify a descale kernel with a video file
## Usage
```bash
python descale_verify.py -v path/to/video.m2ts [-k kernel -a param_a -b param_b] [-i interval] [-r height]
```

`kernel` is the descale kernel, available kernels are `bicubic`, `bilinear`, `lanczos`, `spline16` and `spline36`.

`a` and `b` are parameters of the kernel. For `bicubic`, they correspond to `b` and `c`. For `lanczos`, `a` is `taps`.

`interval` selects every `i` frames to process, setting it to `1` will process the whole video.

`height` is the original resolution. If the video is inspected to be 720p, then this value should be `720`.

