import argparse
import logging
import os
import shutil
from tqdm import tqdm

from utils import init_logging, get_arguments

logger = logging.getLogger(__name__)


def get_script_arguments():
    parser = argparse.ArgumentParser(description='Detect the faces on many images.')
    parser.add_argument('--files_to_copy', required=True, help='TXT file with absolute file paths. One line per path.')
    parser.add_argument('--output_dir', required=True, help='The name of the NVIDIA DIGITS directory.')
    args = get_arguments(parser)
    logger.info('Script inputs: {}.'.format(args))
    return args


def copy(files_to_copy: list, output_dir: str):
    for file_to_copy in tqdm(files_to_copy, desc='copy'):
        city, age, profile_id, image_filename = file_to_copy.split('/')[-4:]
        output_filename = os.path.join(output_dir, city, age, profile_id, image_filename)
        if not os.path.exists(os.path.dirname(output_filename)):
            os.makedirs(os.path.dirname(output_filename))
        shutil.copy(src=file_to_copy, dst=output_filename)
        # logger.info('COPY: {} to {}'.format(file_to_copy, output_filename))


def main():
    init_logging()
    args = get_script_arguments()
    files = open(args.files_to_copy, 'r').read().strip().split('\n')
    output_dir = args.output_dir
    copy(files_to_copy=files,
         output_dir=output_dir)


if __name__ == '__main__':
    main()
