# Changelog

All notable changes to the Compiler will be documented in this file. Note that
these changes in this file are specifically for the Compiler. The full summary
will be in the CHANGELOG.md file the main folder

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
, and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

*Note that Documentation changes should not appear here!*

## Unreleased

### Added

### Changed
 
### Removed

## [v0.2] - 2021-09-12

### Added
- Support for private rooms and private group rooms in other type objects.
  (Added proper checking of the existence of the id and finding)
- `recipient_ids` in the object `Message`.
- Property `room_id`, `house_id` and `author_id` to the `Context` class.
- New Base Type `BaseRoom` for the rooms `TextRoom`, `PrivateRoom` and `PrivateGroupRoom`.
- Added new methods `find_house_member()` and `get_house_member()` to the `HivenClient`.
- Added new method to the class `ClientCache`: `add_or_update_house_member()` 
  and `remove_house_member()`.
- Added new HTTP Exception `HTTPInvalidRequest`.
- Added proper Support for the Member Class in the cache, meaning removal and 
  addition are now properly managed.
- Listeners and proper data management for these listeners:
  - `on_room_create`
  - `on_room_update`
  - `on_room_delete`
  - `on_house_member_join`
  - `on_house_member_leave`
  - `on_house_member_online` / `on_house_member_enter`
  - `on_house_member_offline` / `on_house_member_exit`
  - `on_house_member_update`
  - `on_house_member_chunk`
  - `on_batch_house_member_update`
  - `on_house_entities_update`
  - `on_relationship_update`
  - `on_presence_update`
  - `on_message_update`
  - `on_typing_start`
- Added new decorator to the Event Parsers in `event_parsers.py` and added
  additional data log to allow for better reporting for bugs and errors in the 
  parsers. This also includes avoiding that the Connection class errors as well,
  when one of the Parsers errors.
### Changed
- Integrated usage of the `HivenClient.find_*` methods, instead of direct
  access of the storage in the type properties.
- Updated HTTP Client behaviour handling exceptions. Exceptions will be now 
  re-raised from the Client and not wrapped with a new `HTTPError` exception,
  to allow for easier error handling. This also means the functions implementing
  the HTTP Methods will be not handling their own exception handling anymore.
- Properly updated fetching methods in the class `House`: `get_room`, `find_room`,
  `get_member` and `find_member`.
- Updated `remove_house()` to also properly remove entities and rooms.  
### Removed
- Code from methods `start_call` and `send` in `PrivateRoom` and `PrivateGroupRoom`, as
  they are not functional and therefore not working yet! (Raises now `NotImplementedError`)

## [v0.2.dev4] - 2021-09-03

### Added
- Parsers for events `on_message_create` and `on_message_delete`
- New property `room_ids` to `HivenClient`
- Default coroutine behaviour for `wait_for`, which by default adds a new empty
  coro, so that the args and kwargs can be accessed as returns.
### Changed
- Moved cleanup from `HivenClient.close()` to `HivenClient.connect()` to
  clean up even when the Client closes unexpectedly or due to an issue.
- Moved `Connection` class initialisation to `HivenClient.connect()` and added
  deletion after the HivenClient closed to allow for a full-recreation if 
  the client reconnects.
- Fixed HTTP `json.JSONDecodeError` on empty responses for success returns `200`
- Moved value configuration of `host`, `api_version`, `heartbeat` and 
  `close_timeout` to `HivenClient.__init__()`
- Fixed `rooms` and `entities` property in `House`
- Fixed `mentions`, `author`, `house` and `attachment` property in `Message`
### Removed
- Unnecessary reset of Client-User and the call of `init_client_user_obj` in
  `ClientCache.closing_cleanup()`
- `log_websocket` from the `ClientCache`  

## [v0.2.dev3] - 2021-08-31

### Added
- Event Parsers for events: `HOUSE_JOIN`, `HOUSE_UPDATE`, `HOUSE_LEAVE` and `HOUSE_DOWN` (both for py-events 
  `house_down` and `house_delete`)
- Update functionality for `house_ids` property in `ClientCache`, which
  always return the current available ids for the houses.
- `house_ids` Property in `HivenClient`
- Removal functions in `ClientCache`: `remove_house`, `remove_user`, `remove_room`,
  `remove_entity`, `remove_private_room` adn `remove_relationship`
- `is_house_message` to type `House`
- `is_house_typing` to type `UserTyping`

### Changed
- Renamed py-event `house_downtime` to `house_down`
- Fixed wrong naming of `HOUSE_REMOVE` to `HOUSE_LEAVE`
- Renamed property `read_state` in `ClientCache` to `init_read_state`, due to the
  property not being updated yet!
