# Hiven Swarm Events

---

!!! Warning

    **This documentation page is not finished and due to Hiven being not stable yet, changes will and can occur**

## `INIT_STATE`
Docs · `on_init()`

!!! note

    This a unique event which does not have a parser! Though a listener is available for simple initialisation.
    
    If something listens for this event, the client will wait for it to finish (includes also multiple listeners).
    Meaning initialisation WILL NOT be done while this listener method has not returned.

The user logged successfully into the account, and the init data is sent with it to initialise the client-side (openhiven.py).

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        "user": {
            "username": str,
            "flags": str | int | None,
            "name": str,
            "id": str,
            "icon": str | None,
            "header": str | None,
            "presence": str | None
        },
        "settings": {
            "user_id": str,
            "theme": None,
            "room_overrides": {
                // room preferences mapped to their idz
                "id": { 
                    "notification_preference": int 
                }
            },
            "onboarded": unknown,
            "enable_desktop_notifications": unknown
        },
        "relationships": {
            "id": {
                "user_id": str,
                "user": {
                    "username": str,
                    "flags": str | int | None,
                    "name": str,
                    "id": str,
                    "icon": str | None,
                    "header": str | None,
                    "presence": str | None
                },
                "type": int,
                "last_updated_at": str | None
            },
        },
        "read_state": {
            "id": {
              "message_id": str,
              "mention_count": int
            },
        },
        "private_rooms": [{
            "default_permission_override": None,
            "description": str,
            "emoji": object | None,
            "house_id": None,
            "id": str,
            "last_message_id": str | None,
            "name": str,
            "owner_id": str,
            "permission_overrides": None,
            "position": None,
            "recipients": [{  
                // User Object
                "username": str,
                "flags": str | int | None,
                "name": str,
                "id": str,
                "icon": str | None,
                "header": str | None,
                "presence": str | None
            } ... ],
            "type": int
        } ... ],
        "presences": {
            "id": {
              "username": str,
              "flags": str | int | None,
              "name": str,
              "id": str,
              "icon": str | None,
              "header": str | None,
              "presence": str | None
            }
        },
        "house_memberships": [{
            "id": {
                "user_id": str,
                "user": {
                    // User Object
                    "username": str,
                    "flags": str | int | None,
                    "name": str,
                    "id": str,
                    "icon": str | None,
                    "header": str | None,
                    "presence": str | None
                },
                "roles": [],
                "last_permission_update": str | None,
                "joined_at": str,
                "house_id": str,
            }
        } ... ],
        "house_ids": [
            // list of house_ids
            "house_id",
            ...
        ]
      }
    }
    ```

## `USER_UPDATE`
[Docs · `on_user_update()`](../reference/hiven_parsers.html#openhivenpy.events.event_parsers.HivenParsers.on_user_update)

??? abstract "Expected json-data"
    ```json
    "op": 0,
    "d": {
        // User Object
        "bio": str,
        "bot": bool | None,
        "email_verified": bool,
        "header": str | None,
        "icon": str | None,
        "id": str,
        "location": str,
        "name": str,
        "flags": int,
        "username": str
    }
    ```

## `PRESENCE_UPDATE`
[Docs · `on_presence_update()`](../reference/hiven_parsers.html#openhivenpy.events.event_parsers.HivenParsers.on_presence_update)

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        // User Object
        "username": str,
        "flags": str | int | None,
        "name": str,
        "id": str,
        "icon": str | None,
        "header": str | None,
        "presence": str | None
    }
    ```

