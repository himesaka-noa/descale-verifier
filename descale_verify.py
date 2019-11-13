import vapoursynth as vs
import argparse
import descale
import numpy as np
try:
    import matplotlib
    import matplotlib.pyplot as plt
except BaseException:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
import time
import logging
from datetime import datetime
import sys

core = vs.core


def load_video(filename, interval):
    src8 = core.lsmas.LWLibavSource(filename)
    src16 = core.fmtc.bitdepth(src8, bits=16)
    return src16[::interval]


def descale_y_diff(clip, w, h, dw, dh, kernel, a, b):
    original = core.std.ShufflePlanes(clip, 0, vs.GRAY)

    if kernel == 'bicubic':
        descaled = descale.Debicubic(original, dw, dh, b=a, c=b)
        rescaled = core.resize.Bicubic(descaled, w, h, filter_param_a=a, filter_param_b=b)
    elif kernel == 'bilinear':
        descaled = descale.Debilinear(original, dw, dh)
        rescaled = core.resize.Bilinear(descaled, w, h)
    elif kernel == 'lanczos':
        descaled = descale.Delanczos(original, dw, dh, taps=int(a))
        rescaled = core.resize.Lanczos(descaled, w, h, filter_param_a=int(a))
    elif kernel == 'spline16':
        descaled = descale.Despline16(original, dw, dh)
        rescaled = core.resize.Spline16(descaled, w, h)
    elif kernel == 'spline36':
        descaled = descale.Despline36(original, dw, dh)
        rescaled = core.resize.Spline36(descaled, w, h)
    else:
        raise NotImplementedError('Kernel', kernel, 'is not implemented.')

    # you may change difference formula here
    return core.std.Expr([original, rescaled], "x y - ", vs.GRAY)


def get_statistics(clip):
    values = np.zeros(clip.num_frames)
    frame_buffs = [clip.get_frame_async(i) for i in range(clip.num_frames)]
    for i in range(clip.num_frames):
        # read the first plane into numpy array
        np_array = np.asarray(frame_buffs[i].result().get_read_array(0))
        # you may change the formula here
        values[i] = np.sum(np.abs(np_array))
        print('\r' + str(i + 1) + '/' + str(clip.num_frames), end='', flush=True)
    print()
    return values


def create_plot(data, save_filename):
    fig, ax = plt.subplots()
    t = np.arange(data.shape[0])
    ax.plot(t, data)
    ax.set(xlabel='frames', ylabel='difference',
           title='Descale Error')
    ax.grid()
    fig.savefig(save_filename + '.png')


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='utility to verify descale kernel for a video file')
    parser.add_argument('-v', type=str, dest='filename', help='path to video file', required=True)
    parser.add_argument('-r', type=int, dest='descaled_height', help='descaled resolution height', default=720)
    parser.add_argument('-i', type=int, dest='interval', help='test each X frames', default=24)
    parser.add_argument('-k', type=str, dest='kernel', help='kernel', default='bicubic')
    parser.add_argument('-a', type=float, dest='a', help='1st param of filter', default=0.0)
    parser.add_argument('-b', type=float, dest='b', help='2nd param of filter', default=0.5)
    args = parser.parse_args()
    logging.info('Descale kernel: {}, a: {}, b: {}'.format(args.kernel, args.a, args.b))
    logging.info('Video file: {}'.format(args.filename))
    src16 = load_video(args.filename, args.interval)
    logging.info('Original clip resolution: {} x {}'.format(src16.width, src16.height))
    descaled_width = args.descaled_height * src16.width // src16.height
    logging.info('Descaled resolution: {} x {}'.format(descaled_width, args.descaled_height))
    logging.info('Frames to be tested: {}'.format(src16.num_frames))
    diff_clip = descale_y_diff(src16, src16.width, src16.height, descaled_width, args.descaled_height, args.kernel,
                               args.a, args.b)
    start_time = time.time()
    statistics = get_statistics(diff_clip)
    end_time = time.time()
    print('Time used: {}s'.format(end_time - start_time))
    if sys.platform != "win32":
        save_filename = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        save_filename = datetime.now().strftime("%y-%m-%d %H-%M-%S")
    create_plot(statistics, save_filename)
    logging.info('Plot saved to {}.png'.format(save_filename))


if __name__ == '__main__':
    main()
