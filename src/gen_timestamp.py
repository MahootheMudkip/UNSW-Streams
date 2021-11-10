from datetime import datetime
from pytz import timezone

TIME_ZONE = 'Australia/Sydney'
# this is the timezone we want

# generates a timestamp of the current time converted to the given timezone
def generate_timestamp():
    # current time in utc
    utc_time = datetime.now(timezone('UTC'))
    # convert to local time zone
    local_time = utc_time.astimezone(timezone(TIME_ZONE))
    # generate timestamp and cast to int
    converted = int(local_time.timestamp())
    return converted

print(generate_timestamp())
print(int(datetime.now().timestamp()))
    

