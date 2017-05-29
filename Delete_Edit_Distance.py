##############################################################
# Coding Challenge TripleByte
##############################################################
# Write a function that returns the delete edit distance of 2 strings
# via the sum of each removed character's unicode code point value (i.e. 'a' = 97)
# Example "cat" and "ct" is edit distance 97 cause you just need to remove the
# 'a' character to make the strings equivalent


str1 = 'cAt'
str2 = 'cat'

counter = 0
global counter
print '--------------------------------------'
print 'starting strings'
print 'str1 = ' + str1 + ' , str2 = ' + str2
print '--------------------------------------'

def compare_two_strings(str1,str2,counter):
    if counter == 0:
        original_str1 = str1
        original_str2 = str2
    
    # finding letters not found in one string or the other
    diff_set = set(str1).symmetric_difference(set(str2))
    print 'diff_set: ' + str(diff_set)
    for each in eval(str(diff_set)):
        counter = counter + str1.count(each)
        counter = counter + str2.count(each)
        str1 = str1.replace(each,'')
        str2 = str2.replace(each,'')
    print 'after removing letters not found in both strings'
    print 'new str1: ' + str1 + ' , new str2: ' + str2
    #######
    
    # each1_list stores the max characters found in str1 that can be found
    # in str2
    # each1_type stores position of a letter after the first (1..n) in str1
    # each1_length stores the length (1...n) from each1_type position
    each1_list = []
    each1_type = []
    each1_length = []
    # looping through 1..n letters of str1
    for each1 in range(1, len(str1) + 1):
        # truncating str1 to see if it's in str2
        temp = str1[0:each1]
        if str2.find(temp) >= 0:
            each1_list.append(each1)
            each1_type.append(0)
            each1_length.append(len(temp))

    
    # position of removal (1 = 2nd letter)
    for i in range(1, len(str1)):
        # length of removal
        for j in range(i + 1, len(str1)):
            temp = list(str1)
            temp[i : j] = ''
            temp = ''.join(temp)
            # print 'new str1: ' + temp
            if str2.find(temp)>=0:
                each1_list.append(len(temp))
                each1_type.append(i)
                each1_length.append(j - i)
                
    each2_list = []
    each2_type = []
    each2_length = []
    for each2 in range(1, len(str2) + 1):
        temp = str2[0:each2]
        if str1.find(temp) >= 0:
            each2_list.append(each2)
            each2_type.append(0)
            each2_length.append(len(temp))
            
    for i in range(1, len(str2)):
        for j in range(i + 1, len(str2)):
            temp = list(str2)
            temp[i : j] = ''
            temp = ''.join(temp)
            print 'new str2: ' + temp
            if str1.find(temp)>=0:
                each2_list.append(len(temp))
                each2_type.append(i)
                each2_length.append(j-i)
                    

    try:
        # use either str1 or str2 that preserves the most common letters
        if (max(each2_list) > max(each1_list)):

            m = max(each2_list)
            indices = [i for i, j in enumerate(each2_list) if j == m]
            type_list = []
            len_list = []
            for each in indices:
                type_list.append(each2_type[each])
                len_list.append(each2_length[each])
            
            if min(type_list) == 0:
                ind_ = str1.find(str2[0:max(each2_list)])
                str1 = str1[ind_:]
                counter = counter + ind_
            else:
                str2_original = str2
                str2 = list(str2)
                str2[type_list[0]:type_list[0] + len_list[0]] = ''
                str2 = ''.join(str2)
                counter = counter + (len(str2_original) - len(str2))

        elif max(each2_list) < max(each1_list):
            m = max(each1_list)
            print 'm' + ' = ' + str(m)
            indices = [i for i, j in enumerate(each1_list) if j == m]
            type_list = []
            len_list = []
            for each in indices:
                type_list.append(each1_type[each])
                len_list.append(each1_length[each])

            if min(type_list) == 0:
                ind_ = str2.find(str1[0:max(each1_list)])
                str2 = str2[ind_:]
                counter = counter + ind_
            else:
                str1_original = str1
                str1 = list(str1)
                str1[type_list[0]:type_list[0] + len_list[0]] = ''
                str1 = ''.join(str1)
                counter = counter + (len(str1_original) - len(str1))


        else: # equal
            counter = counter + (len(str2) - len(str2[0:max(each2_list)]))
            str2 = str2[0:max(each2_list)]
            counter = counter + (len(str1) - len(str1[0:max(each1_list)]))
            str1 = str1[0:max(each1_list)]
    except:
        # values are both blank
        pass
    
    if str2 == str1:
        print 'SUCCESS'
        print '###-----FINAL-----####'
        print original_str1 + ' to ' + str1
        print original_str2 + ' to ' + str2
        print '###---------------####'
        
        
        for each in str1:
            original_str1 = original_str1.replace(each,'',1)
        for each in str2:
            original_str2 = original_str2.replace(each,'',1)
        all_replaced = original_str1 + original_str2
        print 'letters replaed: ' + str(all_replaced)
        summed_value = 0
        for each in all_replaced:
            summed_value = summed_value + ord(each)
        
        
        
        return str(counter) + ' moves minimum to make strings alike' + ' , ord sum: ' + str(summed_value)
    
    else:
        
        'RECURSION'
        
        
        return compare_two_strings(str1,str2,counter)
    
print compare_two_strings(str1,str2,0)    
