# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Fixed
- Fixed typing all around the codebase (e.g. coro funcs return annotations).

### Changed
- ***Braking change***: standardized `WebSocketManager` send methods signatures.\
  Such methods now accpets only a `Message` object. This has keep the `send_msg` method clean and simple.\
  Involves the following methods:
    - `WebSocketManager._send`
    - `WebSocketManager.send`
    - `WebSocketManager._broadcast`
    - `WebSocketManager.broadcast`
    - `WebSocketManager._send_by_conn_id`
    - `WebSocketManager._send_multi_by_conn_id`
    - `WebSocketManager.send_by_conn_id`

### Removed
- ***Breaking change***: removed `WebSocketManager.send_multi_by_conn_id` method.

## [0.1.0] - 2022-10-12
### Added
- First release of the API.