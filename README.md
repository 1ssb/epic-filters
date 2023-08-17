# Epic Filters

Epic Filters is a project focused on providing data filtering solutions for the EPIC Kitchens Dataset, specifically designed for Neural Radiance Fields (NeRF) training. This repository contains a collection of Python scripts that implement various filters to preprocess and enhance the dataset.

## Update

This project is an ongoing effort. We are in the process of preparing a fully processed minimal RGB frames dataset optimized for NeRF training. Stay tuned for updates.

## Resources

- [JSON files from the EPIC Fields dataset](https://github.com/epic-kitchens/epic-Fields-code)
- [EPIC Kitchens Dataset](https://github.com/epic-kitchens/)

## Preprocessing (as of 2023, using Python 3.10)

1. Download the EPIC Kitchens dataset RGB frames and the Epic Fields JSON Data.
2. Clone this repository: `git clone https://github.com/1ssb/epic-filters`
3. Configure the unzipper code with the target directory and run it: `python unzipper.py`
4. Install required libraries: `pip install ultralytics cv2 opencv-python Pillow tqdm`
5. Run the filters sequentially: overlap filter, dark filter, hands filter, and fit filter, using: `python {filter_name}.py`

**Note:** For the overlap filter, it's recommended to use a CUDA-enabled GPU (Tested on an RTX 4090). If you prefer using the CPU, the code can be modified accordingly. Concurrency-based Lock methods are recommended for transformations in the Overlap filter.

## Usage

### Hands Filter

**Motivation:** This filter selects images containing human hands while minimizing environmental occlusion. It utilizes the ultralytics YOLOv8 object detection model to identify persons and calculates the bounding box area ratio. Images with ratios below a set threshold are copied to a designated folder.

**Description:** The filter includes two main functions: "person area ratio" and "main." The former computes the bounding box area ratio of detected persons, while the latter applies this calculation to filter images. The code can be adapted for other filtering criteria or detection models.

### Frustrum Overlap Filter

**Design Choice:** This filter retains frames based on camera frustum overlap. It employs an overlap threshold and target ratio to determine the frames to keep. The code offers flexibility by accommodating various overlap reduction methods. Quaternion-format camera pose metadata from the Epic Fields dataset is employed.

**Description:** The filter consists of two functions: "calculate frustum overlap" and "select frames." The former calculates overlap ratios between frustums using projection methods, while the latter extracts camera and image information from JSON data. Frames with high overlap are pruned until the target frame count is reached.

### Post Processing

- **Dark Filter:** This script eliminates dark images from a specified directory based on a user-defined threshold value.
- **Fit Filter:** This script resizes and center-crops images in a specified directory using the PIL library.

For more comprehensive details, please refer to the [Filter Code Documentation](https://github.com/1ssb/epic-filters/blob/main/Filter_Code_Documentation.pdf).

## Cite as

@misc{epic-filters,
title={Epic Kitchen Filters},
author={Subhransu S. Bhattacharjee},
year={2023},
howpublished={https://github.com/1ssb/epic-filters/}
}


## License

&copy; 2023 Subhransu S. Bhattacharjee. This work is protected under the [MIT License](https://opensource.org/licenses/MIT).
