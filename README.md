# actilib
Python library to analyze CT images.

## How to cite this work
A paper describing this library has been submitted.
Until the publication is accepted, the initial public version of
this library can be cited via Zenodo:

[https://doi.org/10.5281/zenodo.19298157](https://doi.org/10.5281/zenodo.19298157)

# Installation

The project is available through [PyPi](https://pypi.org/project/actilib/):

    pip install actilib

# Usage

This is an example taken from the tests: 

    from actilib.helpers.io import load_images_from_directory
    from actilib.analysis.rois import SquareROI, CircleROI
    from actilib.analysis.nps import noise_properties
    from actilib.analysis.ttf import ttf_properties
    from actilib.analysis.detectability import get_dprime_default_params, calculate_dprime

    images = load_images_from_directory('PATH/TO/DICOM/FILES')
    pixel_size_xy_mm = np.array(self.images[0]['header'].PixelSpacing)
    image_size_xy_px = np.array([len(self.images[0]['pixels']), len(self.images[0]['pixels'][0])])

    # define one ROI for NPS
    nps_roi = SquareROI(64, 309, 156)
    # define three ROIs for TTF and d'
    ttf_rois = [CircleROI(16, 305.2, 293.5), CircleROI(16, 246, 202), CircleROI(16, 201, 255)]

    # calculate noise properties (once) and TTF + d' (three times)
    nps = noise_properties(images, nps_roi)
    for i in range(3):
        ttf = ttf_properties(images, ttf_rois[i])
        dprime_params = get_dprime_default_params()
        dprime_params['task_contrast_hu'] = ttf['contrast']
        dprime_params['view_observer_model'] = 'NPWE'
        dprime = calculate_dprime(nps, ttf, params=dprime_params)
        print(i, dprime)

    #
    # Plotting
    #

    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(8, 8))
    axs = axs.flatten()

    axs[0].imshow(images[0]['pixels'], cmap='gray', vmin=-300, vmax=300)
    axs[0].set_xticks([])
    axs[0].set_yticks([])
    axs[0].set_xlim([75, 512-75])
    axs[0].set_ylim([512-75, 75])
    add_roi_on_image(axs[0], nps_roi, color='white')
    add_roi_on_image(axs[0], ttf_roi[0], color='b')
    axs[0].annotate('NPS', (nps_roi.center_x() - 15, nps_roi.center_y() + 5), color='white')
    axs[0].annotate('TTF', (ttf_roi[0].center_x() + 25, ttf_roi[0].center_y() + 5), color='b')
    axs[0].set_title('Image and ROIs')

    print('Noise', 'all', nps['fpeak'], nps['fmean'], nps['noise'])
    axs[1].plot(nps['f1d'], nps['nps_1d']/np.max(nps['nps_1d']))
    axs[1].set_xlim(0, 0.75)
    axs[1].set_xlabel('spatial frequency [mm$^{-1}$]')
    axs[1].set_ylim(0, 1.1)
    axs[1].vlines(nps['fmean'], 0.0, 1.1, linestyles='--', color='gray')
    axs[1].annotate('f$_{mean}$', (nps['fmean'] + 0.01, 0.05), color='#666666')
    axs[1].set_title('Normalized Noise Power Spectrum (nNPS)')

    ttf = ttf_properties(images, ttf_rois[0])
    print('Water', 'all', ttf['f50'], ttf['contrast'])
    axs[2].plot(ttf['frq'], ttf['ttf'])
    axs[2].set_xlim(0, 0.75)
    axs[2].set_xlabel('spatial frequency [mm$^{-1}$]')
    axs[2].vlines(ttf['f50'], 0.0, 1.1, linestyles='--', color='gray')
    axs[2].annotate('f$_{50}$', (ttf['f50'] + 0.01, 0.05), color='#666666')
    axs[2].set_ylim(0, 1.1)
    axs[2].set_title('Task Transfer Function (TTF)')

    axs[3].set_title('Detectability index (d\')')
    pixel_size_xy_mm = np.array(images[0]['header'].PixelSpacing)
    dprime_params = get_dprime_default_params()
    dprime_params['task_contrast_hu'] = ttf['contrast']
    dprime_params['task_pixel_size_mm'] = pixel_size_xy_mm[0]
    dprime_params['view_pixel_size_mm'] = pixel_size_xy_mm[0]
    for model in ['NPW', 'NPWE']:
        lesion_diameters = []
        dprime_values = []
        for task_radius_mm in [1 + i for i in range(10)]:
            lesion_diameters.append(2 * task_radius_mm)
            dprime_params['task_diameter_mm'] = 2 * task_radius_mm
            dprime_params['view_observer_model'] = model
            dprime = calculate_dprime(nps, ttf, params=dprime_params)
            dprime_values.append(dprime)
        axs[3].plot(lesion_diameters, dprime_values, label=model)
        axs[3].set_xticks(lesion_diameters)
        axs[3].set_xlabel('lesion diameter [mm]')
    axs[3].legend()

    fig.tight_layout()
    fig.savefig('analysis_example.png')
    plt.close(fig)

# Data structures

## Images

Dictionary (or list of) returned by load_image* functions:

    # requires pydicom and Path - imports not shown here
    dicom_data = dcmread(input_file)
    input_file.seek(0)
    dicom_head = dcmread(input_path, stop_before_pixels=True)  # just the metadata
    image = {
        'pixels': apply_modality_lut(dicom_data.pixel_array, dicom_data),   # proper HU values
        'source': input_file.name  #
        'header': dicom_head
    }

## Noise Power Spectrum (NPS)

    nps_data = {
        'huavg': np.mean(hu_values),
        'noise': np.sqrt(np.mean(var_values)),
        'noise_std': np.std(np.sqrt(var_values)),
        'f1d': nps_freqs.tolist(),
        'f2d_x': freq_x.tolist(),
        'f2d_y': freq_y.tolist(),
        'fpeak': peak_freq,
        'fmean': mean_freq,
        'nps_1d': nps_1d.tolist(),
        'nps_2d': nps_2d.tolist()
    }

## Task Transfer Function (TTF)

If multiple images are provides as input, the default strategy ('default') is to use the information from all images to calculate only one set of values; as alternative (strategy = 'combine') the TTF properties can be calculated for each image and then the average value for each property is returned.

        return {
            'esf': esf.tolist(),
            'lsf': lsf.tolist(),
            'ttf': ttf.tolist(),
            'frq': frq.tolist(),
            'f10': f10,
            'f50': f50,
            'huavg': fgd,
            'hustd': std,
            'hubgd': bgd,
            'noise': noi,
            'contrast': nct
        }

## Detectability Index (d')

### Parameters

    default_params = {
        "task_profile": 'Flat',       # 2D shape of the object [Flat, Gaussian...]
        "task_profile_coeff": 1,      # blur factor (GaussianEdge profile) or exponent of shape (Ogival profile)
        "task_diameter_mm": 10,       # lesion diameter for simulations [mm]
        "task_contrast_hu": 15,       # contrast of the ROI [HU]
        "task_pixel_number": 300,     #
        "task_pixel_size_mm": 0.05,   # pixel size for the task function
        "view_pixel_size_mm": 0.2,    # pixel size for the display (monitor resolution)
        "view_zoom": 1,               # magnification factor to simulate display
        "view_distance_mm": 400,      #
        "view_observer_model": 'NPW', # ['NPW', 'NPWE']
        "view_eye_model": 'Saunders'  # ['Eckstein', 'Saunders']
    }

### Calculation

A scalar (float) is returned.

