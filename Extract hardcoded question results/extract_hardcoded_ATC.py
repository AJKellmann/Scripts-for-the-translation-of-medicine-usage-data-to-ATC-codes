# -*- coding: cp1252 -*-
__author__ = "alexander kellmann"
__license__ = "Apache 2.0"
__date__ = "14/04/2020"

# Description:
#
# This program reads the results of the Lifelines Covid Questionnaires. 
# It extracts the results of the multiple choice questions.
#
# Depending on which options are chosen, the output file will save a file containing a tab separated file ("Medication_use_multiplechoice.tsv")
# containing the Participants ID ("PSEUDOIDEXT") and the ATC code(s) of the selected drugs. 
#
# The relation between the answers and their ATC codes is stored in the "file hardcoded_ATC_questions_week1-6.tsv"
#
# The results of the Covid questionnaires are in "../../data/raw/covid_questionnaires/week1/covid19-week1-1.dat"
# this can be changed with the option -d ("--datasources") to specify another path.
# 


import csv
import codecs
from optparse import OptionParser

def extractAnswer(name, participants_answers, atc_code):
    drugs = []  #Empty arry
    column = 0  #Column of the identifier
    for question in range(0, len(participants_answers[0])):                         # check each column
        if participants_answers[0][question] == name:                               # if the column with the answer to the identifier of the question is found
            #print("found: " + participants_answers[0][question])
            column+=1
            for participant in range(1, len(participants_answers)):                 # check each participant (each row), skipping the headers
                if (participants_answers[participant][question] == "1"):            # the answer is 1 in case the participani takes the drug
                    #print(participants_answers[participant][question] +" "+ participants_answers[0][question])
                    drugs.append([participants_answers[participant][0], atc_code])  # in this case we store the PseudoID and the atc code in the drug dictionary
    if column == 0:                                                                 # if the identifier hasn't been found at all
        print(name + " not found")                                                  # then this identifier was probably wrong - therefore inform the user
    return(drugs)                                                                   # return the dictionary




class Extractor:
    def __init__(self):
        # Open file
        parser = OptionParser()
        parser.add_option("-d", "--datasources", help="use the parameter -d to specify the datasource file")
        (options, args) = parser.parse_args()

       #In case no datasource is given the first questionnaire is evaluated instead.
        defaultPath = "../../data/raw/covid_questionnaires/week1/covid19-week1-1.dat"
        path = defaultPath

        if options.datasources:
            path = options.datasources
#            print("loading "+path)
        # Open file
        with codecs.open(path, 'r', encoding="iso-8859-1", errors='ignore') as f:
            contents = f.readlines()
        f.close

        # Splitting the file into columns:
        for i in range(len(contents)):
            contents[i] = contents[i].split("\t")

        # The Column names are hardcoded per question. Since the drug is part of the question, the ATC code is also known.
        with codecs.open("./hardcoded_ATC_questions_week1-6.tsv", 'r', encoding="iso-8859-1", errors='ignore') as f:
            contents2 = f.readlines()
        f.close

        # Splitting the file:
        for i in range(len(contents2)):
            contents2[i] = contents2[i].strip("\n").split("\t")


        # Creating a table for the results
        results=[["PSEUDOIDEXT","ATC"]]
        for i in range(len(contents2)): #For each hardcoded drug get PSEUDOIDEXT and ATC code 
            results+=(extractAnswer(contents2[i][0], contents, contents2[i][1]))

        # Write the output file:
        with open("./Medication_use_multiplechoice.tsv", "w") as csvfile:
            writer = csv.writer(csvfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerows(results)


if __name__ == '__main__':
    Extractor()

