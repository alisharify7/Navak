
def Pars_Time_Request_Vacation(data:str) -> int:
    """
        this function take time selected from employee and validate it
        only possible input args are : num{1]char{1} => 1d,1h

        numbers must between 1 - 4
    """

    if len(data) != 2:
        return 0

    if "d" in data:
        dt = data.split("d")[0]
        return int(dt)*8 if dt.isdigit() and 5> int(dt) > 0 else 0

    elif "h" in data:
        dt = data.split("h")[0]
        return int(dt) if dt.isdigit() and 5 > int(dt) > 0 else 0

    else:
        return 0


