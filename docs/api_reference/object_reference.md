# JSON Object Reference

---

!!! Warning

    **This documentation page is not finished and due to Hiven being not stable yet, changes will and can occur**

## Default User

Full possible data of a User. *Usually* only visible to the client!

```json
{
    "account": str | int | None,
    "username": str,
    "name": str,
    "id": str,
    "flags": str | int | None,
    "user_flags": str | int | None, // deprecated, rarely available
    "bio": str | None,
    "email_verified": bool | None,
    "header": str, // empty when not filled
    "icon": str, // empty when not filled
    "bot": bool | None,
    "application": str | int | None,
}
```

## Lazy User

Base User that is available to everyone.

```json
{
    "account": str | int | None,
    "flags": str | int | None,
    "header": str, // empty when not filled
    "icon": str, // empty when not filled
    "id": str,
    "name": str,
    "username": str
}
```

## Objects for the Client-User

### PrivateRoom

PrivateRoom for interacting with a Hiven user or users outside a House

!!! Note

    OpenHiven.py splits the rooms into single and group rooms for easier differentiation 

```json
{
    "default_permission_override": int,
    "description": str,
    "emoji": object | None,
    "house_id": str,
    "id": str,
    "last_message_id": str | None,
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
        "flags": str | int | None,
        "name": str,
        "id": str,
        "icon": str | None,
        "header": str | None,
        "presence": str | None
    },
    "type": int,
    "last_updated_at": str | None
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
    "last_permission_update": str | None,
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
    "last_message_id": str | None,
    "id": str,
    "house_id": str,
    "emoji": object | None,
    "description": str,
    "default_permission_override": int
}
```

### Entity

```json
{
  "type": int,
  "resource_pointers": [
    {
      // Resource Pointer
      "resource_type": str,
      "resource_id": str
    }
    ...
  ],
  "position": int,
  "name": str,
  "id": str
}
```

### Role

Role of a House that can be assigned to a Member

```json
{
    "position": int,
    "name": str,
    "level": int,
    "id": str,
    "house_id": str,
    "deny": bits,
    "color": str, // hex
    "allow": bits
}
```

## Message

### Embed

### Attachment
