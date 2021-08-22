# Request Exceptions

---

!!! Warning

    **This documentation page is not finished and due to Hiven being not stable yet, changes will and can occur**

## `400 Bad Request` - no_auth

If you receive this error response that means it is an issue relating the authentication which is either not passed 
in the headers or is not correct!

More info on [`Authentication Header`](#authentication-header)

**Example Exception Response:**

```json
    {
        "success": false,
        "error": {
            "code": "no_auth",
            "message": "Authorization is required for this route"
        }
    }
```

## `400 Bad Request` - parent_entity_doesnt_exist

The chosen parent_entity in the request does not exist in the house! 

**Example Exception Response:**

```json
    {
        "success": false,
        "error": {
            "code": "parent_entity_doesnt_exist",
            "message": "Parent entity does not exist in this house"
        }
    }
```

## `404 Not Found` - not_found

The 404 Exception is a classic exception in the Web-Area and means here the Hiven API did not find the endpoint you
specified.

**Example Exception Response:**

```json
{
    "success": false,
    "error": {
        "code": "not_found",
        "message": "Not found"
    }
}
```

## `415 Unsupported Media Type` - internal_server_error
    
If you receive this error, the server encountered an internal error due to a header-issue where some data that you 
passed, or a specification causes the server to fail to perform the request.

**Example Exception Response:**

```json
{
    "success": false,
    "error": {
        "code": "internal_server_error",
        "message": "Something went wrong interally"
    }
}
```