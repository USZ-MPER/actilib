import os
import pkg_resources
from actilib.helpers.io import load_images_from_tar
from actilib.analysis.segmentation import SegMats
from actilib.analysis.gnl import calculate_gnl

tarpath = pkg_resources.resource_filename('actilib', os.path.join('resources', 'dicom_gnl.tar.xz'))
images = load_images_from_tar(tarpath)

import matplotlib.pyplot as plt
from time import time

fig, axs = plt.subplots(3, 2, figsize=(8, 8))
gnlmap = [None, None, None]
for a, algorithm in enumerate(['generic_filter', 'convolution', 'sliding_window_view']):
    time_start = time()
    gnl1, gnl2, pixels, segmap, gnlmap[a] = calculate_gnl(dicom_images=images[0],
                                                          tissues=SegMats.SOFT_TISSUE,
                                                          return_plot_data=True,
                                                          kernel_radius_mm=2,
                                                          algorithm=algorithm)
    title = '{} ({:.1f} s) GNL = {}'.format(algorithm, time() - time_start, gnl1)
    print(title)
    axs[a, 0].set_title(title)
    axs[a, 0].set_title('difference with generic_filter')
    img = axs[a, 0].imshow(gnlmap[a], cmap='nipy_spectral', interpolation='nearest')
    plt.colorbar(img, orientation='horizontal', shrink=0.75)
    img = axs[a, 1].imshow(gnlmap[a]-gnlmap[0], cmap='nipy_spectral', interpolation='nearest')
    plt.colorbar(img, orientation='horizontal', shrink=0.75)
    axs[a, 0].set_xticks([])
    axs[a, 0].set_yticks([])
    axs[a, 1].set_xticks([])
    axs[a, 1].set_yticks([])
    plt.tight_layout()
    plt.savefig('gnl.png')  # within the loop on purpose
