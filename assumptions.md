1. If there is an invalid channel_id, then it is most likely that the given
   user_id will not be a part of that channel. In this scenario, according to
   the project spec, an InputError should be raised.

   However, the spec also states that in the case the authorised user
   is not a member of the channel, an AccessError should be raised. The spec 
   also states that in the scenario both InputError and AssertError are raised,
   AssertError takes precedence. 

   However, this doesn't quite make sense given that the main error is the 
   invalid channel_id, so I have assumed that in the case of an invalid
   channel_id, an InputError should be raised instead of an AccessError.