# Request Exceptions

---

!!! Warning

    **This documentation page is not finished and due to Hiven being not stable yet, changes will and can occur**

!!! Important

    The possible return codes and exceptions only contain generic exceptions,
    meaning unique ones specific for certain endpoints are not added to avoid 
    making the docs messy!

    For unique exceptions and endpoint info go [here](./hiven_request_endpoints.html)

## `400 Bad Request` - `no_auth`

If you receive this error response that means it is an issue relating the authentication which is either not passed 
in the headers or is not correct!

More info on [`Authentication Header`](./hiven_restapi.html#authentication-header)

!!! Example Exception Response

    ```json
    {
        "success": false,
        "error": {
            "code": "no_auth",
            "message": "Authorization is required for this route"
        }
    }
    ```

## `400 Bad Request` - `invalid_schema`

You selected `application/json` as `Content-Type`, but no json data was passed,
this is true for all types of requests, both that accept json data and not.

!!! Example Exception Response

    ```json
    {
        "success": false,
        "error": {
            "code": "invalid_schema",
            "message": "JSON body cannot be empty"
        }
    }
    ```

## `400 Bad Request` - `parent_entity_doesnt_exist`

The chosen parent_entity in the request does not exist in the house! 

(Usually for rooms or entities)

!!! Example Exception Response
  
    ```json
    {
        "success": false,
        "error": {
            "code": "parent_entity_doesnt_exist",
            "message": "Parent entity does not exist in this house"
        }
    }
    ```

## `404 Not Found` - `not_found`

The 404 Exception is a classic exception in the Web-Area and means here the Hiven API did not find the endpoint you
specified.

!!! Example Exception Response
  
    ```json
    {
        "success": false,
        "error": {
            "code": "not_found",
            "message": "Not found"
        }
    }
    ```

## `415 Unsupported Media Type` - `internal_server_error`
    
If you receive this error, the server encountered an internal error due to a header-issue where some data that you 
passed, or a specification causes the server to fail to perform the request.

!!! Example Exception Response

    ```json
    {
        "success": false,
        "error": {
            "code": "internal_server_error",
            "message": "Something went wrong interally"
        }
    }
    ```

## `429 Rate Limit` - `rate_limit`
    
If you receive this error, your client has sent too many requests, and it is
rate-limiting you to wait until you can send a request again.

!!! Example Exception Response
    
    ```json
    { 
      "expires_at": "<unix-timestamp>"
    }
    ```