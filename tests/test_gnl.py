import numpy as np
import os
import pkg_resources
import unittest
from actilib.helpers.io import load_images_from_tar
from actilib.analysis.segmentation import SegMats
from actilib.analysis.gnl import calculate_gnl


class TestGNL(unittest.TestCase):
    def load(self, filename):
        tarpath = pkg_resources.resource_filename('actilib', os.path.join('resources', filename))
        self.images = load_images_from_tar(tarpath)
        self.pixel_size_xy_mm = np.array(self.images[0]['header'].PixelSpacing)
        self.image_size_xy_px = np.array([len(self.images[0]['pixels']), len(self.images[0]['pixels'][0])])

    def test_gnl_calculation(self):
        self.load('dicom_gnl.tar.xz')
        gnl, std = calculate_gnl(dicom_images=self.images[0], tissues=SegMats.SOFT_TISSUE)
        self.assertAlmostEqual(gnl, 25, delta=1)
        gnl, std = calculate_gnl(dicom_images=self.images[0], tissues=SegMats.FAT)
        self.assertAlmostEqual(gnl, 4, delta=1)
        gnl, std = calculate_gnl(dicom_images=self.images[0], tissues=SegMats.BONE)
        self.assertAlmostEqual(gnl, 185, delta=1)
        gnl, std = calculate_gnl(dicom_images=self.images[0], tissues=SegMats.CUSTOM,
                                 hu_ranges={SegMats.CUSTOM: [300, 2500]})
        self.assertAlmostEqual(gnl, 676, delta=1)
