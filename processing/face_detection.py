import argparse
import json
import logging
import os
from glob import glob

import face_recognition
from slugify import slugify
from tqdm import tqdm

from utils import init_logging, get_arguments

logger = logging.getLogger(__name__)


def get_script_arguments():
    parser = argparse.ArgumentParser(description='Detect the faces on many images.')
    parser.add_argument('--images_dir', required=True, help='The directory with the images.')
    parser.add_argument('--batch_size', default=8, type=int, help='Batch size used in the model.')
    args = get_arguments(parser)
    logger.info('Script inputs: {}.'.format(args))
    return args


class Persistence:

    def __init__(self, persist_filename: str):
        self.persist_filename = persist_filename
        self.keys = {}
        self.sep = '\t'
        self.load_cache()

        self.fp = open(self.persist_filename, 'a+')

    def has_processed_image(self, image_path: str):
        return image_path in self.keys

    def has_processed_images(self, images_paths: list):
        results = []
        for image_path in images_paths:
            results.append(self.has_processed_image(image_path))
        return all(results)

    def load_cache(self):
        self.keys = {}
        if os.path.isfile(self.persist_filename):
            with open(self.persist_filename, 'r') as r:
                for l in r.readlines():
                    image_path, face_locations = l.split(self.sep)
                    self.keys[image_path] = json.loads(face_locations)
        logger.info('Found {} lines in the persistence file.'.format(len(self.keys)))

    def persist(self, image_path: str, face_locations: list):
        if image_path not in self.keys:
            self.keys[image_path] = face_locations
            self.fp.write(image_path)
            self.fp.write(self.sep)
            self.fp.write(json.dumps(face_locations, indent=0).replace('\n', ''))
            self.fp.write('\n')
            self.fp.flush()
            return True
        return False

    def close(self):
        self.fp.close()


def split(arr: list, size: int):
    arrays = []
    while len(arr) > size:
        slice_ = arr[:size]
        arrays.append(slice_)
        arr = arr[size:]
    arrays.append(arr)
    return arrays


def load_batch_images(image_paths: list):
    return list(map(face_recognition.load_image_file, image_paths))


def run_batch(batch_image_paths: list):
    batch_images = load_batch_images(batch_image_paths)
    # using the cnn face detector
    batch_face_locations = face_recognition.batch_face_locations(batch_images)
    return batch_face_locations


def run_single(image_path: str):
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image, model='cnn')
    return face_locations


class DetectFaces:

    def __init__(self, images_dir: str, batch_size: int, ext: str = 'png'):
        # Because it can be long to detect all the faces.
        self.images_dir = images_dir
        self.batch_size = batch_size
        self.persistence_filename = slugify(self.images_dir) + '.log'
        self.persistence = Persistence(self.persistence_filename)
        self.ext = ext
        self.glob_syntax = self.images_dir + '/**/*.{}'.format(self.ext)
        self.image_paths = sorted(glob(self.glob_syntax, recursive=True))
        logger.info('Running face detection on {}.'.format(self.images_dir))
        logger.info('Inferred GLOB syntax is {}.'.format(self.glob_syntax))
        logger.info('Batch size used for the CNN model is {}.'.format(self.batch_size))
        logger.info('Found {} image files.'.format(len(self.image_paths)))

    def _run_batch_detection(self):
        assert self.batch_size >= 2
        image_path_batchs = split(self.image_paths, size=self.batch_size)
        bar = tqdm(image_path_batchs, desc='face detection')
        for batch_image_paths in bar:
            if not self.persistence.has_processed_images(batch_image_paths):
                batch_face_locations = run_batch(batch_image_paths)
                bar.set_description('{} ... {}'.format(batch_image_paths[0], batch_image_paths[-1]))
                self.persist_batch(batch_image_paths, batch_face_locations)
            else:
                logger.info('[{}] already persisted. Skipping.'.format(str(batch_image_paths)))
        bar.close()
        self.persistence.close()

    def _run_single_detection(self):
        assert self.batch_size == 1
        bar = tqdm(self.image_paths, desc='face detection')
        for image_path in bar:
            if not self.persistence.has_processed_image(image_path):
                face_locations = run_single(image_path)
                bar.set_description(image_path)
                self.persist_batch([image_path], [face_locations])
            else:
                logger.info('[{}] already persisted. Skipping.'.format(image_path))
        bar.close()
        self.persistence.close()

    def run_detection(self):
        if self.batch_size > 1:
            self._run_batch_detection()
        else:
            self._run_single_detection()

    def persist_batch(self, batch_image_paths: list, batch_face_locations: list):
        for image_path, face_location in zip(batch_image_paths, batch_face_locations):
            if not self.persistence.persist(image_path, face_location):
                logger.info('[{}] already persisted. Skipping.'.format(image_path))


def main():
    init_logging()
    arguments = get_script_arguments()
    detect_faces = DetectFaces(arguments.images_dir, arguments.batch_size)
    detect_faces.run_detection()


if __name__ == '__main__':
    main()
