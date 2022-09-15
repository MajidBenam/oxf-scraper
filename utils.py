from lxml import etree, html
from bs4 import BeautifulSoup
import requests
import re
import bs4
import json
import time


from oxf_vars import *

source_url = 'https://www.oxfordlearnersdictionaries.com/definition/english/'

# cool trick
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
}

# 
#my_list = ["cushion", "maroon", "wanderer"]
#source = requests.get(source_url, headers=headers).text
# the def_counter problem is solved. The other problem is with so many try and except blocks
# I will rewrite everything with simple if and if else and it will be good.


def put_one_word_in(word, main_defs, words_dic):
    entry_dic = {}
    for index, item in enumerate(main_defs):
        inner_dic = {}
        for i in range(len(item)):
            try:
                a_def = item[i].text
            except:
                a_def = "NO_DEFINITION"
            good_key_for_def = "DEF_" + str(i+1)
            inner_dic[good_key_for_def] = a_def
        entry_dic[index] = inner_dic
    words_dic[word] = entry_dic


def test_func(my_list):
    words_dic = {}
    for word in my_list:
        def_counter = 1
        main_defs_for_all_in_one_word = []
        for i in [1,2,3,4]:
            print(word, str(i),  end=",")
            my_word_url = source_url + word + "_" + str(i)
            source = requests.get(my_word_url, headers=headers)
            soup = BeautifulSoup(source.content.decode('utf-8'), 'lxml')
            main_defs_for_one = soup.find_all('span', class_ = 'def')
            if main_defs_for_one:
                main_defs_for_all_in_one_word.append(main_defs_for_one)
            else:
                #print("Itseems there were no definitions for: ", my_word_url)
                continue
                #main_defs_for_all_in_one_word.append("NO_DEFINITION")
        put_one_word_in(word, main_defs_for_all_in_one_word, words_dic)
    return words_dic

def test_func_smaller_soup(my_list):
    words_dic = {}
    for word in my_list:
        time.sleep(2)
        inner_dic = {}
        for i in [1,2,3,4,5,6]:
            print(word, str(i), end=", ")
            my_word_url = source_url + word + "_" + str(i)
            source = requests.get(my_word_url, headers=headers, verify=False)
            # the big soup (not so useful)
            soup = BeautifulSoup(source.content.decode('utf-8'), 'lxml')
            # my smaller soups which will have all we need
            my_sngs = soup.find_all('li', {'id':re.compile(word + r'_sng_\d{1,2}')})
            if my_sngs:
                #my_sngs_list.append(my_sngs)
                sng_dic = {}
                # go loop through all the smaller soups
                for small_soup_index, small_soup in enumerate(my_sngs):
                    # REMEMBER: we have an i (the numbber on top)
                    # and a small_soup_index which is the inner one.
                    # get the definition

                    # details_dic gets populated gradually in this loop
                    details_dic = {}

                    my_def_inside = small_soup.find_all('span', class_ = 'def')
                    if my_def_inside:
                        for def_index, my_def in enumerate(my_def_inside):
                            def_key = "DEF_" + str(def_index)
                            details_dic[def_key] = my_def.text
                    else:
                        def_key = "DEF_" + str(small_soup_index)
                        details_dic[def_key] = "NO_DEFINITIONS"
                        #print("It seems there were no definitions for: ", my_word_url)

                    # get the examples
                    main_examples = small_soup.find_all('span', class_ = 'x')
                    if main_examples:
                        for example_index, my_example in enumerate(main_examples):
                            example_key = "EX_" + str(example_index)
                            details_dic[example_key] = my_example.text
                    else:
                        example_key = "EX_" + str(small_soup_index)
                        details_dic[example_key] = "NO_EXAMPLES"
                        #print("It seems there were no EXAMPLES for: ", my_word_url)

                    # get the phonetics
                    my_american_pros = soup.find('div', class_="phons_n_am")
                    my_american_pro = my_american_pros.find_all('span', class_ = 'phon')
                    if my_american_pro:
                        details_dic["PHON"] = my_american_pro[0].text
                    else:
                        details_dic["PHON"] = "NO_PHONS"
                        #print("It seems there are no Phonetics for: ", my_word_url)

                    # get the part of speech (from the main soup)
                    my_pos = soup.find('span', class_ = 'pos')
                    if my_pos:
                        details_dic["POS"] = my_pos.text
                    else:
                        details_dic["POS"] = "NO_POS"
                        #print("It seems there are no POS for: ", my_word_url)

                    sng_dic[small_soup_index] = details_dic
                    #print(my_def_inside)
                inner_dic[i] = sng_dic
            else:
                #print("NO_SNG: ", i)
                break
        words_dic[word] = inner_dic
    with open("my_json_file_of_oxford_test_dic.json", "w") as outfile:
       json.dump(words_dic, outfile)
    return words_dic


