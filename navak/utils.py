from khayyam import JalaliDatetime

import datetime
import khayyam

def gregorian_to_jalali(gy, gm, gd):
 g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
 if (gm > 2):
  gy2 = gy + 1
 else:
  gy2 = gy
 days = 355666 + (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) + gd + g_d_m[gm - 1]
 jy = -1595 + (33 * (days // 12053))
 days %= 12053
 jy += 4 * (days // 1461)
 days %= 1461
 if (days > 365):
  jy += (days - 1) // 365
  days = (days - 1) % 365
 if (days < 186):
  jm = 1 + (days // 31)
  jd = 1 + (days % 31)
 else:
  jm = 7 + ((days - 186) // 30)
  jd = 1 + ((days - 186) % 30)
 return [jy, jm, jd]


def jalali_to_gregorian(jy, jm, jd):
 jy += 1595
 days = -355668 + (365 * jy) + ((jy // 33) * 8) + (((jy % 33) + 3) // 4) + jd
 if (jm < 7):
  days += (jm - 1) * 31
 else:
  days += ((jm - 7) * 30) + 186
 gy = 400 * (days // 146097)
 days %= 146097
 if (days > 36524):
  days -= 1
  gy += 100 * (days // 36524)
  days %= 36524
  if (days >= 365):
   days += 1
 gy += 4 * (days // 1461)
 days %= 1461
 if (days > 365):
  gy += ((days - 1) // 365)
  days = (days - 1) % 365
 gd = days + 1
 if ((gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0)):
  kab = 29
 else:
  kab = 28
 sal_a = [0, 31, kab, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
 gm = 0
 while (gm < 13 and gd > sal_a[gm]):
  gd -= sal_a[gm]
  gm += 1
 return [gy, gm, gd]


def convert_dt2_khayyam(dt: datetime.datetime):
    """
        this function take an datetime and return
        a khayyam object
    :param dt:
    :return:
    """
    date = gregorian_to_jalali(gy=dt.year, gm=dt.month, gd=dt.day)
    return khayyam.JalaliDate(year=date[0], month=date[1], day=date[2])



def convert_kh2_datetimeD(dt: datetime.datetime):
    """
        this function take an datetime and return
        a khayyam object
    :param dt:
    :return:
    """
    date = jalali_to_gregorian(jy=dt.year, jm=dt.month, jd=dt.day)
    return datetime.date(year=date[0], month=date[1], day=date[2])


def validate_date(dt: str):
    """
        this function take a string date like=> "2023/10/1"
        and make sure that input is date
    :return: JalaliDatetime.date if valid date otherWise False
    """

    if len(dt_arry := dt.split("/")) != 3:
        return False

    try:
        dt_obj = JalaliDatetime(year=dt_arry[-3], month=dt_arry[-2], day=dt_arry[-1])
        return dt_obj.date()
    except ValueError:
        return False


def validate_phone(dt: str):
    """
        this view take an phone number ins tring format and validate it
    :return: phone:int if valid phonenumber otherWise False
    """

    if len(dt) != 11:
        return False

    if not dt.isdigit():
        return False

    return dt
