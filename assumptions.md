1. For channel_messages_v1, it is assumed that a negative "start" value
   will not be assessed/tested.
2. For auth_login_v1, it is assumed that logged in users can log in more
   than once.
3. For all functions requiring a user_id, it is assumed that users could
   not be logged in when calling the respective function since auth_login
   doesn't change return anything or modify user.