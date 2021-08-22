# API Request Endpoints

---

!!! Warning

    **This documentation page is not finished and due to Hiven being not stable yet, changes will and can occur**

## Endpoints

---

### User Endpoints

#### ```/users/@me```

Default user endpoint for accessing the user-data of the owner of the passed token in the header.

=== "GET"

    ??? success "200"

        Authorisation was successful and the body contains the requested data

        **Expected Response:**

        ```json
        {
            "success": true,
            "data": {
                "id": str,
                "name": str,
                "username": str,
                "icon": str,
                "header": str,
                "user_flags": int,
                "bot": bool,
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

        **Expected Response:**
        
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

    !!! note "Requires body"

        Pass at least one value that should be overwritten

        ```json
        {
            "location": str,
            "username": str,
            "website": str,
            "bio": str,
            "header": unknown,
            "icon": unknown
        }
        ```

    ??? success "200"

        Patch was successful and the data was changed! The response will containt the updated data of the User

        ```json
        {
            "success": True,
            "data": {
                "id": str,
                "name": str,
                "username": str,
                "icon": str,
                "header": str,
                "user_flags": int,
                "bot": bool,
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

    ??? fail "400"

        Authorisation Token is not set or faulty! Check your header if the token was entered correctly!

        **Expected Response:**
        
        ```json
        {
            "success": false,
            "error": {
                "code": "no_auth",
                "message": "Authorization is required for this route"
            }
        }
        ```

        !!! Warning

            Currently there is a bug in the Hiven API causing it to return 200 instead of 400 or 403!

    ??? fail "415"

        The passed content-type is faulty!
    
        **Expected Response:**
    
        ```json
        {
            "success": false,
            "error": {
                "code": "internal_server_error",
                "message": "Something went wrong interally"
            }
        }
        ```

#### ```/users/username```

Endpoint for a specific user based on their username. Will return the user if they were found.

!!! Example

    GET `/users/kudo`

=== "GET"

    ??? success "200"

        Authorisation was successful and the body contains the requested data

        **Expected Response:**

        ```json
        {
            "success": true,
            "data": {
                "id": str,
                "name": str,
                "username": str,
                "icon": str,
                "header": str,
                "user_flags": int,
                "bot": bool,
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

        User with that id was not found

        **Expected Response:**
        
        ```json
        {
            "success": false,
            "error": {
                "code": "user_not_found",
                "message": "That user does not exist"
            }
        }
        ```

        !!! Warning

            Currently there is a bug in the Hiven API causing it to return 200 instead of 400 or 403!

#### ```/users/id```

Endpoint for a specific user based on their id. Will return the user if they were found.

!!! Example

    GET `/users/175697072878514388`

=== "GET"

    ??? success "200"

        Authorisation was successful and the body contains the requested data

        **Expected Response:**

        ```json
        {
            "success": true,
            "data": {
                "id": str,
                "name": str,
                "username": str,
                "icon": str,
                "header": str,
                "user_flags": int,
                "bot": bool,
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

        User with that id was not found

        **Expected Response:**
        
        ```json
        {
            "success": false,
            "error": {
                "code": "user_not_found",
                "message": "That user does not exist"
            }
        }
        ```

        !!! Warning

            Currently there is a bug in the Hiven API causing it to return 200 instead of 400 or 403!


#### ```/streams/@me/mentions```

Endpoint for fetching your mentions in the Houses and rooms of your scope.

=== "GET"
    
    ??? success "200"
    
        Returns a list with all mentions wrapped in a message Hiven object
    
        **Expected Response:**
    
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
                            "icon": str,
                            "id": str,
                            "username": str,
                            "name": str,
                            "header": str,
                            "user_flags": str,
                            "bot": bool
                        }
                        // All mentions in the message
                    ],
                    "metadata": unknown,
                    "timestamp": str,
                    "type": int,
                    "author": {
                        // User object
                        "icon": str,
                        "id": str,
                        "username": str,
                        "name": str,
                        "header": str,
                        "user_flags": str,
                        "bot": bool
                    }
                },
                ...
            ]
        }
        ```

    ??? fail "400"

        Authorisation Token is not set or faulty! Check your header if the token was entered correctly!

        **Expected Response:**
        
        ```json
        {
            "success": false,
            "error": {
                "code": "no_auth",
                "message": "Authorization is required for this route"
            }
        }
        ```

        !!! Warning

            Currently there is a bug in the Hiven API causing it to return 200 instead of 400 or 403!

#### `users/@me/rooms`

Endpoint for private rooms that are not related to any House

=== "POST"

    ??? success "200"

    ??? fail "400"
        

### House Endpoints


### Message Endpoints


### Room Endpoints 