## `RELATIONSHIP_UPDATE`
[Docs · `on_relationship_update()`](../reference/hiven_parsers.html#openhivenpy.events.event_parsers.HivenParsers.on_relationship_update)

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        "user": {
            // User Object
            "website": str,
            "username": str,
            "flags": int,
            "name": str,
            "location": str,
            "id": str,
            "icon": str | None,
            "bio": str
        },
        "type": int,
        "recipient_id": str,
        "id": str
    }
    ```

## `MESSAGE_CREATE`
[Docs · `on_message_create()`](../reference/hiven_parsers.html#openhivenpy.events.event_parsers.HivenParsers.on_message_create)

??? abstract "Expected json-data - HOUSE MESSAGE "

    ```json
    "op": 0,
    "d": {
        "timestamp": int,
        "room_id": str,
        "mentions": [{
            // Mention object aka. user object
            "username": str,
            "flags": str | int | None,
            "name": str,
            "id": str,
            "icon": str | None,
            "header": str | None,
            "presence": str | None,
            "bot": bool | None
        } ... ],
        "member": {
            // Member Object
            "user_id": str,
            "user": {
                // User Object
                "username": str,
                "flags": str | int | None,
                "name": str,
                "id": str,
                "icon": str | None,
                "header": str | None,
                "presence": str | None
            },
            "roles": [{
                // Role Object
                "position": int,
                "name": str,
                "level": int,
                "id": str,
                "house_id": str,
                "deny": bits,
                "color": str, // hex
                "allow": bits
            } ... ],
            "last_permission_update": str | None,
            "joined_at": str,
            "house_id": str
        },
        "id": str,
        "house_id": str,
        "exploding_age": int | None,
        "exploding": bool,
        "device_id": str,
        "content": str,
        "bucket": int,
        "author_id": str,
        "author": {
            // User Object
            "username": str,
            "flags": str | int | None,
            "name": str,
            "id": str,
            "icon": str | None,
            "header": str | None,
            "presence": str | None
        }
        "attachment": {
            // Attachment Object
            "media_url": str,
            "filename": str,
            "dimensions": {
                "width": int,
                "type": str,
                "height": int
            }
        }
    }
    ```

??? abstract "Expected json-data - HOUSE MESSAGE "

    ```json
    {
        "author": {
            // User Object
            "username": str,
            "flags": str | int | None,
            "name": str,
            "id": str,
            "icon": str | None,
            "header": str | None,
            "presence": str | None
        },
        "author_id": str,
        "bucket": int,
        "content": str,
        "device_id": str,
        "exploding": bool,
        "exploding_age": int | None,
        "id": str,
        "mentions": [{
            // Mention object aka. user object
            "username": str,
            "flags": str | int | None,
            "name": str,
            "id": str,
            "icon": str | None,
            "header": str | None,
            "presence": str | None,
            "bot": bool | None
        } ... ],
        "recipient_ids": [
            // List of user ids - str
        ],
        "room_id": str,
        "timestamp": int
    }
    ```

## `MESSAGE_DELETE`
[Docs · `on_message_delete()`](../reference/hiven_parsers.html#openhivenpy.events.event_parsers.HivenParsers.on_message_delete)

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        "room_id": str,
        "message_id": str,
        "house_id": str
    }
    ```

## `MESSAGE_UPDATE`
[Docs · `on_message_update()`](../reference/hiven_parsers.html#openhivenpy.events.event_parsers.HivenParsers.on_message_update)

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        "type": int,
        "timestamp": str,
        "room_id": str,
        "metadata": unknown,
        "mentions": [{
            // Mention object aka. user object
            "username": str,
            "flags": str | int | None,
            "name": str,
            "id": str,
            "icon": str | None,
            "header": str | None,
            "presence": str | None
        }, ...],
        "id": str,
        "house_id": str,
        "exploding_age": int | None,
        "exploding": bool,
        "embed": {
            // Embed Object
        },
        "edited_at": str,
        "device_id": str,
        "content": str,
        "bucket": int,
        "author_id": str,
        "attachment": {
            // Attachment Object
            "media_url": str,
            "filename": str,
            "dimensions": {
                "width": int,
                "type": str,
                "height": int
            }
        }
    }
    ```

## `ROOM_CREATE`
[Docs · `on_room_create()`](../reference/hiven_parsers.html#openhivenpy.events.event_parsers.HivenParsers.on_room_create)

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        "house_id": str,
        "id": str,
        "name": str,
        "position": int,
        "type": int
    }
    ```

## `ROOM_UPDATE`
[Docs · `on_room_update)`](../reference/hiven_parsers.html#openhivenpy.events.event_parsers.HivenParsers.on_room_update)

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        "house_id": str,
        "id": str,
        "name": str,
        "position": int,
        "type": int
    }
    ```

## `ROOM_DELETE`
[Docs · `on_room_update)`](../reference/hiven_parsers.html#openhivenpy.events.event_parsers.HivenParsers.on_room_update)

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        "house_id": str,
        "id": str
    }
    ```


