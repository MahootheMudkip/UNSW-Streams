from datetime import datetime
from pytz import timezone

TIME_ZONE = 'UTC'
# time zone

# generates a timestamp
def get_curr_timestamp():
    # current time in utc timestamp
    timestamp = int(datetime.now(timezone(TIME_ZONE)).timestamp())
    return timestamp

# print(generate_timestamp())
# print(int(datetime.now().timestamp()))
    

