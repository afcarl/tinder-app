
IMAGES_DIR=/home/philippe/TINDER-DATASET-2
OUTPUT_DIR=/home/philippe/TINDER-DATASET-2-final
RESIZE_DIMS="512,512"
EXT=png
BATCH_SIZE=8

# auxiliary constants
RESIZE_OUTPUT_DIR=${IMAGES_DIR}-resize
FACE_DETECTION_RESULTS_FILENAME=detection.txt
IMAGES_WITH_ONLY_ONE_FACE_FILENAME=images_with_one_face.txt

python resize_images_mt.py --input_dir $IMAGES_DIR --output_dir $RESIZE_OUTPUT_DIR --resize_dims $RESIZE_DIMS --extension $EXT
python face_detection.py --images_dir $RESIZE_OUTPUT_DIR --output_filename $FACE_DETECTION_RESULTS_FILENAME --batch_size $BATCH_SIZE --extension $EXT
cat $FACE_DETECTION_RESULTS_FILENAME | grep -v "\],\[" | grep -v "\[\]" | cut -f 1 > $IMAGES_WITH_ONLY_ONE_FACE_FILENAME
python copy_to_nvidia_DIGITS_dataset.py --files_to_copy $IMAGES_WITH_ONLY_ONE_FACE_FILENAME --output_dir $OUTPUT_DIR
