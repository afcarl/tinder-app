import argparse
import concurrent.futures
import logging
import os
from PIL import Image
from glob import glob
from tqdm import tqdm

from utils import init_logging, get_arguments

logger = logging.getLogger(__name__)


def get_script_arguments():
    parser = argparse.ArgumentParser(description='Detect the faces on many images.')
    parser.add_argument('--input_dir', required=True, help='The directory with the images.')
    parser.add_argument('--output_dir', required=True, help='The output directory for the resized images.')
    parser.add_argument('--resize_dims', default='512,512', help='The resize dimensions. Default is (512, 512).')
    parser.add_argument('--extension', default='png', help='Extension of the images. Default is png.')
    args = get_arguments(parser)
    logger.info('Script inputs: {}.'.format(args))
    return args


def resize(image_path, input_base_dir, output_base_dir, resize_dims):
    fp = Image.open(image_path)
    new_image_path = image_path.replace(input_base_dir, output_base_dir)
    if not os.path.isfile(new_image_path):
        new_dir_image = os.path.dirname(new_image_path)
        fp = fp.resize(resize_dims, Image.ANTIALIAS)
        try:
            if not os.path.exists(new_dir_image):
                os.makedirs(new_dir_image)
        except FileExistsError:
            pass
        fp.save(new_image_path)


def resize_images(input_base_dir, output_base_dir, ext='png', resize_dims=(512, 512)):
    logger.info('Resizing has started.')
    image_paths = glob(input_base_dir + '/**/*.{}'.format(ext), recursive=True)
    logger.info(len(image_paths))
    # Create a pool of processes. By default, one is created for each CPU in your machine.

    with concurrent.futures.ProcessPoolExecutor(os.cpu_count()) as executor:

        futures = {
            executor.submit(resize, image_path, input_base_dir, output_base_dir, resize_dims): image_path for
            image_path
            in image_paths}
        bar = tqdm(futures, desc='resize')
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
                bar.update(1)
            except Exception:
                logger.exception('Exception occurred here.')
        bar.close()


def main():
    init_logging()
    args = get_script_arguments()
    resize_images(input_base_dir=args.input_dir,
                  output_base_dir=args.output_dir,
                  ext=args.extension,
                  resize_dims=[int(v) for v in args.resize_dims.split(',')])


if __name__ == '__main__':
    main()
