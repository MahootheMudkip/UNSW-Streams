1. For channel_messages_v1, it is assumed that a negative "start" value
   will not be assessed/tested.
2. For auth_login_v1, it is assumed that logged in users can log in more
   than once.
3. For all functions requiring a user_id, it is assumed that users could
   not be logged in when calling the respective function since auth_login
   doesn't change return anything or modify user.
4. For channel_details_v1, it is assumed that users returned in all_members 
   and owner_members does not need to be ordered
5. For channels_list_v1 and channels_listall_v1, it is assumed that channels
   returned does not need to be an orderd list 
