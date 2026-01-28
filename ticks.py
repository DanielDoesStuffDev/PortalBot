import math

def minute_checker(time):
    convertedSeconds = 0.0
    time = time.split(":")
    timecount = len(time)-1
    for i in time:
        convertedSeconds += float(i)*(pow(60,timecount))
        timecount-=1
    if convertedSeconds > 86400:
        return False
    return round(float(convertedSeconds)/0.015,3)

def second_to_minute(time):
    if time >= 60:
        seconds = round(time % 60, 3)
        if seconds < 10:
            seconds = f"0{seconds}"

        while len(str(seconds)) <= 5:
            seconds = f"{seconds}0"

        minutes = int(time // 60)
        if minutes >= 60:
            hours = minutes // 60
            minutes = minutes % 60
            if minutes < 10:
                minutes = "0"+str(minutes)
            return f"{hours}:{minutes}:{seconds}"
        return f"{minutes}:{seconds}"
       
    else:
        if time < 10:
            while len(str(time)) <= 4:
                time = f"{time}0"
        else:
            while len(str(time)) <= 5:
                time = f"{time}0"

    return time


def time_to_tick(time):
    try:
        ticks = minute_checker(time)
        if ticks:
            if ticks.is_integer():
                correctTime = second_to_minute(round((ticks)*0.015, 3))
                return f"Your time is valid, being {int(ticks)} tick{'' if ticks == 1 else 's'} / {correctTime} seconds."
            
            else:
                floor_time = second_to_minute(round(math.floor(ticks)*0.015, 3))
                ceil_time = second_to_minute(round(math.ceil(ticks)*0.015, 3))
                return f"That time is invalid, did you mean:\n{math.floor(ticks)} tick{'' if math.floor(ticks) == 1 else 's'} / {floor_time} seconds\n{math.ceil(ticks)} tick{'' if math.ceil(ticks) == 1 else 's'} / {ceil_time} seconds."
        else:
            return "That is over a month long, I no no wanna :("
    except Exception as e:
        print(e)


def tick_to_time(ticks):
    # Convert ticks to real time
    try:
        try:
            ticks = int(ticks)
            time = round(float(ticks) * 0.015, 3)
            if time > 2678400:
                return "That is over a month long, I no no wanna :("
            if ticks == 1163:
                return f"Your ticks in real time is {second_to_minute(time)} (:heart:)"
            if ticks == 4104:
                return f"Your ticks in real time is {second_to_minute(time)} (<:no4104:1180929144977117364>)"
            return f"Your ticks in real time is {second_to_minute(time)}"
        except:
            return f"'{ticks}' was not a valid tick count, please try again!"
    except Exception as e:
        print(e)