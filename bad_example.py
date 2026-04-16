#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
这是一个不符合百度Python编码规范的示例代码
用于演示混合搜索如何识别违规项
"""

import sys, os
from os import unlink
from xxx import *

sys.path.append('../../')

DEBUG = True
user_list = []

def process_data(a, b=[], c=time.time()):
    """处理数据"""
    global user_list
    
    result = [(x, y) for x in range(10) for y in range(5) if x * y > 10]
    
    try:
        if len(user_list) == 0:
            print 'no users'
        
        data = open("file.txt").readlines()
        
        for line in data:
            if line:
                user_list.append(line)
                
    except:
        pass
    
    return a, b, c, result, user_list


def get_user_info():
    """获取用户信息"""
    return 'zhangsan', 'MALE', 25, 'Beijing', 'Engineer'


class MyClass:
    def __init__(self):
        self.value = 1
        
    def method( self ):
        if (self.value):
            return (self.value)


def bad_exception_handling():
    try:
        raise MyException, 'Error Message'
    except Error, error:
        print error


def nested_function():
    def inner():
        def deep():
            return 1
        return deep()
    return inner()


if __name__ == '__main__':
    name,gender,age,city,job = get_user_info()
    
    unit = "seconds" if age < 60 else "minutes" if age < 3600 else "hours"
    
    if not age % 10:
        print "multiple of ten"
