#-*- coding: UTF-8 -*-
'''
Miscellaneous functions
compatibility: python 3.X
'''

import datetime

def timestamp():
    """
    Formatted date and time
    """
    dtt = datetime.datetime.today()
    monthconv = {1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September', 10:'October',11:'November',12:'December'}
    return "{month} {day} {year}, {hour}:{minute}:{second}".format(year=dtt.year, month=monthconv[dtt.month], day=dtt.day, hour=dtt.hour, minute=dtt.minute, second=dtt.second)

def firstCapital(strVal):
    """
    Lower case with first capital letter
    """
    textList = list(strVal.lower())
    textList[0] = textList[0].upper()
    return ''.join(textList)
