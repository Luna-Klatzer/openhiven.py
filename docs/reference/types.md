# Hiven Types

---

!!! Important 

    Note that each type has a property that is *cached*! Meaning when you 
    access one, it is stored forever without any changes (deletions or updates)
    being applied to it.

    For example: When you access the *rooms* property of the House class and
    use it for a longer time and in the meantime one of them gets deleted. 
    The library will be unable to correctly delete it, since it's now stored
    by the user themselves. Therefore watch out for the proper existance!

    In the next releases a property `exists()` will be added to validate 
    the existance of objects to not possibly use an outdated one!

## List of represented Types

| List of Type                                                               | Description                                                                                 |
| :------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------ |
| [Attachment](#openhivenpy.types.attachment.Attachment)                    | Represents a Hiven message attachment containing a file                                     |
| [Context](#openhivenpy.types.context.Context)                             | Represents a Command Context for a triggered command that was registered prior              |
| [Embed](#openhivenpy.types.embed.Embed)                                   | Represents an embed message object either customised or from a website                      |
| [Entity](#openhivenpy.types.entity.Entity)                                | Represents a Hiven Entity inside a House which can contain Rooms                            |
| [Feed](#openhivenpy.types.feed.Feed)                                      | Represents the feed that is displayed on Hiven specifically for the user                    |
| [House](#openhivenpy.types.house.House)                                   | Represents a Hiven House which can contain rooms and entities                               |
| [LazyHouse](#openhivenpy.types.house.LazyHouse)                                 | Represents a Hiven House which can contain rooms and entities (Lazy)        
| [Invite](#openhivenpy.types.invite.Invite)                                | Represents an Invite to a Hiven House                                                       |
| [Member](#openhivenpy.types.member.Member)                                | Represents a House Member on Hiven which contains the Hiven User, role-data and member-data |
| [Mention](#openhivenpy.types.mention.Mention)                             | Represents an mention for a user in Hiven                                                   |
| [DeletedMessage](#openhivenpy.types.message.DeletedMessage)               | Represents a Deleted Message in a Room                                                      |
| [Message](#openhivenpy.types.message.Message)                             | Represents a standard Hiven message sent by a user                                          |
| [PrivateRoom](#openhivenpy.types.private_room.Privateroom)                 | Represents a private chat room with only one user                                           |
| [PrivateGroupRoom](#openhivenpy.types.private_room.PrivateGroupRoom)  | Represents a private group chat room with multiple users                                    |
| [Relationship](#openhivenpy.types.relationship.Relationship)              | Represents a user-relationship with another user or bot                                     |
| [TextRoom](#openhivenpy.types.textroom.TextRoom)                                  | Represents a Hiven Room inside a House                                                      |
| [User](#openhivenpy.types.user.User)                                      | Represents the standard Hiven User                                                          |
| [LazyUser](#openhivenpy.types.user.LazyUser)                              | Represents the standard Hiven User (Lazy)
| [UserTyping](#openhivenpy.types.usertyping.UserTyping)                    | Represents a Hiven User typing in a room                                                    |

::: openhivenpy.Attachment

::: openhivenpy.Context

::: openhivenpy.Embed

::: openhivenpy.Entity

::: openhivenpy.Feed

!!! Important

    The class [`LazyHouse`](##openhivenpy.types.house.LazyHouse) is inherited
    into the class [`House`](##openhivenpy.types.house.House), meaning
    all properties of the [`LazyHouse`](##openhivenpy.types.house.LazyHouse) class
    are also available in the standard [`House`](##openhivenpy.types.house.House) class

::: openhivenpy.House

::: openhivenpy.LazyHouse

::: openhivenpy.Invite

::: openhivenpy.Member

::: openhivenpy.Mention

::: openhivenpy.DeletedMessage

::: openhivenpy.Message

::: openhivenpy.PrivateRoom

::: openhivenpy.PrivateGroupRoom

::: openhivenpy.Relationship

::: openhivenpy.TextRoom

!!! Important

    The class [`LazyUser`](##openhivenpy.types.user.LazyUser) is inherited
    into the class [`User`](##openhivenpy.types.user.User), meaning
    all properties of the [`LazyUser`](##openhivenpy.types.user.LazyUser) class
    are also available in the standard [`User`](##openhivenpy.types.user.User) class

::: openhivenpy.User

::: openhivenpy.LazyUser

::: openhivenpy.UserTyping
