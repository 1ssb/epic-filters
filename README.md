# Epic Filters

# Description
This repo provides some filters for NeRF data preparation for the EPIC Kitchens Dataset as of 2023 and uses the Epic Fields JSON files which are really well prepared. Tune to your own needs.

Update: Added an unzipper file. Minimized rgb frames dataset for NeRF coming soon.

# References

1. JSON files from the EPIC Fields dataset: https://github.com/epic-kitchens/epic-Fields-code
2. Dataset from EPIC Kitchens: https://github.com/epic-kitchens/

# Requirements (as of 2023)
1. Clone this repo ``git clone https://github.com/1ssb/epic-filters``
2. Install Python 3.10
3. Install Libraries ``pip install ultralytics cv2 opencv-python Pillow tqdm``
4. Recommended to use a CUDA-enabled GPU (Tested on an RTX 4090)

PS: If you would like to use the CPU it shouldn't be too hard to modify the code. It is recommended to use concurrency-based Lock methods for the transformations in Overlap-filter.

# Usage 
Described in the pdf document.

# Cite as:
``@misc{epic-filters, title={Epic Kitchen Filters}, author={1ssb}, year={2021}, howpublished={\url{https://github.com/1ssb/epic-filters/}}}``
