from datetime import datetime, timedelta

def get_current_timestamp():
    # This function returns the cureent date time timestamp
    return datetime.timestamp(datetime.now())

def get_future_timestamp_in_days(days):
    # This function returns the future timestamp in days from current date time
    future_time = timedelta(days=days) + datetime.now()
    return datetime.timestamp(future_time)

def get_future_timestamp_in_secs(secs):
    # This function returns the future timestamp in seconds from current date time
    future_time = timedelta(seconds=secs) + datetime.now()
    return datetime.timestamp(future_time)
