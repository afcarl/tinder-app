import argparse
import datetime
import logging


def parallel_function(f, sequence, num_threads=None):
    from multiprocessing import Pool
    pool = Pool(processes=num_threads)
    result = pool.map(f, sequence)
    cleaned = [x for x in result if x is not None]
    pool.close()
    pool.join()
    return cleaned


def init_logging():
    format_str = '%(asctime)12s - %(threadName)12s - %(name)18s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(format_str)
    log_filename = datetime.datetime.now().strftime('%Y-%m-%d') + '.log'
    logging.basicConfig(format=format_str,
                        filename=log_filename,
                        level=logging.INFO)
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def get_arguments(parser: argparse.ArgumentParser):
    args = None
    try:
        args = parser.parse_args()
    except Exception:
        parser.print_help()
        exit(1)
    return args