## `HOUSE_JOIN`
[Docs · `on_house_join()`](../reference/hiven_parsers.html#openhivenpy.events.event_parsers.HivenParsers.on_house_join)

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        "rooms": [{
            // Room Object
            "type": int,
            "recipients": None,
            "position": int,
            "permission_overrides": bits,
            "owner_id": str,
            "name": str,
            "last_message_id": str | None,
            "id": str,
            "house_id": str,
            "emoji": object | None,
            "description": str,
            "default_permission_override": int
        }, ...],
        "roles": [{
            // Role Object
            "position": int,
            "name": str,
            "level": int,
            "id": str,
            "house_id": str,
            "deny": bits,
            "color": str, // hex
            "allow": bits
        }],
        "owner_id": str,
        "name": str,
        "members": [{
            // Member Object
            "user_id": str,
            "user": {
                // User Object
                "username": str,
                "flags": str | int | None,
                "name": str,
                "id": str,
                "icon": str | None,
                "header": str | None,
                "presence": str | None
            },
            "roles": [
                "position": int,
                "name": str,
                "level": int,
                "id": str,
                "house_id": str,
                "deny": bits,
                "color": str, // hex
                "allow": bits
            ],
            "last_permission_update": str | None,
            "joined_at": str,
            "house_id": str
        }],
        "id": str,
        "icon": str | None,
        "entities": [{
            // Entity Object
            "type": int,
            "resource_pointers": [{
                // Resource Pointer
                "resource_type": str,
                "resource_id": str
            } ... ],
            "position": int,
            "name": str,
            "id": str
        } ... ],
        "default_permissions": int,
        "banner": str | None
    }
    ```

## `HOUSE_UPDATE`
[Docs · `on_house_update()`](../reference/hiven_parsers.html#openhivenpy.events.event_parsers.HivenParsers.on_house_update)

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        "rooms": [{
            // Room Object
            "type": int,
            "recipients": None,
            "position": int,
            "permission_overrides": bits,
            "owner_id": str,
            "name": str,
            "last_message_id": str | None,
            "id": str,
            "house_id": str,
            "emoji": object | None,
            "description": str,
            "default_permission_override": int
        }, ...],
        "roles": [{
            // Role Object
            "position": int,
            "name": str,
            "level": int,
            "id": str,
            "house_id": str,
            "deny": bits,
            "color": str, // hex
            "allow": bits
        }],
        "owner_id": str,
        "name": str,
        "members": [{
            // Member Object
            "user_id": str,
            "user": {
                // User Object
                "username": str,
                "flags": str | int | None,
                "name": str,
                "id": str,
                "icon": str | None,
                "header": str | None,
                "presence": str | None
            },
            "roles": [
                "position": int,
                "name": str,
                "level": int,
                "id": str,
                "house_id": str,
                "deny": bits,
                "color": str, // hex
                "allow": bits
            ],
            "last_permission_update": str | None,
            "joined_at": str,
            "house_id": str
        }],
        "id": str,
        "icon": str | None,
        "entities": [{
            // Entity Object
            "type": int,
            "resource_pointers": [{
                // Resource Pointer
                "resource_type": str,
                "resource_id": str
            } ... ],
            "position": int,
            "name": str,
            "id": str
        } ... ],
        "default_permissions": int,
        "banner": str | None
    }
    ```

## `HOUSE_LEAVE`
[Docs · `on_house_remove()`](../reference/hiven_parsers.html#openhivenpy.events.event_parsers.HivenParsers.on_house_remove)

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
      "id": str,
      "house_id": str
    }
    ```

## `HOUSE_MEMBER_JOIN`
[Docs · `on_house_member_join()`](../reference/hiven_parsers.html#openhivenpy.events.event_parsers.HivenParsers.on_house_member_join)

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        "house_id": str,
        "joined_at": timestamp,
        "roles": [{
            // Role Object
            "position": int,
            "name": str,
            "level": int,
            "id": str,
            "house_id": str,
            "deny": bits,
            "color": str, // hex
            "allow": bits 
        } ... ],
        "length": int
        "user": {
            "id": str,
            "name": str,
            "flags": str | int | None,
            "username": str,
        }
    }
    ```

