#!/usr/bin/python
import re

"""
defination is called by 'compare_results' to compare dictonary against list of dictonary.a
This module is generic with respect to Reporting search, may fail for other dictonary/list comparision.  
"""
def compare_dict_with_list_dict(dict1,list2,delta):
    found=0
    for dict2 in list2:
        found=0
        for k in dict1.keys():
            if k in dict2.keys():
                try:
                    if dict1[k] == dict2[k]:
                        found = found + 1
                    elif (type(dict1[k]) is dict) and (type(dict2[k]) is unicode):  # This is modified for 'Publish Data Report'(Integration.)
                        rc=compare_results([dict1[k]],[eval(str(dict2[k]))])
                        if rc == 0:
                            found = found + 1
                        else:
                            break
                    elif (re.findall(r"[-+]?\d*\.\d+|\d+",dict1[k])[0] == dict1[k]):  #Checking value is numeric or not
                        if (abs(float(dict1[k])-(float(dict2[k]))) <= delta):
                            found = found + 1
                        else:
                            break
                    else:
                        break
                except IndexError:
                    break       
                except TypeError:
                    break
            else:
                break
        if found == len(dict1):
           return 0
    return 1


"""
Compare List of dictonaries, User can compare two list of dictonary, This module will compare list1 dictonary elements are exists in list2. 
Example:1 
  a=[{'a':'3.5','b':'2'},{'b':'2','c':'3a'}]
  b=[{'a':'113','b':'2','c':'3a'},{'a':'114','b':'2','c':'3a'},{'a':'3.3','b':'2','c':'3a'}]
  compare_results(a,b) #Result will be PASS(0), because dictonary elements belongs to 'a' are exists in 'b'
Exampl:2 
 a=[{'a':'3.8','b':'2'}]  b=[{'a':'3.5','b':'2'}]
 compare_results(a,b)  #Result will be FAIL(1), because value of dictonary element 'a' is not matching exactly. 
Example:3
 a=[{'a':'3.8','b':'2'}]  b=[{'a':'3.5','b':'2'}]
 Compare_results(a,b,0.3) #Result will be PASS(0), because comparision will be done + or - '0.3'
 i.e., (abs(3.8 - 3.5)<=0.3) ===>  (abs(- 0.3) <=0.3) ===>  (0.3 <= 0.3) ===>       #True
"""

def compare_results(list1,list2,delta=0):
    found=0
    return_hash=[]
    for dict1 in list1:
        r=compare_dict_with_list_dict(dict1,list2,delta)
        if r == 0:
            found = found + 1
        else:
            return_hash.append(dict1)
    if found == len(list1):
        return 0
    else:
        return 1,return_hash
