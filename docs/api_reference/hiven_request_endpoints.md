# API Request Endpoints

---

!!! Warning

    **This documentation page is not finished and due to Hiven being not stable yet, changes will and can occur**

## Endpoints

---

!!! Important

    The possible return codes and exceptions only contain *unique* exceptions,
    meaning generic ones are not added to avoid making the docs messy!

    For generic exceptions go [here](./hiven_exceptions.html)

### User Endpoints

#### ```/users/@me```

Default user endpoint for accessing the user assigned to the passed token.

=== "GET"

    Fetches your own user data.

    **Required header:**

    ```json
    {
        "Authorization": "*************", // enter your own token
    }
    ```

    ??? success "200"

        Authorisation was successful and the body contains the requested data

        Expected Response:

        ```json
        {
            "success": true,
            "data": {
                "id": str,
                "name": str,
                "username": str,
                "icon": str | None,
                "header": str | None,
                "flags": int,
                "bot": bool | None,
                "location": str,
                "website": str,
                "bio": str,
                "email": str,
                "email_verified": bool,
                "mfa_enabled": bool
            }
        }
        ```

    ??? fail "400"

        Authorisation Token is not set or faulty! Check your header if the token was entered correctly!

        Expected Response:
        
        ```json
        {
            "success": false,
            "error": {
                "code": "no_auth",
                "message": "Authorization is required for this route"
            }
        }
        ```

=== "PATCH"

    Edits your user accounts data

    **Required body:**

    | Name                | Type                       | Description                 | Required |
    |---------------------|----------------------------|-----------------------------|----------|
    | `location`          | `str`                      | Location field of the user  | No*      |
    | `username`          | `str`                      | Display Username            | No*      |
    | `website`           | `str`                      | Display website link        | No*      |
    | `bio`               | `str`                      | Bio of the user             | No*      |
    | `header`            | `str` (base64 encoded img) | Header image of the user    | No*      |
    | `icon`              | `str` (base64 encoded img) | Icon image of the user      | No*      |

    **At least one value must be passed!*

    **Required header:**

    ```json
    {
        "Authorization": "*************", // enter your own token
    }
    ```

    ??? success "200"

        Patch was successful and the data was changed! 
        The response will containt the updated data of the User

        ```json
        {
            "success": True,
            "data": {
                "id": str,
                "name": str,
                "username": str,
                "icon": str | None,
                "header": str | None,
                "flags": int,
                "bot": bool | None,
                "location": str,
                "website": str,
                "bio": str,
                "email": str,
                "email_verified": bool,
                "mfa_enabled": bool
            }
        }
        ```

        !!! warning 
        
            If you enter an unknown or mistyped variable, it will not be correctly recognised, and the Hiven API Server 
            will change no value. Still the result will be 200 and the user-data will be sent without any changes!

#### ```/users/:username```

Endpoint for a specific user.

=== "GET"

    Fetches the user and returns the data.

    **No Required header**

    !!! Example

        GET `/users/testname`

    ??? success "200"

        Authorisation was successful and the body contains the requested data

        Expected Response:

        ```json
        {
            "success": true,
            "data": {
                "id": str,
                "name": str,
                "username": str,
                "icon": str | None,
                "header": str | None,
                "flags": int,
                "bot": bool | None,
                "location": str,
                "website": str,
                "bio": str,
                "email": str,
                "email_verified": bool,
                "mfa_enabled": bool
            }
        }
        ```

    ??? fail "400"

        **Possible Exceptions:**

        === "`user_not_found`"

            User with that id was not found

            !!! Error Response
                ```json
                {
                    "success": false,
                    "error": {
                        "code": "user_not_found",
                        "message": "That user does not exist"
                    }
                }
                ```

#### ```/users/:id```

Endpoint for a specific user based on their id. 

