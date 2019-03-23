# Changelog

All notable changes to this project will be documented in this file.

## 1.1.0 - 2019-03-23

### Added

- Support control validator accept and output type, add `object` parameter. #22 #24
- Add `accept_object` parameter to `str` validator. #24
- Handle invalid values more flexibly. #23 #25
- Add `invalid_to` and `invalid_to_default` parameter. #25
- Add `field` and `value` attributes to ValidrError #25

### Changed

- `validator` decorator now use `accept` and `output` to control data types, `string` argument is deprecated. #24

## 1.0.6 - 2018-10-16

### Fixed

- Fix list unique check slow #17,#21
- Fix install error when system encoding not UTF-8 #19

## 1.0.4 - 2018-08-02

### Added

- Add `is_string` and `validator` attributes to validator

## 1.0.3 - 2018-07-03

### Changed

- Support set and frozenset as schema slice keys
- Support create model with dict as position argument
- Fix copy custom validator

## 1.0.0 - 2018-06-29

### Added

- A Python based schema and validators, easy to write schema with fewer mistakes
- Model class, similar to dataclass in python 3.7

### Changed

- Not compatible with previous schema!

## 0.14.1 - 2017-05-25

This is the last version of **old schema syntax**.

### Added

- A JSON String based schema and validators, works for an internal web application
