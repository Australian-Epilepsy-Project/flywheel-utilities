# Changelog

## 0.3.0 (2022-25-21)

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
