# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Tornado Port Number
tornado_port = 80

# File name to store cookies
cookie_file = 'temp_cookies.lst'

# Cookie Pool Size and Rise Chance range from min to max
# This config is all about cookie pool auto-size, you can leave it default
# Explanation:
#   When we query a article, we'll pick up a cookie from cookie pool to query
#   If pool size is less than `config.pool_size_min`, we'll use an empty cookie to query
#      (And save the return cookie in cookie pool)
#   If pool size is greater than `config.pool_size_max`, we'll use an existing cookie to query
#   If pool size is in the range, we'll use existing or empty cookie randomly by the chance
pool_size_min = 5
pool_size_max = 20
rise_chance_min = 0.005
rise_chance_max = 0.08

# This is the default NOT_FOUND hint when some key is absent on sogou.com
not_found_hint = 'Not Found'

# When WeSpider can't get valid search result, will return json like
# {'url':'http://localhost/$date', 'subject':'No article found at $date'}
# Set to False to get json in error format ({'date':'$date', 'error':'No article found'})
always_return_in_format = True

# Date format, check [python.datetime](https://docs.python.org/2/library/datetime.html) for details
date_format = '%Y-%m-%d %H:%M:%S'

# Default search types. You don't need to change these.
type_acc = 'account'
type_all = 'key-all'
type_day = 'key-day'
type_week = 'key-week'
type_mon = 'key-mon'
type_year = 'key-year'
types = [type_acc, type_all, type_day, type_week, type_mon, type_year]