- Fixed data issue in `HivenParsers.dispatch()`, which modifies original data
  as well. Using `deepcopy` now to avoid this issue.
- Fixed minor issue with `on_house_member_online` and `on_house_member_offline`
### Removed
- `house_memberships` property in Cache

## [v0.2.dev2] - 2021-08-23

### Added
- Full Properties of Class `User` are now added to the `HivenClient`
- `application` and `account` as new properties to `BaseUser`
- Decorator `log_type_exception` for logging exceptions in `__init__` methods
- `get_cached_data` to type Class `User`, instead of property `raw`

### Changed
- Made `flags` the base property as replacement for `user_flags`. Though 
  `user_flags` will still exist

## [v0.2.dev1] - 2021-08-13

- Rewrite of the base structure. Not all changes will be noted here, but main
  ones!

### Added
- Message-Broker for handling incoming events and distribute them to the
  listeners.
- Event-Buffers, which store the events and will one by one execute the events/
  call its listeners. This can be changed by setting queue_events in the client
  to False, which means all tasks are immediately sent to the event-loop and
  executed in the next cycle if possible.
- New event_parsers file with a new execution schema, where calling the
  function will simply add the event with its data, args and kwargs to the
  buffer.
- Added `HivenEventHandler` as a class and interface for listeners and
  functions related to that.
- Implementation of `SingleDispatchEventListener`, which will listen for an
  event once and execute an assigned coroutine when the event is received. This
  can be done dynamically using `HivenEventHandler.add_single_listener()`
- Implementation of `MultiDispatchEventListener`, which will listen for an
  event until the bot is stopped. Will call a coroutine every time the event is
  received. Creating one can be done dynamically using
  `HivenEventHandler.add_multi_listener()`
- `wait_for` function in `HivenEventHandler`, which will dynamically wait for
  an event. This will under the hood create a
  simple `SingleDispatchEventListener`. It will return the data passed to the
  function as well.
- `dispatch_event` function in `HivenEventHandler`, which will dynamically add
  a new event to the buffer with the args and kwargs passed.
- `call_listeners` to call all listeners for an event based on the passed args
  and kwargs. This will call them directly and not utilise the message-broker
  unlike `dispatch_event`
- `HTTPRateLimitError` for receiving http rate-limits (429) and parameter
  retry_on_rate_limit to raw_request()
- Parameter `remove_listeners` to `HivenClient.close()`, which will, if set to
  True, remove all listeners created using @client.event(),
  add_multi_listener() and add_single_listener()

### Changed
- Rewrite of the base structure
- Proper WebSocket structure, with init handling that will delay all other
  incoming events until the Bot is ready. This means when the Bot enters ready
  state all cached events are sent to the event-buffer.
- Base Types for referencing general types in the library
- Cache implementation using cache.py, which will hold and store values and
  provide functions for generating data and update the cache correctly. This
  will remove implementations in the data classes itself.
- Dot-Env Handling, which will now load the openhivenpy.env file on default and
  update all variables based on the given input. This will avoid None values
  when an .env file only updates a few values

### Removed
- Old structure (everything not mentioned in changed or added is likely gone)

## [v0.1.3.2] - 2021-04-09

### Added

