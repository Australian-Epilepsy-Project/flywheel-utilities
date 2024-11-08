# Changelog

## 0.11.1 (2024-11-08)

Hotfix to lower the required python version restriction as many gears still only using python 3.8.

### Maintenance

- https://github.com/Australian-Epilepsy-Project/flywheel-utilities/pull/42: Reduce python version restriction back down to 3.8

## 0.11.0 (2024-11-08)

Minor version increase. Required python version now 3.10. Includes bug fix release so that metadata.py no longer raises error if subject already has tag name from a specific gear.

### Maintenance

- https://github.com/Australian-Epilepsy-Project/flywheel-utilities/pull/40: Bump required python version to 3.10 and set `flywheel-sdk` version to ~= 19.0.3

### Fix

- https://github.com/Australian-Epilepsy-Project/flywheel-utilities/pull/39: `metadata.py` now no longer returns 1 if a subject already has a specified tag.

## 0.10.1 (2024-07-30)

Bug fix release to fix scenario where `dicom_specific_dicoms` would place enhanced DICOMS in the same output folder.

### Fix

- https://github.com/Australian-Epilepsy-Project/flywheel-utilities/pull/35: `download_specific_dicoms()` now handles enhanced DICOM filenames containing '.'. Previously this could cause all enhanced DICOMS to be moved into the same folder.

## 0.10.0 (2024-07-23)

Minor version release to improve `dicom_specific_dicoms` function.

### Enhancement

- https://github.com/Australian-Epilepsy-Project/flywheel-utilities/pull/33: `download_specific_dicoms()` now returns a dictionary containing as the key the regex used to find the DICOM series, and the value the corresponding Path to the downloaded DICOMS.

## 0.9.0 (2024-07-23)

Minor version release bumping the `flywheel-sdk` version and including a fix to better handle and standardise unzipping of DICOMS.

### Maintenance

- https://github.com/Australian-Epilepsy-Project/flywheel-utilities/commit/c062cce7ab01362939b2781ef05df6bff4a9cd3e: bump the `flywheel-sdk` version to => 18.1.1

### Fixed

- https://github.com/Australian-Epilepsy-Project/flywheel-utilities/pull/31: handle both classic and enhanced DICOMS the same when downloading (specific files or "all" DICOMS).

## 0.8.0 (2023-11-08)

Minor enhancement release to handle unzipping of enhanced DICOMS.

### Enhancement

- https://github.com/Australian-Epilepsy-Project/flywheel-utilities/pull/29: handle both classic and enhanced DICOMS when unzipping.

## 0.7.0 (2023-10-06)

Enhancement release, with changes to package structure

### Enhancement

- https://github.com/Australian-Epilepsy-Project/flywheel-utilities/pull/27: handle metadata on Flywheel for v2
  onwards of dcm2niix

- https://github.com/Australian-Epilepsy-Project/flywheel-utilities/pull/26: update packaging layout, add pre-commit, switch do numpy-doc style, add more type hints, update CONTRIBUTING

## 0.6.0 (2023-03-20)

Enhancement release, with some minor bug fixes

### Enhancement

- https://github.com/Australian-Epilepsy-Project/flywheel-utilities/pull/23: when trying to locate the DICOM series
  that produced a specific BIDS file, now use the SeriesNumber to unambiguously locate the series, rather than the
  filename, which can be fragile.

- https://github.com/Australian-Epilepsy-Project/flywheel-utilities/pull/24: now filter DICOMS using the
  acquisition.label on Flywheel rather than the filename itself. Should be much more robust. Also includes a bug fix
  which adds a guard against trying to unzip a non-zip file.

## 0.5.0 (2023-03-02)

Minor bug fix release

### Fixed

- https://github.com/Australian-Epilepsy-Project/flywheel-utilities/pull/22: check the container has the BIDS information field before checking for the ignore field.

## 0.5.0 (2023-02-27)

Minor release update

### Changed

- https://github.com/Australian-Epilepsy-Project/flywheel-utilities/pull/21: check at the container level whether or not the BIDS.ignore field has been checked. If so, ignore contents of containing when searching for either BIDS files or DICOMS

## 0.4.1 (2022-12-30)

Bug fix release

### Fixed

- https://github.com/Australian-Epilepsy-Project/flywheel-utilities/pull/20: fixes a bug where the recently added
  post_populate function only worked for subjects without any sessions in the BIDS path.

## 0.4.0 (2022-12-23)

Enhancement release

### Added
- https://github.com/Australian-Epilepsy-Project/flywheel-utilities/pull/14: post_populate_intended_for() function added to download_bids module to allow one to fill the IntendedFor fields of the fmaps with files in the downloaded dataset. That is, to post populate, rather then use the metadata stored on Flywheel.

### Updated
- https://github.com/Australian-Epilepsy-Project/flywheel-utilities/pull/15: certifi version increase due to security implications. See: https://groups.google.com/a/mozilla.org/g/dev-security-policy/c/oxX69KFvsm4/m/yLohoVqtCgAJ

## 0.3.0 (2022-11-25)

Enhancement release

### Added
- download_attachments module for downloading files stored as attachments at the project level

### Fixed
- Wrong description of for Freesurfer module fixed, as well as error messaging for module when the Freesurfer license
  information cannot be found

## 0.2.0 (2022-11-21)

Bug fix release along with significant formatting changes to code base.

### Fixed

- https://github.com/Australian-Epilepsy-Project/flywheel-utilities/commit/f60e179a42636ff6386c299daea4aff4f8387d56:
Populate the IntendedFor fields in the fmap sidecars. The IntendedFor information is stored as metadata, NOT in the json
sidecar. This update sources this information and writes it into the downloaded sidecars.

### Added

- requirements.txt file
- Type hints for static type checking
- Add more unit tests

### Changed

- Extend the allowable textwidth up to 120 (was 80).

## 0.1.2 (2022-09-13)

Minor bug fix.

### Fixed

- https://github.com/Australian-Epilepsy-Project/flywheel-utilities/pull/7: Catch exceptions when checking the ignore field

## 0.1.1 (2022-09-13)

Minor bug fixes.

### Fixed
- https://github.com/Australian-Epilepsy-Project/flywheel-utilities/pull/6: Check the "ignore" field in the metadata when checking if a file is correctly BIDSified

- https://github.com/Australian-Epilepsy-Project/flywheel-utilities/pull/5:  Fixed an bug which caused zip files with files but without nested folders structures to be classified as empty
