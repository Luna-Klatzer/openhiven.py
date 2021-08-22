# JSON Object Reference

---

!!! Warning

    **This documentation page is not finished and due to Hiven being not stable yet, changes will and can occur**

## User

## Client-User

### PrivateRoom

PrivateRoom for interacting with a Hiven user or users outside a House

!!! Note

    OpenHiven.py splits the rooms into single and group rooms for easier differentiation 

```json
{
    "default_permission_override": int,
    "description": str,
    "emoji": object,
    "house_id": str,
    "id": str,
    "last_message_id": str,
    "name": str,
    "owner_id": str,
    "permission_overrides": int,
    "position": int,
    "recipients": [
      // List of users
    ],
    "type": int
}
```

### Relationship

Relationship with another Hiven User

**Types:**

*    0 - No Relationship
    
*    1 - Outgoing Friend Request
    
*    2 - Incoming Friend Request
    
*    3 - Friend
    
*    4 - Restricted User
    
*    5 - Blocked User

```json
{
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
}
```

## House

### Member

Member of a House

```json
{
    "user_id": str,
    "user": {
        // User Object
    },
    "roles": [
        // List of roles
    ],
    "last_permission_update": str,
    "joined_at": str,
    "house_id": str
}
```

### Room

```json
{
    "type": int,
    "recipients": unknown,
    "position": int,
    "permission_overrides": int,
    "owner_id": str,
    "name": str,
    "last_message_id": str,
    "id": str,
    "house_id": str,
    "emoji": object,
    "description": str,
    "default_permission_override": int
}
```

### Entity

```json
    "type": int,
    "resource_pointers": [{
        // Resource Pointer
        "resource_type": str,
        "resource_id": str
    } ... ],
    "position": int,
    "name": str,
    "id": str
```

### Role

Role of a House that can be assigned to a Member

```json
{
    "position": int,
    "name": str,
    "level": int,
    "id": str,
    "deny": bits,
    "color": str,
    "allow": bits
}
```

## Message

### Embed

### Attachment