- Updated validation
  traceback [#69](https://github.com/Luna-Klatzer/openhiven.py/issues/69)
- Updated presence to be a string and removed the deprecated and unneeded class

### Changed

- Small code enhancements before v0.2 rewrite

### Removed

- Unneeded exception log inside the exception strings and replaced it
  with `from e` to have a cleaner traceback

## [v0.1.3.1] - 2021-04-09

### Added

- Error-messages for ValidationError in from_dict() inside type classes

### Changed

- Updated MANIFEST.in
- [#68](https://github.com/Luna-Klatzer/openhiven.py/issues/68) Fixed with
  removal of name parameter in `asyncio.create_task()` which is unsupported in
  3.7

### Removed

- Old licensing of FrostbyteSpace and updated the URLs to the latest changes

## [v0.1.3] - 2021-02-16

### Added

- `HivenObject` as Base for Type Classes
- more TypeHinting using the module `typing`
- ObjectValidation as in #46 using an integration of a `@classmethod` for
  object creation as explained in #37. Will likely switch from `marshmallow` to
  another library for the sake of speed and more efficiency (or possibly own
  implementation using `@dataclass`
- `wait_for_initialisation()` and `wait_for_ready()` to the WebSocket to wait
  for the initialisation or ready state to be fired
- op-code constants to the WebSocket
- Missing Schemas and fully implemented the Validation process
- `client_user` to `PrivateRoom` and `PrivateGroupRoom`
- `bucket`, `author_id`, `exploding_age` and `device_id` to the Message Class
- Missing `CLOSED` and `CLOSING` handlers to the WebSocket
- Event `USER_UPDATE` as event and its corresponding
  event_handler `on_user_update`
- Exceptions to object initialisation and validation

### Changed

- Fixed `HivenClient.close()` for closing the HivenClient Connection
- Updated current docstrings as in #36
- Fixed circular Import errors and fixed some Type Errors
- Fixed WebSocket bug causing events to be fired before the initialisation was
  successful
- Fixed bug causing `last_message_id` sometimes to be a string and not an
  integer
- Fixed multiple WebSocket and Instance Construction bugs

### Removed

- Deprecated `timeout_handler` and replaced it with a
  standard `asyncio.wait_for()`

## [v0.1.2] - 2021-02-03

### Added

- Traceback to in-code exceptions for easier debugging and testing
- Proper docs to the HTTP Class, and it's methods
- `json` and `header` with default `None` as parameters to the HTTP method
  requests. If they are not overwritten by a passed parameter:
  - param json: Will not get passed to the requests to allow a `data` field of
    any type
  - param headers: Will be overwritten by the default headers, and the passed
    as an argument to the request
- `on_house_delete` and `on_house_member_leave` as events and added correct
  handling
- `username` option for `Client.edit(**kwargs)`
- `create_private_group_room` as method in the class `HivenClient`
- Until now missing entity object to the event `on_house_entities_update`

### Changed

- Rewrite of core Websocket Event Handling:
  - Moved handler methods from `response_handler` to the websocket object
    itself (Will be changed in the Websocket Rewrite and EventHandling Update)
- Renamed `EventHandler` event-function names and changed name prefix
  to `dispatch_{event_name}`
- Rewrote restart handler and moved the instantiation of the loop from
  `Connection.connect()` to `HivenClient.run()` and `HivenClient.connect()` to
  not be dependent on the connection object itself. This will avoid that the
  restart handler is also affected when the connection fails due to an
  exception.
- Fixed `Client.edit(**kwargs)` bug causing issues with data being passed as
  json without correct formatting. Caused by `HTTP.patch()` faulty param
  passing to `HTTP.raw_request()`
- Fixed `room_create` as event and added group room creation
- Fixed cache lists reference error caused by prior commits (houses, rooms,
  users etc.)
- Rewrote `create_private_room` in `HivenClient` to take only the `user`
  parameter instead of `user_id` and `user`
- Fixed attribute `joined_at` in the class `Member`
- Renamed object `Category` to `Entity` to be equivalent to the Hiven API
- Fixed `fetch_invite()` and `Invite` Object Creation bug
- `on_house_member_exit` to `on_house_member_offline`
  and `on_house_member_enter` to `on_house_member_online`
- Fixed `HOUSE_MEMBER_EXIT` bug causing members to be removed from houses
  instead of being set offline
- Added better traceback for exceptions, including event_listener methods to
  avoid that asyncio exceptions are thrown and
  added `log_traceback(level='error', msg='Traceback: ', suffix=None)` as
  function to utils
- Fixed `room_create` as event and added group room creation

### Removed

- `joined_at` from `User`
- `ping` from the HivenClient (Will be added back later but with better
  implementation)

[unreleased]: https://github.com/Para-C/Para-C/compare/0.2...v0.2.dev

[v0.2]: https://github.com/Para-C/Para-C/compare/0.2.dev4...0.2

[v0.2.dev4]: https://github.com/Para-C/Para-C/compare/0.2.dev3...0.2.dev4

[v0.2.dev3]: https://github.com/Para-C/Para-C/compare/0.2.dev2...0.2.dev3

[v0.2.dev2]: https://github.com/Para-C/Para-C/compare/0.2.dev1...0.2.dev2

[v0.2.dev1]: https://github.com/Para-C/Para-C/compare/v0.1.3.2...0.2.dev1

[v0.1.3.2]: https://github.com/Para-C/Para-C/compare/v0.1.2.1...v0.1.3.2

[v0.1.3.1]: https://github.com/Para-C/Para-C/compare/v0.1.3...v0.1.3.1

[v0.1.3]: https://github.com/Para-C/Para-C/compare/v0.1.2...v0.1.3

[v0.1.2]: https://github.com/Para-C/Para-C/releases/tag/v0.1.2