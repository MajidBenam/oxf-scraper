from lxml import etree, html
from bs4 import BeautifulSoup
import requests
import re
import bs4
import json
import time
import csv


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

def test_func_smaller_soup(my_list_of_words, my_jsonfile):
    words_dic = {}
    for word in my_list_of_words:
        time.sleep(2)
        inner_dic = {}
        for i in [1,2,3,4,5,6]:
            print(word, str(i))
            my_word_url = source_url + word + "_" + str(i)
            source = requests.get(my_word_url, headers=headers, verify=False)
            # the big soup (not so useful)
            soup = BeautifulSoup(source.content.decode('utf-8'), 'lxml')
            # my smaller soups which will have all we need
            my_sngs = soup.find_all('li', {'id':re.compile(word + r'_sng_\d{1,2}')})
            if my_sngs:
                #my_sngs_list.append(my_sngs)
                sng_dic = {}
                all_cf_texts = []
                # go loop through all the smaller soups
                for small_soup_index, small_soup in enumerate(my_sngs):
                    # REMEMBER: we have an i (the numbber on top)
                    # and a small_soup_index which is the inner one.
                    # get the definition

                    # details_dic gets populated gradually in this loop
                    details_dic = {}

                    # my_def_inside = small_soup.find_all('span', class_ = 'def')
                    # if my_def_inside:
                    #     for def_index, my_def in enumerate(my_def_inside):
                    #         def_key = "DEF_" + str(def_index)
                    #         details_dic[def_key] = my_def.text
                    # else:
                    #     def_key = "DEF_" + str(small_soup_index)
                    #     details_dic[def_key] = "NO_DEFINITIONS"
                    #     #print("It seems there were no definitions for: ", my_word_url)


                    # get the FULL examples
                    group_examples = small_soup.find_all('ul', class_ = 'examples')
                    if group_examples:
                        for example_index, my_example in enumerate(group_examples):
                            #print(my_example)
                            #print(type(my_example))
                            #print(len(my_example))
                            for ex_index, inner_ex in enumerate(my_example):
                                main_example = inner_ex.find('span', class_ = 'x')
                                main_example_cf = inner_ex.find('span', class_ = 'cf')
                                
                                if main_example_cf and main_example:
                                    to_be_bolded = "(" +main_example_cf.text + ") " 
                                    to_be_bolded = "<b>" + to_be_bolded + "</b>"
                                    full_example_str = to_be_bolded + main_example.text 
                                    all_cf_texts.append(main_example_cf.text)
                                elif main_example:
                                    full_example_str =  main_example.text 
                                else:
                                    continue
                                    #full_example_str = "NO_EXAMPLES"
                                example_key = "EX_" + str(ex_index)
                                details_dic[example_key] = full_example_str
                                #print(example_key, ": ", details_dic[example_key])
                                #print(full_example_str)
                                #print("..................")
                            # main_examples = small_soup.find_all('span', class_ = 'x')
                            # main_examples_start = small_soup.find_all('span', class_ = 'cf')
                            # for example_index, my_example in enumerate(main_examples):
                            #     example_key = "EX_" + str(example_index)
                            #     details_dic[example_key] = my_example.text
                            #     print(my_example.text)
                    else:
                        example_key = "EX_" + str(ex_index)
                        details_dic[example_key] = "NO_EXAMPLES"
                        #print(example_key, ": ", details_dic[example_key])
                        #print("It seems there were no EXAMPLES for: ", my_word_url)

                    # definitions plus
                    my_def_inside = small_soup.find('span', class_ = 'def')
                    my_def_inside_cf = small_soup.find('span', class_ = 'cf')
                    def_key = "DEF_0"# + str(small_soup_index)

                    if my_def_inside_cf and my_def_inside_cf.text.strip() not in all_cf_texts:
                        to_be_bolded = "(" +my_def_inside_cf.text + ") "
                        to_be_bolded = "<b>" + to_be_bolded + "</b>"
                        full_def_str = to_be_bolded + my_def_inside.text 
                        details_dic[def_key] = full_def_str
                        #print(def_key, ": ", full_def_str)
                    elif my_def_inside_cf and my_def_inside_cf.text.strip() in all_cf_texts:
                        full_def_str = my_def_inside.text 
                        details_dic[def_key] = full_def_str
                        #print(def_key, ": ", full_def_str)
                    elif my_def_inside:
                        full_def_str = my_def_inside.text
                        details_dic[def_key] = full_def_str
                        #print(def_key, ": ", full_def_str)
                        #for def_index, my_def in enumerate(my_def_inside):
                            #print(my_def)
                            #print(type(my_def))
                            #print(len(my_def))
                            #main_def = my_def.find('span', class_ = 'def')
                            #print(main_def.text)
                            #def_key = "DEF_" + str(def_index)
                            # details_dic[def_key] = my_def.text
                    else:
                        details_dic[def_key] = "NO_DEFINITIONS"
                        #full_def_str =  my_def_inside.text
                        #print(def_key, ": ", full_def_str)
                    #print(f"_____{word}___{i}____")
                    #print(full_def_str)
                    #print("EXAMPLES: ")
                    # get the examples
                    # main_examples = small_soup.find_all('span', class_ = 'x')
                    # if main_examples:
                    #     for example_index, my_example in enumerate(main_examples):
                    #         example_key = "EX_" + str(example_index)
                    #         details_dic[example_key] = my_example.text
                    #         #print(my_example)
                    # else:
                    #     example_key = "EX_" + str(small_soup_index)
                    #     details_dic[example_key] = "NO_EXAMPLES"
                    #     #print("It seems there were no EXAMPLES for: ", my_word_url)



                    # get the phonetics
                    try:
                        my_american_pros = soup.find('div', class_="phons_n_am")
                        my_american_pro = my_american_pros.find_all('span', class_ = 'phon')
                    except:
                        details_dic["PHON"] = "NO_PHONS"

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
    with open(my_jsonfile, "w") as outfile:
       json.dump(words_dic, outfile)
    return words_dic