#             main_defs_for_one = soup.find_all('span', class_ = 'def')
#             if main_defs_for_one:
#                 main_defs_for_all_in_one_word.append(main_defs_for_one)
#             else:
#                 print("Itseems there were no definitions for: ", my_word_url)
#                 continue
#                 #main_defs_for_all_in_one_word.append("NO_DEFINITION")
#         put_one_word_in(word, main_defs_for_all_in_one_word, words_dic)
#     return words_dic

# def sng_situation_clearer(my_list):
#     words_dic = {}
#     for word in my_list:
#         main_defs_for_all_in_one_word = []
#         for i in [1,2,3]:
#             print("Going for word: ", word, str(i))
#             my_word_url = source_url + word + "_" + str(i)
#             source = requests.get(my_word_url, headers=headers)
#             soup = BeautifulSoup(source.content.decode('utf-8'), 'lxml')
#             my_sngs = soup.find_all('li', {'id':re.compile(word + r'_sng_\d{1,2}')})
#             if my_sngs:
#                 #my_sngs_list.append(my_sngs)
#                 for small_soup in my_sngs:
#                     my_def_inside = small_soup.find_all('span', class_ = 'def')
#                     if my_def_inside:
#                         main_defs_for_all_in_one_word.append(my_def_inside)
#                     else:
#                         print("Itseems there were no definitions for: ", my_word_url)
#                         continue
#                     print(my_def_inside)
#             else:
#                 continue
#         put_one_word_in(word, main_defs_for_all_in_one_word, words_dic)
#     return words_dic




        # my_sng_situations = soup.find_all('li', {'id':re.compile(word + r'_sng_\d{1,2}')})
        # #my_sng_situations = soup.find_all('li', {'id':re.compile(word + r'_sng_\d{1,2}')})
        # if my_sng_situations:
        #     print('fffffffff:', len(my_sng_situations))
        #     a_potential_start_def_counter = my_sng_situations[0]["id"].split("_")[-1]
        #     print("WORD: ", my_sng_situations[0]["id"])
        #     def_counter = a_potential_start_def_counter
        # else:
        #     print("riddddiiiiiiiiiiiiii")
        #     pass
        
        # # parts of speech
        # try:
        #     my_pos = soup.find('span', class_ = 'pos')
        #     my_dic_for_this_word["pos"] = my_pos.text
        # except:
        #     my_dic_for_this_word["pos"] = "NoPOSFound"

        # # phonetics
        # try:
        #     my_american_pros = soup.find('div', class_="phons_n_am")
        #     my_american_pro = my_american_pros.find_all('span', class_ = 'phon')
        #     my_dic_for_this_word["phon"] = my_american_pro[0].text
        # except:
        #     my_dic_for_this_word["phon"] = "NoProFound"
            
        # # ol with a class of sense_single or senses_multiple
        # my_multiple_defs = soup.find('ol', class_="senses_multiple")
        # my_single_def = soup.find('ol', class_="sense_single")
        # if my_multiple_defs:
        #     for index, my_def in enumerate(main_defs):
        #         list_item_id = word + "_sng_" + str(def_counter)
        #         try:
        #             my_smaller_soup_multi = my_multiple_defs.find(id=list_item_id)
        #             my_dic_for_this_word["def_" + str(index+1)] = my_def.text
        #             def_counter = def_counter + 1
        #         except:
        #             pass
        #             print("kkkk: ", list_item_id, my_dic_for_this_word["pos"])
        #             #continue
        #         try:
        #             #print("Haloooooo: ", list_item_id)
        #             my_examples = my_smaller_soup_multi.find_all('span', class_ = 'x')
        #             #print(my_smaller_soup_multi)
        #             my_dic_for_this_word["example_set_" + str(index+1)] = [my_exm.text for my_exm in my_examples]
        #             print("examples Collected for: ", word, my_dic_for_this_word["pos"])
        #         except:
        #             my_dic_for_this_word["example_set_" + str(index+1)] = "NoExamples"
        # else:
        #     my_single_def = soup.find('ol', class_="sense_single")
        #     list_item_id = word + "_sng_" + str(def_counter)
        #     my_smaller_soup = my_single_def.find(id=list_item_id)
        #     # the only def:
        #     #print(my_smaller_soup)
        #     try:
        #         main_def = my_smaller_soup.find('span', class_ = 'def')
        #         my_dic_for_this_word["def_1"] = main_def.text
        #         def_counter = def_counter + 1
        #     except:
        #         continue
        #     # the only set of examples:
        #     try:
        #         main_examples = my_smaller_soup.find_all('span', class_ = 'x')
        #         #print(type(my_smaller_soup))
        #         my_dic_for_this_word["example_set_1"] = [my_ex.text for my_ex in main_examples]
        #     except:
        #         my_dic_for_this_word["example_set_1"] = "NoExamples"
        # #else:
        # #    print("NoGOOD")
        #     #print(my_smaller_soup)
        # my_words_list_of_dics.append(my_dic_for_this_word)
        # print("SUCCESS: ", word, my_dic_for_this_word["pos"])
        
    #with open("my_json_file_of_oxford_test.json", "w") as outfile:
    #    json.dump(my_words_list_of_dics, outfile)