## `HOUSE_MEMBER_LEAVE`
[Docs · `on_house_member_leave()`](../reference/hiven_parsers.html#openhivenpy.events.event_parsers.HivenParsers.on_house_member_leave)

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        house_id: str,
        id: str,
        joined_at: str,
        last_permission_update: str,
        presence: str,
        roles: [{
            // Role Object
            "position": int,
            "name": str,
            "level": int,
            "id": str,
            "house_id": str,
            "deny": bits,
            "color": str, // hex
            "allow": bits 
        } ... ],
        user: { 
            bot: bool,
            id: str,
            name: str,
            flags: str,
            username: str,
        },
        user_id: str
    }
    ```

## `HOUSE_MEMBER_ENTER`
[Docs · `on_house_member_online()`](../reference/hiven_parsers.html#openhivenpy.events.event_parsers.HivenParsers.on_house_member_online)

House member went online. Triggers in every house the client, and the user is in the event!

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        "user_id": str,
        "user": {
            "username": str,
            "flags": str | int | None,
            "name": str,
            "id": str,
            "icon": str | None,
            "bot": bool | None,
        },
        "roles": [{
            // Role Object
            "position": int,
            "name": str,
            "level": int,
            "id": str,
            "house_id": str,
            "deny": bits,
            "color": str, // hex
            "allow": bits 
        } ... ],
        "presence": str | None,
        "last_permission_update": null or str,
        "joined_at": str,
        "id": str,
        "house_id": str
    }
    ```


## `HOUSE_MEMBER_EXIT`
[Docs · `on_house_member_offline()`](../reference/hiven_parsers.html#openhivenpy.events.event_parsers.HivenParsers.on_house_member_offline)

House user went offline. Triggers in every house the client, and the user is in the event

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        "id": str,
        "house_id": str
    }
    ```

## `HOUSE_MEMBER_UPDATE`
[Docs · `on_member_update()`](../reference/hiven_parsers.html#openhivenpy.events.event_parsers.HivenParsers.on_member_update)

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        "user_id": str,
        "user": {
            // User Object
            "website": str,
            "username": str,
            "flags": int,
            "name": str,
            "location": str,
            "id": str,
            "icon": str | None,
            "header": str | None,
            "email_verified": bool,
            "bot": bool | None,
            "bio": str
        },
        "roles": [{
            // Role Object
            "position": int,
            "name": str,
            "level": int,
            "id": str,
            "deny": bits,
            "color": str, // hex
            "allow": bits 
        } ... ],
        "presence": str | None,
        "last_permission_update": unknown,
        "joined_at": str,
        "id": str,
        "house_id": str
    }
    ```

