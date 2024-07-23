[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
# flywheel-utilites

## What is flywheel-utilities?

`flywheel-utilities` is a Python package to help interface with the Flywheel ecosystem.
While many of the modules are simply quality of life improvements (e.g., `fly_wrappers.py` and `utils.py`),
many of the modules (e.g., `bids.py`, `download_X.py`) were designed to help analyses being performed at the subject level,
including cases where the subject may have had what should be considered a single session split into multiple sessions.
For example, when searching for a subject's T1-weighted image, the function `download_specific_bids`,
will search all of the subject's sessions to find the file. See Usage below for examples.

## Tested with

  * Python == 3.8.10
  * flywheel-gear-toolkit == 0.6.18
  * flywheel-sdk == 18.1.1

## Quick start

`flywheel-utilities` can be installed using pip. To install locally, execute the following command from this directory:

`python3 -m pip install .`

To install during a docker build, include the following in the Dockerfile with <TAG> substituted for the desired github tag:
```
RUN git clone https://github.com/Australian-Epilepsy-Project/flywheel-utilities.git -b <TAG> flywheel-utilities && \
    cd flywheel-utilities && \
    python3 -m pip install . && \
    rm -rf flywheel-utilities
```

## Usage

The following usage examples require the `gear_toolkit_context` object to be initialised.
See [here](https://flywheel-io.gitlab.io/public/gear-toolkit/flywheel_gear_toolkit/context/) for an introduction.

### Basic usage

```python
  from flywheel_utilities import fly_wrappers
  from flywheel_utilities import bids, download_bids

  fly_wrappers.check_run_level(context, "subject")
  subject = fly_wrappers.get_subject(context)

  # List of modalities to be downloaded
  MODALITIES = ['func', 'dwi']

  # Create BIDS directory structure (including dummy README and description)
  bids_dir = bid.create_bids_dir(context, subject, MODALITIES)

  # Create a BIDS derivative directory based on gear name and version
  deriv_dir = bids.create_deriv_dir(context, subject.label)

  # Download BIDS data
  download_bids.download_bids_modalities(subject, MODALITIES, bids_dir, is_dry_run=False)

  # Download BIDS data and post populate the fmap IntendedFor fields with all files from
  # dwi and func folders
  download_bids.download_bids_modalities(subject, MODALITIES, bids_dir, is_dry_run=False, ['dwi', 'func'])

  # Download specific files by performing a regex on the BIDS file names.
  # In this case the T1-weighted scan will be downloaded. You will need to alter
  # the string to match your naming conventions.
  download_bids.download_bids_files(subject, ['.*_acq-iso_rec-norm_T1w.*'], False)

```
Note: By default the function `create_deriv_dir` assumes the gear versioning follows X.X.X_Y.Y.Y,
where X.X.X is the version of the underlying BIDS app, and Y.Y.Y is the flywheel gear version.
When the BIDS directory is created, only the BIDS app version will be appended to the folder name.

To change this behaviour, the arg `which_version` can be set to:
- "second": this appends Y.Y.Y to the folder name
- "single": use this when the gear has only X.X.X as its version
- "none": use this to omit any versions from the directory name

Note: the IntendedFor fields in the json sidecars are not populated during the BIDS Curation step on Flywheel.
Instead, this information is stored in the metadata of the json file. So, when downloading fmaps, either
this IntendedFor metadata is retrieved and written into the downloaded json file, or, one can request a post
population of the IntendedFor fields which after downloading the bids data set,
will scan the desired directories and add all NIfTI files found within to the IntendedFor fields of all fmap sidecars.

### Downloading results from analysis containers

Search for successful gear runs from a particular gear and download the output based on the output file name.
This example ignores gears if they were run at the export level.
That is, produced a DICOM series rather than NIfTI files.
```python
  from flywheel_utilities import download_results

  # Create dict containing gear name, name of file to be downloaded and an
  # additional tag which is used to filter the gears via their job tags. If no tag
  # filter is used, the latest gear run will be taken
  RESULTS = {"gear_name": "fmriprep",
            "filename": "fmriprep",
            "tag": context.config['gear-search-tag']}
  download_results.download_previous_result(subject,
                                            RESULTS,
                                            context.work_dir,
                                            export_gear=False,
                                            is_dry_run=False)

```

Download a specific result using the destination ID of the analysis container.
This example assumes 'results-dest-ID' is an option in the manifest.
```python
  from flywheel_utilities import download_results

  # Analysis container destination ID
  dest_id = context.config.get('results-dest-ID')
  # Partial string matching used to find the desired output from the gear (in case
  of multiple outputs)
  filename = "freesurfer"
  analysis = context.client.get(dest_id)
  download_results.download_specific_result(analysis,
                                            filename,
                                            context.work_dir,
                                            is_dry_run=False)
```

### Downloading DICOM series based on BIDS file names

The following example shows how to use the BIDS file name of a NIfTI file to download the corresponding DICOM series.
```python
  from flywheel_utilities import download_dicoms

  # List of BIDS names to use for search
  file_names = ["dir-ap_part-phase_dwi.nii"]
  dicoms = download_dicoms.download_specific_dicoms(subject,
                                                    file_names,
                                                    context.work_dir,
                                                    is_dry_run=False)
```

### Downloading an attachment stored at the project level

The following example shows how to download an attachment stored at the project level. The download will be placed in
the working directory (defined in the context), and will be unzipped beforehand if needed.
```python
  from flywheel_utilities import download_attachments

  download_attachments.download_attachment(context, attachment_name, is_dry_run=False)
```

### Installing Freesurfer license

Install the Freesurfer license to $FREESURFER_HOME.
This assumes the Freesurfer license information is stored at the project level in "Custom Information" as string with
the key set to "FREESURFER_LICENSE" and the value set to the contents of `licence.txt`.

```python
from flywheel_utilities import freesurfer

freesurfer.install_freesurfer_license(context)
```

### Additional modules

- `basic_logging.setup_basic_logging(context)`
      - reduce overhead when setting up basic logging
- `metadata.update_subjects_tags(context, subject)`
      - update a subject's tags with the name and version of the successfully completed gear
- `resource.determine_n_cpus(re_cpus, req_omp)` and `resource.determine_max_mem(req_mem)`
      - determine number of available CPUs and memory (e.g., for fMRIPrep)

# Development and contributions

Flywheel-utilities is a new package under active development, and as such may change rapidly.
Contributions are very welcome! See [CONTRIBUTING.md](./CONTRIBUTING.md) for details.
