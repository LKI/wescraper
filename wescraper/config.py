# Tornado Port Number
tornado_port   = 80


# File name to store cookies
cookie_file    = "temp_cookies.lst"


# Cookie Pool Size, range from min to max
# This feature in in develop. Current we use 5 as static pool size - 2016-6-8
pool_size_min  = 5
pool_size_max  = 5


# This is the default NOT_FOUND hint when some key is absent on sogou.com
not_found_hint = "Not Found"


# Date format, check [python.datetime](https://docs.python.org/2/library/datetime.html) for details
date_format    = '%Y-%m-%d %H:%M:%S'


# Default search types. You don't need to change these.
type_acc  = "account"
type_all  = "key-all"
type_day  = "key-day"
type_week = "key-week"
type_mon  = "key-mon"
type_year = "key-year"
types     = [type_acc, type_all, type_day, type_week, type_mon, type_year]