## `HOUSE_MEMBERS_CHUNK`
[Docs · `on_house_member_chunk()`](../reference/hiven_parsers.html#openhivenpy.events.event_parsers.HivenParsers.on_house_member_chunk)

Chunked House Member Update

??? abstract "Expected json-data"
    
    ```json
    "op": 0,
    "d": {
        "members": [{
            "id": {
                "user_id": str,
                "user": {
                "username": str,
                "flags": str | int | None,
                "name": str,
                "id": strstr
                "icon": str | None,
                "header": str | None,
                "presence": str | None
            },
            "roles": [{
                // Role Object
                "position": int,
                "name": str,
                "level": int,
                "id": str,
                "house_id": str,
                "deny": bits,
                "color": str, // hex
                "allow": bits 
            } ... ],
            "last_permission_update": str | None,
            "joined_at": str,
            "house_id": str
            }
        } ... ],
        "house_id": str
    }
    ```

## `HOUSE_ENTITIES_UPDATE`
[Docs · `on_house_entity_update()`](../reference/hiven_parsers.html#openhivenpy.events.event_parsers.HivenParsers.on_house_entity_update)

??? abstract "Expected json-data"

    ```json
    "op": 0
    "d": {
        "house_id": str,
        "entities": [{
            "type": int,
            "resource_pointers": [{
                // Resource Pointer
                "resource_type": str,
                "resource_id": str
            } ... ],
            "position": int,
            "name": str,
            "id": str
        } ... ]
    }
    ```

## `BATCH_HOUSE_MEMBER_UPDATE`
[Docs · `on_batch_house_member_update()`](../reference/hiven_parsers.html#openhivenpy.events.event_parsers.HivenParsers.on_batch_house_member_update)

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        "house_id": str,
        "batch_type": [],
        "batch_size": int,
        "data": {
            // Collection of Members that are mapped to their id
            "id": {
                // Member Object
                "user_id": str,
                "user": {
                    // User Object
                    "username": str,
                    "flags": str | int | None,
                    "name": str,
                    "id": str,
                    "icon": str | None,
                    "header": str | None,
                    "presence": str | None
                },
                "roles": [{
                    // Role Object
                    "position": int,
                    "name": str,
                    "level": int,
                    "id": str,
                    "house_id": str,
                    "deny": bits,
                    "color": str, // hex
                    "allow": bits
                } ... ],
                "last_permission_update": str | None,
                "joined_at": str,
                "house_id": str
            }
        }
    }
    ```

## `HOUSE_ENTITY_UPDATE`
[Docs · `on_house_entity_update()`](../reference/hiven_parsers.html#openhivenpy.events.event_parsers.HivenParsers.on_house_entity_update)

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        "entities": {
            // Entity Object
            "type": int,
            "resource_pointers": [{
                // Resource Pointer
                "resource_type": str,
                "resource_id": str
            } ... ],
            "position": int,
            "name": str,
            "id": str
        },
        "house_id": str
    }
    ```

## `HOUSE_DOWN`
Docs · [`on_house_down`](../reference/hiven_parsers.html#openhivenpy.events.event_parsers.HivenParsers.on_house_down) 
[/ `on_house_delete`](../reference/hiven_parsers.html#openhivenpy.events.event_parsers.HivenParsers.on_house_delete)

`HOUSE_DOWN` represents two types of events:

* House Deletion - A House was entirely deleted.
* House Downtime - The data of a house failed to load, and the server has issues recovering it.

If the given variable `unavailable` is `True`, the house with that id is currently down but not deleted. 

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        "unavailable": bool,
        "house_id": str
    }
    ```

## `TYPING_START`
[Docs · `on_typing_start()`](../reference/hiven_parsers.html#openhivenpy.events.event_parsers.HivenParsers.on_typing_start)

??? abstract "Expected json-data"

    Hiven separates the `TYPING_START` event into two classifications: 

    **House Typing:**
    
    ```json
    "op": 0,
    "d": {
        "timestamp": int,
        "room_id": str,
        "house_id": str,
        "author_id": str
    }
    ```

    **Private Room Typing:**
    ```json
    "op": 0,
    "d": {
        "author_id": int,
        "recipient_ids": [ "user_id", ... ]
        "room_id": str,
        "timestamp": int
    }
    ```

## `CALL_CREATE`
[Docs · `missing`](../reference/hiven_parsers.html#openhivenpy.events.event_parsers.HivenParsers)

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        "join_token": str,
        "recipients": ["user_id", ...],
        "ringing":["user_id", ...],
        "room_id": str,
        "rtc_states": [],
        "uuid": str,
    }
    ```

## `CALL_UPDATE`
[Docs · `missing`](../reference/hiven_parsers.html#openhivenpy.events.event_parsers.HivenParsers)

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        "join_token": str,
        "recipients": ["user_id", ...],
        "ringing":["user_id", ...],
        "room_id": str,
        "rtc_states": [
        {
            // Voice status
            "deafened": bool,
            "joined_at": int, // Unix Timestamp
            "muted": bool,
            "room_id": str,
            "video": bool
        }    
        ],
        "uuid": str,
    }
    ```

## `CALL_DELETE`
[Docs · `missing`](../reference/hiven_parsers.html#openhivenpy.events.event_parsers.HivenParsers)

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        "room_id": str
    }
    ```

## `ROLE_UPDATE`
[Docs · `missing`](../reference/hiven_parsers.html#openhivenpy.events.event_parsers.HivenParsers)

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        "position": int, 
        "name": str,
        "level": int,
        "id": str,
        "house_id": str,
        "deny": int,
        "color": str, // hex
        "allow": int
    }
    ```