=== "GET"

    Fetches the user and returns the data.

    **No Required header**

    !!! Example
        GET `/users/123456789123456789`

    ??? success "200"

        Authorisation was successful and the body contains the requested data

        !!! Expected Response:
    
            ```json
            {
                "success": true,
                "data": {
                    "id": str,
                    "name": str,
                    "username": str,
                    "icon": str | None,
                    "header": str | None,
                    "flags": int,
                    "bot": bool | None,
                    "location": str,
                    "website": str,
                    "bio": str,
                    "email": str,
                    "email_verified": bool,
                    "mfa_enabled": bool
                }
            }
            ```

    ??? fail "400"

        **Possible Exceptions:**        

        === "`user_not_found`"

            User with that id was not found

            !!! Error Response
                ```json
                {
                    "success": false,
                    "error": {
                        "code": "user_not_found",
                        "message": "That user does not exist"
                    }
                }
                ```

#### ```/streams/@me/mentions```

Endpoint for fetching your mentions in the Houses and rooms of your scope.

=== "GET"
    
    Fetches the mentions in your scope.

    **Required header:**

    ```json
    {
        "Authorization": "*************", // enter your own token
    }
    ```

    ??? success "200"
    
        Returns a list with all mentions wrapped in a message Hiven object
    
        Expected Response:
    
        ```json
        {
            "success": true,
            "data": [
                {
                    "room_id": str,
                    "bucket": int,
                    "id": str,
                    "attachment": unknown,
                    "author_id": str,
                    "content": str,
                    "device_id": str,
                    "edited_at": str,
                    "embed": {},
                    "exploding": bool,
                    "exploding_age": unknown,
                    "mentions": [
                        {
                            // User object
                            "icon": str | None,
                            "id": str,
                            "username": str,
                            "name": str,
                            "header": str | None,
                            "flags": str | int | None,
                            "bot": bool | None
                        }
                        // All mentions in the message
                    ],
                    "metadata": unknown,
                    "timestamp": str,
                    "type": int,
                    "author": {
                        // User object
                        "icon": str | None,
                        "id": str,
                        "username": str,
                        "name": str,
                        "header": str | None,
                        "flags": str | int | None,
                        "bot": bool | None
                    }
                },
                ...
            ]
        }
        ```

#### `/users/@me/rooms`

Endpoint for private rooms that are not related to any House.

=== "POST"

    Creates a new private room or private group room.

    **Required body:**

    | Name                | Type                       | Description                                                    | Required |
    |---------------------|----------------------------|----------------------------------------------------------------|----------|
    | `recipient`         | `str` (user id)            | Recipient that should be added to the DM room                  | No*      |
    | `recipients`        | `List[str]` (user ids)     | Recipients that should be added to the DM room (Group Channel) | No*      |

    **At least one is required for the correct execution of the request*

    **Required header:**

    ```json
    {
        "Authorization": "*************", // enter your own token
        "Content-Type": "application/json"
    }
    ```

    ??? success "200"

        *In work*

    ??? fail "400"

        *In work*
        
#### `/users/@me/rooms/:id`

Endpoint for a specific private room based on the id.

=== "DELETE"

    Leaves a private group room.

    **Required header:**

    ```json
    {
        "Authorization": "*************", // enter your own token
    }
    ```

    ??? success "204"

        Successfully left the private group room.

    ??? fail "400"

        **Possible Exceptions:**        

        === "`method_not_allowed_on_room_type`"

            This method is not allowed on a private room, but only private
            group rooms.

            ```json
            {
                "success": false,
                "error": {
                    "code": "method_not_allowed_on_room_type",
                    "message": "This endpoint can only be called on private group rooms (room type 2"
                }
            }
            ```

#### `/users/@me/houses/:id`

Endpoint for a specific House where you are member in.

=== "DELETE"

    Leaves a house.

    **Required header:**

    ```json
    {
        "Authorization": "*************", // enter your own token
    }
    ```

    ??? success "204"

        Successfully left the house

    ??? fail "400"

        **Possible Exceptions:**        

        === "`out_of_scope`"

            The House is out of scope! You can not leave a house you are not
            in.

            ```json
            {
                "success": false,
                "error": {
                    "code": "out_of_scope",
                    "message": "you are not part of this house, so you can't leave it"
                }
            }
            ```

