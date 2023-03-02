# Changelog

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
