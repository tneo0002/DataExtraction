#!/usr/bin/env python
# coding: utf-8

# In[ ]:


class DialogueExtractor:
    
    def __init__(self, intext = 'input_script.txt', outtext = '32726279_clean_dialogue.txt'):
        self._intext = intext
        self._outtext = outtext
    
    def extract_dialogue(self, save = True):
        import re
        
        self._save = save
        with open(self._intext, 'r', encoding = 'utf-8') as f:
            text = f.readlines()
            text = [string.strip() for string in text if string]
        # Going through the extract lines of text one by one and identifying the start position
        # of dialogue & removing any preceeding lines.
        position = -1
        new_text = []
        for i in range(len(text)):
            if text[i].startswith('[Scene:'):
                position = i
                break
        # Removing lines before the first scene description.
        for j in range(i, len(text)):
            new_text.append(text[j])
        # Removing parenthesised contents
        debraced_text = []
        for string in new_text:
            debraced_string = re.sub(r'\(.*?\) *', '', string)               
            debraced_string2 = re.sub(r'\[.*?\] *', '', debraced_string)
            if debraced_string2:
                debraced_text.append(debraced_string2.strip())
        cleaned_dialogue = []
        formatted_lines = []
        # Going through the string one by one and formatting the string such that there is only
        # one whitespace after every colon.
        for string in debraced_text:
            if re.findall(': *', string):
                formatted_line = re.sub(': *', ': ', string)
                formatted_lines.append(formatted_line)
            else:
                formatted_lines.append(string)
        # Going through the string one by one and extracting only dialogue lines.
        for string in formatted_lines:
            if re.findall(':', string):
                cleaned_dialogue.append(string)
        output = []
        # Going through the string one by one and creating a list of tuples: 1st item of tuples
        # is character name, 2nd item is cleaned dialogue.
        for string in cleaned_dialogue:
            output.append(tuple(string.split(': ')))
        # Creating and writing the list to text file or return output depending of the argument.
        if self._save:
            with open (self._outtext, 'w', encoding = 'utf-8') as f:
                f.write(repr(output))
        else:
            return output
    
    def extract_role(self):
        role_list = []
        unique_roles = []
        # Going through the item of the list one by one and extracting roles into a list.
        for i in self.extract_dialogue(False):
            role_list.append(i[0])
        for j in role_list:
            if j not in unique_roles:
                unique_roles.append(j)
        return unique_roles
    
    def separate_dialogue(self):
        # Looping through the characters and separating the corresponding dialogues for each
        # character and writing them to file.
        for role in self.extract_role():
            with open ('32726279_' + role.lower() + '.txt', 'w', encoding = 'utf-8') as f:
                for item in self.extract_dialogue(False):
                    if role == item[0]:
                        f.write(item[1] + '\n')

    def rolesorted_dialogue(self, outcsv = '32726279_data.csv'):
        import pandas as pd
        
        self._outcsv = outcsv
        # Creating and saving an empty DF as a container.
        df_linefreq = pd.DataFrame(columns = ["role", "word", "freq"])
        df_linefreq.to_csv(self._outcsv, index = False)
        # Looping through the characters.
        for role in self.extract_role():
            sorted_dialogue = []
            sorted_words = []
            dic_dialogue = {}
            dic_uniqwords = {}
            dic_linefreq = {}
            # Looping through the list of dialogues and creating a list of unique words for a
            # particular character and a list of dialogues spoken by the character.
            for item in self.extract_dialogue(False):
                if role == item[0]:
                    sorted_words.extend(item[1].lower().split())          
                    sorted_dialogue.append(item[1].lower().split())
                    dic_uniqwords[role] = list(set(sorted_words))
                    dic_dialogue[role] = sorted_dialogue
            # Counting the line frequency of unique words spoken by the a role who has spoken
            # > 100 unique words and creating a dictionary to store the information.
            if len(dic_uniqwords[role]) > 100:
                for uniqword in dic_uniqwords[role]:
                    uniqword_count = 0
                    for dialogue in dic_dialogue[role]:
                        if uniqword in dialogue:
                            uniqword_count += 1
                            dic_linefreq[uniqword] = uniqword_count
                            dic_linefreq = dict(sorted(dic_linefreq.items(), key = lambda x: x[0]))
                # Finding 5 words with the highest line frequencies in the dictionary and creating
                # a DF.
                from collections import Counter                
                dic_linefreq = dict(Counter(dic_linefreq).most_common(5))
                df_role_linefreq = pd.DataFrame({                             
                                                "role" : [role.lower()] * len(dic_linefreq),
                                                "word" : dic_linefreq.keys(),
                                                "freq" : dic_linefreq.values()
                                                })
                # Appending the DF created for a role to csv file.
                df_linefreq = pd.read_csv(self._outcsv)
                df_linefreq.append(df_role_linefreq).to_csv(self._outcsv, index = False)


