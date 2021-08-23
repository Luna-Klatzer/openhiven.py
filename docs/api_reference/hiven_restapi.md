# Using the REST API

---

!!! Warning

    **This documentation page is not finished and due to Hiven being not stable yet, changes will and can occur**

The Hiven API uses standard REST endpoints to allow its users to interact with it. Therefore, you can quickly write 
HTTP-requests for these endpoints as long as you specify the details. We will explain this in-depth through-out the
docs for each endpoint.

Current API access-point:

* Host: `api.hiven.io`
* Version: `v1`
* URL: `https://api.hiven.io/v1/`

## Authentication Header

---

The Hiven API uses a classic header authorization where your auth-token is passed as a parameter in the header of the
request. If you do not have your token yet, getting it is discussed in the docs page [Getting a User-token](https://openhivenpy.readthedocs.io/en/mkdocs-material-rewrite/getting_started/deploying_your_first_bot.html#getting-a-user-token)

If you already have one and want to make a request to Hiven simply put it as following into the header:
```json
{
  "Authorization": "enter your token here"
}
```

## Writing a Request with a JSON-body

### Specifying the Content-Type

Writing a request that contains data is relatively easy with Hiven and only requires you to specify what datatype 
the body you sent is, so the server can properly read it and perform the request. In this case the standard type 
`application/json` is used which allows us to pass regular data in json format to the Server. Throughout the entire API 
this is common usage for endpoints.

!!! info

    After some research, specifying the Content-Type is not required in some cases, but it is nevertheless good practice 
    setting it. Still, if it does more harm than good, you should consider removing it when it is not needed!

To specify the `application/json` datatype, add to the header this line: 
```json
{
  "Content-Type": "application/json"
}
```

### Passing values in the body

After the content-type was specified, and the configuration works, you only need to write a proper JSON-body, and it 
should work like wanted! There are exceptions to that of course, since some requests might require some additional 
information and configuration.

Body-Example:
```json
{
  "data_field": "value"
}
```

!!! warning 

    Specifying the Content-Type can cause errors if you set it on endpoints that do not expect such datatype. This can
    be the case with the methods `GET` or `DELETE` where the server expects no data except it is specifically requested.
    Such Configuration can cause the `400 Bad Request` HTTP-Exception to be returned when you send a request!

    **Common-Methods for data parsing:**
    
    * `POST`
    * `PUT`
    * `PATCH` 
