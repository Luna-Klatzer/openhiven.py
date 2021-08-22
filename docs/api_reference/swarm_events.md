# Hiven Swarm Events

---

!!! Warning

    **This documentation page is not finished and due to Hiven being not stable yet, changes will and can occur**

## `INIT_STATE`
[:octicons-file-code-24: Source Code · ](https://github.com/Luna-Klatzer/openhiven.py/)
[Docs · `on_init()`]()

The user logged successfully into the account, and the data will now be sent back to initialise the client-side.

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        "user": {
            "username": str,
            "user_flags": str,
            "name": str,
            "id": str,
            "icon": str,
            "header": str,
            "presence": str
        },
        "settings": {
            "user_id": str,
            "theme": None,
            "room_overrides": {
                // room preferences mapped to their id
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
                    "user_flags": str,
                    "name": str,
                    "id": str,
                    "icon": str,
                    "header": str,
                    "presence": str
                },
                "type": int,
                "last_updated_at": str
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
            "emoji": object,
            "house_id": None,
            "id": str,
            "last_message_id": str,
            "name": str,
            "owner_id": str,
            "permission_overrides": None,
            "position": None,
            "recipients": [{  
                // User Object
                "username": str,
                "user_flags": str,
                "name": str,
                "id": str,
                "icon": str,
                "header": str,
                "presence": str
            } ... ],
            "type": int
        } ... ],
        "presences": {
            "id": {
              "username": str,
              "user_flags": str,
              "name": str,
              "id": str,
              "icon": str,
              "header": str,
              "presence": str
            }
        },
        "house_memberships": [{
            "id": {
                "user_id": str,
                "user": {
                    // User Object
                    "username": str,
                    "user_flags": str,
                    "name": str,
                    "id": str,
                    "icon": str,
                    "header": str,
                    "presence": str
                },
                "roles": [],
                "last_permission_update": str,
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
[:octicons-file-code-24: Source Code · ](https://github.com/Luna-Klatzer/openhiven.py/)
[Docs · `on_user_update()`]()

??? abstract "Expected json-data"
    ```json
    "op": 0,
    "d": {
        // User Object
        "bio": str,
        "bot": bool,
        "email_verified": bool,
        "header": str,
        "icon": str,
        "id": str,
        "location": str,
        "name": str,
        "user_flags": int,
        "username": str
    }
    ```

## `PRESENCE_UPDATE`
[:octicons-file-code-24: Source Code · ](https://github.com/Luna-Klatzer/openhiven.py/)

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        // User Object
        "username": str,
        "user_flags": str,
        "name": str,
        "id": str,
        "icon": str,
        "header": str,
        "presence": str
    }
    ```

## `RELATIONSHIP_UPDATE`
[:octicons-file-code-24: Source Code · ](https://github.com/Luna-Klatzer/openhiven.py/)
[Docs · `on_relationship_update()`]()

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        "user": {
            // User Object
            "website": str,
            "username": str,
            "user_flags": int,
            "name": str,
            "location": str,
            "id": str,
            "icon": str,
            "bio": str
        },
        "type": int,
        "recipient_id": str,
        "id": str
    }
    ```

## `MESSAGE_CREATE`
[:octicons-file-code-24: Source Code · ](https://github.com/Luna-Klatzer/openhiven.py/)
[Docs · `on_message_create()`]()

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        "timestamp": int,
        "room_id": str,
        "mentions": [{
            // Mention object aka. user object
            "username": str,
            "user_flags": str,
            "name": str,
            "id": str,
            "icon": str,
            "header": str,
            "presence": str,
            "bot": bool
        } ... ],
        "member": {
            // Member Object
            "user_id": str,
            "user": {
                // User Object
                "username": str,
                "user_flags": str,
                "name": str,
                "id": str,
                "icon": str,
                "header": str,
                "presence": str
            },
            "roles": [{
                // Role Object
                "position": int,
                "name": str,
                "level": int,
                "id": str,
                "deny": bits,
                "color": str,
                "allow": bits
            } ... ],
            "last_permission_update": str,
            "joined_at": str,
            "house_id": str
        },
        "id": str,
        "house_id": str,
        "exploding_age": int,
        "exploding": bool,
        "device_id": str,
        "content": str,
        "bucket": int,
        "author_id": str,
        "author": {
            // User Object
            "username": str,
            "user_flags": str,
            "name": str,
            "id": str,
            "icon": str,
            "header": str,
            "presence": str
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

## `MESSAGE_DELETE`
[:octicons-file-code-24: Source Code · ](https://github.com/Luna-Klatzer/openhiven.py/)
[Docs · `on_message_delete()`]()

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
[:octicons-file-code-24: Source Code · ](https://github.com/Luna-Klatzer/openhiven.py/)
[Docs · `on_message_update()`]()

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
            "user_flags": str,
            "name": str,
            "id": str,
            "icon": str,
            "header": str,
            "presence": str
        }, ...],
        "id": str,
        "house_id": str,
        "exploding_age": int,
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
[:octicons-file-code-24: Source Code · ](https://github.com/Luna-Klatzer/openhiven.py/)
[Docs · `on_room_create()`]()

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
[:octicons-file-code-24: Source Code · ](https://github.com/Luna-Klatzer/openhiven.py/)
[Docs · `on_room_update)`]()

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
[:octicons-file-code-24: Source Code · ](https://github.com/Luna-Klatzer/openhiven.py/)
[Docs · `on_room_update)`]()

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        "house_id": str,
        "id": str
    }
    ```


## `HOUSE_JOIN`
[:octicons-file-code-24: Source Code · ](https://github.com/Luna-Klatzer/openhiven.py/)
[Docs · `on_house_join()`]()

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
            "last_message_id": str,
            "id": str,
            "house_id": str,
            "emoji": object,
            "description": str,
            "default_permission_override": int
        }, ...],
        "roles": [{
            // Role Object
            "position": int,
            "name": str,
            "level": int,
            "id": str,
            "deny": bits,
            "color": str,
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
                "user_flags": str,
                "name": str,
                "id": str,
                "icon": str,
                "header": str,
                "presence": str
            },
            "roles": [
                "position": int,
                "name": str,
                "level": int,
                "id": str,
                "deny": bits,
                "color": str,
                "allow": bits
            ],
            "last_permission_update": str,
            "joined_at": str,
            "house_id": str
        }],
        "id": str,
        "icon": str,
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
        "banner": str
    }
    ```

## `HOUSE_LEAVE`
[:octicons-file-code-24: Source Code · ](https://github.com/Luna-Klatzer/openhiven.py/)
[Docs · `on_house_remove()`]()

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
      "id": str,
      "house_id": str
    }
    ```

## `HOUSE_MEMBER_JOIN`
[:octicons-file-code-24: Source Code · ](https://github.com/Luna-Klatzer/openhiven.py/)
[Docs · `on_house_member_join()`]()

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
            "deny": bits,
            "color": str,
            "allow": bits 
        } ... ],
        "length": int
        "user": {
            "id": str,
            "name": str,
            "user_flags": str,
            "username": str,
        }
    }
    ```

## `HOUSE_MEMBER_LEAVE`
[:octicons-file-code-24: Source Code · ](https://github.com/Luna-Klatzer/openhiven.py/)
[Docs · `on_house_member_leave()`]()

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
            "deny": bits,
            "color": str,
            "allow": bits 
        } ... ],
        user: { 
            bot: bool,
            id: str,
            name: str,
            user_flags: str,
            username: str,
        },
        user_id: str
    }
    ```

## `HOUSE_MEMBER_ENTER`
[:octicons-file-code-24: Source Code · ](https://github.com/Luna-Klatzer/openhiven.py/)

House member went online. Triggers in every house the client, and the user is in the event!

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        "user_id": str,
        "user": {
            "username": str,
            "user_flags": str,
            "name": str,
            "id": str,
            "icon": str,
            "bot": bool,
        },
        "roles": [{
            // Role Object
            "position": int,
            "name": str,
            "level": int,
            "id": str,
            "deny": bits,
            "color": str,
            "allow": bits 
        } ... ],
        "presence": str,
        "last_permission_update": null or str,
        "joined_at": str,
        "id": str,
        "house_id": str
    }
    ```


## `HOUSE_MEMBER_EXIT`
[:octicons-file-code-24: Source Code · ](https://github.com/Luna-Klatzer/openhiven.py/)
[Docs · `on_house_member_offline()`]()

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
[:octicons-file-code-24: Source Code · ](https://github.com/Luna-Klatzer/openhiven.py/)
[Docs · `on_member_update()`]()

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        "user_id": str,
        "user": {
            // User Object
            "website": str,
            "username": str,
            "user_flags": int,
            "name": str,
            "location": str,
            "id": str,
            "icon": str,
            "header": str,
            "email_verified": bool,
            "bot": bool,
            "bio": str
        },
        "roles": [{
            // Role Object
            "position": int,
            "name": str,
            "level": int,
            "id": str,
            "deny": bits,
            "color": str,
            "allow": bits 
        } ... ],
        "presence": str,
        "last_permission_update": unknown,
        "joined_at": str,
        "id": str,
        "house_id": str
    }
    ```

## `HOUSE_MEMBERS_CHUNK`
[:octicons-file-code-24: Source Code · ](https://github.com/Luna-Klatzer/openhiven.py/)
[Docs · `on_house_member_chunk()`]()

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
                "user_flags": str,
                "name": str,
                "id": strstr
                "icon": str,
                "header": str,
                "presence": str
            },
            "roles": [{
                // Role Object
                "position": int,
                "name": str,
                "level": int,
                "id": str,
                "deny": bits,
                "color": str,
                "allow": bits 
            } ... ],
            "last_permission_update": str,
            "joined_at": str,
            "house_id": str
            }
        } ... ],
        "house_id": str
    }
    ```

## `HOUSE_ENTITIES_UPDATE`
[:octicons-file-code-24: Source Code · ](https://github.com/Luna-Klatzer/openhiven.py/)
[Docs · `on_house_entity_update()`]()

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
[:octicons-file-code-24: Source Code · ](https://github.com/Luna-Klatzer/openhiven.py/)
[Docs · `on_batch_house_member_update()`]()

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
                    "user_flags": str,
                    "name": str,
                    "id": str,
                    "icon": str,
                    "header": str,
                    "presence": str
                },
                "roles": [{
                    // Role Object
                    "position": int,
                    "name": str,
                    "level": int,
                    "id": str,
                    "deny": bits,
                    "color": str,
                    "allow": bits
                } ... ],
                "last_permission_update": str,
                "joined_at": str,
                "house_id": str
            }
        }
    }
    ```

## `HOUSE_ENTITY_UPDATE`
[:octicons-file-code-24: Source Code · ](https://github.com/Luna-Klatzer/openhiven.py/)
[Docs · `on_house_entity_update()`]()

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
[:octicons-file-code-24: Source Code · Docs](https://github.com/Luna-Klatzer/openhiven.py/)
[`on_house_down`](../getting_started/event_handling.html) [/ `on_house_delete`](../getting_started/event_handling.html) 
[· `on_house_down()`]() [ · `on_house_delete()`]()

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
[:octicons-file-code-24: Source Code · ](https://github.com/Luna-Klatzer/openhiven.py/)
[Docs · `on_typing_start()`]()

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
[:octicons-file-code-24: Source Code · ](https://github.com/Luna-Klatzer/openhiven.py/)
[Docs · `missing`]()

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
[:octicons-file-code-24: Source Code · ](https://github.com/Luna-Klatzer/openhiven.py/)
[Docs · `missing`]()

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
[:octicons-file-code-24: Source Code · ](https://github.com/Luna-Klatzer/openhiven.py/)
[Docs · `missing`]()

??? abstract "Expected json-data"

    ```json
    "op": 0,
    "d": {
        "room_id": str
    }
    ```