class Plot:
    
    def __init__(self):
        pass

    def get_data(self, incsv, role = [], word = [], linefreq = []):
        import os
        import pandas as pd
        
        self._incsv = incsv
        self._role = role
        # Retrieving data from csv file to create a DF and convert the DF to a list.
        df_csv = pd.read_csv(self._incsv)
        data_list = df_csv.values.tolist()
        # Spliting the 1st, 2nd, and 3rd item in the elements of the list
        # into 3 lists and return the created 3 lists.
        for index in range(0, len(data_list), 5):
            self._role.append(data_list[index][0].capitalize())
        self._word = word
        self._linefreq = linefreq
        for item in data_list:
            self._word.append(item[1])
            self._linefreq.append(item[2])
        os.remove(self._incsv)
        return self._role, self._word, self._linefreq
    
    def plot_fig(self, incsv):
        import matplotlib.pyplot as plt
        import numpy as np
        
        self._incsv = incsv
        self.get_data(self._incsv)
        
        yinterval = np.arange(0, 21, 4)
        xlabel = 'Top 5 Words Spoken'
        ylabel = 'Line Frequency'
        width = 0.8
        
        plt.figure(figsize = (15, 10))
        plt.suptitle('Five Most Frequent Words Spoken By Characters', fontsize = 20)
        
        plt.subplot(231)
        plt.title(self._role[0], fontsize = 15)
        plt.bar(self._word[0:5], self._linefreq[0:5], width, color = 'r')
        plt.xticks(fontsize = 10)
        plt.yticks(yinterval, fontsize = 10)
        plt.ylabel(ylabel, fontsize = 13)
        
        plt.subplot(232)
        plt.title(self._role[1], fontsize = 15)
        plt.bar(self._word[5:10], self._linefreq[5:10], width, color = 'b')
        plt.xticks(fontsize = 10)
        plt.yticks(yinterval, fontsize = 10)
                
        plt.subplot(233)
        plt.title(self._role[2], fontsize = 15)
        plt.bar(self._word[10:15], self._linefreq[10:15], width, color = 'g')
        plt.xticks(fontsize = 10)
        plt.yticks(yinterval, fontsize = 10)
                
        plt.subplot(234)
        plt.title(self._role[3], fontsize = 15)
        plt.bar(self._word[15:20], self._linefreq[15:20], width, color = 'blueviolet')
        plt.xticks(fontsize = 10)
        plt.yticks(yinterval, fontsize = 10)
        plt.xlabel(xlabel, fontsize = 13)
        plt.ylabel(ylabel, fontsize = 13)
        
        plt.subplot(235)
        plt.title(self._role[4], fontsize = 15)
        plt.bar(self._word[20:25], self._linefreq[20:25], width, color = 'turquoise')
        plt.xticks(fontsize = 10)
        plt.yticks(yinterval, fontsize = 10)
        plt.xlabel(xlabel, fontsize = 13)
        
        plt.subplot(236)
        plt.title(self._role[5], fontsize = 15)
        plt.bar(self._word[25:30], self._linefreq[25:30], width, color = 'gold')
        plt.xticks(fontsize = 10)
        plt.yticks(yinterval, fontsize = 10)
        plt.xlabel(xlabel, fontsize = 13)
        
        plt.show()


# In[ ]:


# Task 1: Extracting Dialogue
de = DialogueExtractor()
de.extract_dialogue()


# In[ ]:


# Task 2: Separating Dialogue
de = DialogueExtractor()
de.separate_dialogue()


# In[ ]:


# Task 3: Obtaining Top 5 Frequent Words For Each Role
de = DialogueExtractor()
de.rolesorted_dialogue()


# In[ ]:


# Task 4: Visualising The Findings From Task 3
de = DialogueExtractor()
de.rolesorted_dialogue('v(^-^)temp_source(^-^)v.csv')
p1 = Plot()
p1.plot_fig('v(^-^)temp_source(^-^)v.csv')


# In[ ]:


# In my opinion, presenting the data in 6 separate subplots of bar chart and having them arranged
# side by side is satisfactory for capturing the differences across the six characters (i.e.,  
# Ross, Chandler, Joey, Phoebe, Rachel, and Monica) not only in terms of line frequencies but
# also the exact top five words most spoken by each character.
# "i" is the only one word out of the top five words most spoken by all of the characters. 
# It was the most frequently repeated word by Ross, Chandler, and Joey and the second most 
# repeated word by Rachel and Monica.
# Four out of six characters frequently used "you" and "a", while three characters shared "of",
# "the", and "to" as their top five most spoken words.

