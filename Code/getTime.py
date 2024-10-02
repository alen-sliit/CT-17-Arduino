import urequests  # Use urequests for MicroPython HTTP requests
import ujson  # Use ujson for JSON parsing

try:
    # Send GET request to the server
    response = urequests.get("http://worldtimeapi.org/api/timezone/Asia/Colombo")
    if response.status_code == 200:
        data = json.loads(response.text)
        print("received data from server = ", data)
        datetime_str = api_response['datetime']

    # The datetime format is "YYYY-MM-DDTHH:MM:SS.SSSSSS±HH:MM"
        hours = int(datetime_str[11:13])   # Slice out the hours part
        minutes = int(datetime_str[14:16])  # Slice out the minutes part
    else:
        print("Error fetching data, status code:", response.status_code)
        
except Exception as e:
    print("Error:", e)