#### `/relationships/@me/friends/:id`

Endpoint for a user you are friends with.

=== "DELETE"

    Unfriends someone.

    **Required header:**

    ```json
    {
        "Authorization": "*************", // enter your own token
    }
    ```

    ??? success "204"

        Succesfully unfriended the user.

    ??? fail "400"

        *In work*

### House Endpoints

#### `/houses`

Endpoint for the general house collection. Only used for house creation
at the moment.

=== "POST"

    Creates a new House with the passed data.

    **Required body:**

    | Name                | Type                       | Description                 | Required |
    |---------------------|----------------------------|-----------------------------|----------|
    | `name`              | `str`                      | Name of the House           | Yes      |
    | `icon`              | `str` (base64 encoded img) | Icon image of the House     | No       |

    **Required header:**

    ```json
    {
        "Authorization": "*************", // enter your own token
        "Content-Type": "application/json"
    }
    ```

    ??? success "200"

        House Creation was successful and the newly created House is now 
        returned.

        ```json
        {
            "success": true,
            "data": {
                "id": str,
                "name": str,
                "description": str | None,
                "owner_id": str,
                "rooms": [
                    {
                        "id": str,
                        "house_id": str,
                        "name": str,
                        "position": int,
                        "type": int
                    }
                ],
                "type": int
            }
        }
        ```

    ??? fail "400"

        **Possible Exceptions:**        

        === "`invalid_schema`"

            The field `name` is missing (Required)

            ```json
            {
                "success": false,
                "error": {
                    "code": "invalid_schema",
                    "message": "Required fields (name) not met"
                }
            }
            ```
        
#### `/houses/:id`

Endpoint for a specific house based on its id.

=== "PATCH"

    Edits the house if the permissions are sufficient.

    **Required body:**

    | Name                | Type                       | Description                 | Required |
    |---------------------|----------------------------|-----------------------------|----------|
    | `name`              | `str`                      | Name of the House           | No*      |
    | `icon`              | `str` (base64 encoded img) | Icon image of the House     | No*      |

    **At least one is required for the correct execution of the request*

    **Required header:**

    ```json
    {
        "Authorization": "*************", // enter your own token
        "Content-Type": "application/json"
    }
    ```

    ??? success "200"

        Patch was successful and the data was changed! 
        The response will containt the updated value of the House

        ```json
        {
            "success": true,
            "data": {
                "name": "test2",
                "house_id": "289393198252424847"
            }
        }
        ```

    ??? fail "400"

        **Possible Exceptions:**        

        === "`invalid_schema`"

            The field `name` is missing (Required)

            ```json
            {
                "success": false,
                "error": {
                    "code": "invalid_schema",
                    "message": "Required fields (name) not met"
                }
            }
            ```

        === "`invalid_icon_file_format`"

            The passed image base64 string was not in the correct format.

            ```json
            {
                "success": false,
                "error": {
                    "code": "invalid_icon_file_format",
                    "message": "Your icon must be an image"
                }
            }
            ```

    ??? fail "500"

        **Possible Exceptions:**        

        === "`internal_server_error`"

            *Possibly* caused by a faulty base64 string, which could not be
            processed.

            ```json
            {
                "success": false,
                "error": {
                    "code": "invalid_schema",
                    "message": "Required fields (name) not met"
                }
            }
            ```

=== "DELETE"

    Deletes the house if the permissions are sufficient.

    **Required header:**

    ```json
    {
        "Authorization": "*************", // enter your own token
    }
    ```

    ??? success "204"

        House Deletion was successful.

    ??? fail "400"

        **Possible Exceptions:**        

        === "`no_permission`"

            You do not have the permissions to delete this House.

            ```json
            {
                "success": false,
                "error": {
                    "code": "no_permission",
                    "message": "You do not have permission to do this"
                }
            }
            ```

### Message Endpoints

### Room Endpoints 

### Entity Endpoint

### Invite Endpoint
