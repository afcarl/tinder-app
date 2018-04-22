import argparse
import logging
import os
from glob import glob

from PIL import Image
from tqdm import tqdm

from utils import init_logging, get_arguments

logger = logging.getLogger(__name__)


def get_script_arguments():
    parser = argparse.ArgumentParser(description='Detect the faces on many images.')
    parser.add_argument('--input_dir', required=True, help='The directory with the images.')
    parser.add_argument('--output_dir', required=True, help='The output directory for the resized images.')
    parser.add_argument('--resize_dims', default='(512, 512)', help='The resize dimensions. Default is (512, 512).')
    parser.add_argument('--extension', default='png', help='Extension of the images. Default is png.')
    args = get_arguments(parser)
    logger.info('Script inputs: {}.'.format(args))
    return args


def resize_images(input_base_dir, output_base_dir, ext='png', resize_dims=(512, 512)):
    logger.info('Resizing has started.')
    image_paths = glob(input_base_dir + '/**/*.{}'.format(ext), recursive=True)
    bar = tqdm(image_paths, desc='resize')
    for image_path in bar:
        try:
            fp = Image.open(image_path)
            bar.set_description('resizing {} => {}'.format(fp.size, resize_dims))
            new_image_path = image_path.replace(input_base_dir, output_base_dir)
            new_dir_image = os.path.dirname(new_image_path)
            fp = fp.resize(resize_dims, Image.ANTIALIAS)
            if not os.path.exists(new_dir_image):
                os.makedirs(new_dir_image)
            fp.save(new_image_path)

        except IOError as ioe:
            logger.exception('Exception occurred here.')
            logger.error('error: {} skipping.'.format(ioe))
    bar.close()


def main():
    init_logging()
    args = get_script_arguments()
    resize_images(input_base_dir=args.input_dir,
                  output_base_dir=args.output_dir,
                  ext=args.extension,
                  resize_dims=[int(v) for v in list(args.resize_dims)])


if __name__ == '__main__':
    main()