def longman_to_list(longman_text):
    final_list = []
    with open(longman_text) as textfile:
        lines = textfile.readlines()
        lines = [line.rstrip() for line in lines]
        for index, line in enumerate(lines):
            #print(index)
            if " ," in line:
                separated_words_pos_list = line.split(" ,")
            else:
                separated_words_pos_list = [line, ""]

            final_list.append(separated_words_pos_list)
    return final_list


def AnkiDroid_deck_creator(my_json_file):
    with open(my_json_file, 'r') as f:
        my_data = json.load(f)

    list_of_ank_cards = []
    for word, details in my_data.items():
        for numb, numb_details in details.items():
            for shomare, shomare_details in numb_details.items():
                print(shomare_details)
                definition = shomare_details.get("DEF_0", "No_DEFINITION")
                MY_POS = shomare_details.get("POS", "No_POS")
                PHON = shomare_details.get("PHON", "PHON")

                examples = []
                for my_key in shomare_details.keys():
                    if "EX" in my_key:
                        examples.append(shomare_details[my_key])
                examples_str = "<br>".join(examples)
                
                anki_string = str(word) + "<br>" + str(MY_POS) + "<br>" + str(PHON) +  "|" + definition  + "<br><h3>Examples:</h3><br>" + examples_str + "\n"
                list_of_ank_cards.append(anki_string)

    list_of_cards_str = "".join(list_of_ank_cards)

    with open("my_anki_csv_new.csv", "w") as f:
        f.write(list_of_cards_str)

    return list_of_ank_cards


def AnkiDroid_deck_creator_with_csv(my_json_file, my_csv_file):
    with open(my_json_file, 'r') as f:
        my_data = json.load(f)

    list_of_ank_cards = []
    for word, details in my_data.items():
        for numb, numb_details in details.items():
            for shomare, shomare_details in numb_details.items():
                print(numb, shomare, word)
                definition = shomare_details.get("DEF_0", "No_DEFINITION")
                MY_POS = shomare_details.get("POS", "No_POS")
                PHON = shomare_details.get("PHON", "PHON")

                examples = []
                for my_key in shomare_details.keys():
                    if "EX" in my_key:
                        examples.append("- " + shomare_details[my_key])
                examples_str = "<br>".join(examples)
                number_good = str(int(shomare)+1)
                number_span = f"<span style='color:cornsilk; background-color:darkcyan; border-radius:5px;'>&nbsp;{number_good}&nbsp;</span>"
                anki_string_word = number_span + " " + "<b style='color:darkslategray;'>" + str(word) + "</b><br>" + str(MY_POS) + "<br>" + str(PHON)
                anki_def =  definition  + "<br><b style='color:darkcyan;'>Examples:</b><br>"+ examples_str
                list_of_ank_cards.append([anki_string_word, anki_def])

    with open(my_csv_file, "w", newline='') as file:
        writer = csv.writer(file, delimiter="|")
        for card in list_of_ank_cards:
            writer.writerow(card)

    return list_of_ank_cards

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
