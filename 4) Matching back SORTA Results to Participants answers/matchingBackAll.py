# -*- coding: cp1252 -*-
__author__ = "alexander kellmann"
__license__ = "LGPL-3.0 License"
__date__ = "11/08/2020"

# Description:
# This program expects 3 parameters:
# 1) The path of the table with PSEUDOIDEXT and Drugname
# 2) The path of the table that contains the results from SORTA mapped to the ATC codes including a score
# 3) The path for the output

# Aim of this program is to match the ATC codes to the given answers for all the given answers


import pandas as pd
import csv
import sys
import numpy as np


#This program expects 3 parameters:
# 1) The path of the table with PSEUDOIDEXT and Drugname
# 2) The path of the table that contains the results from SORTA mapped to the ATC codes including a score
# 3) The path for the output

# Aim of this program is to match the ATC codes to the given answers for all the given answers

#default values
answers = "../../extractedColumns4_week1/COVID24A2TXT_column.csv"
atccodes = "./Lifelines_Covid_questionaire_week1_question_24A2_processed_wide_ATC_codes_incl_unfilteredlong_format.tsv"

#reading the values from the commandline
if len(sys.argv)>1:
    answers = sys.argv[1]
if len(sys.argv)>2:
    atccodes = sys.argv[2]

#Read the file with the ATC codes
#try:
df = pd.read_csv(atccodes, header=0, sep="\t") #read Name, ATC code and the score.
df.rename(columns={"Synonym":"Original"}, inplace=True)
df2= pd.read_csv(answers, header=0, sep="\t") #read the participantsID and the drug
#strip whitespaces
for col in df2.columns:
        if pd.api.types.is_string_dtype(df2[col]):
            df2[col] = df2[col].str.strip()
        df2 = df2.replace({"":np.nan})

#output the headers of the files
print(df.head())
print(df2.head())
#take the Table df2 and map the Atccode and the threshold to the drugname 
finaldf = pd.merge(df2, df, left_on=['Original'], right_on = ['Original'], how = 'left', validate="m:m")

#write the results down to a file
resultpath="result.tsv"
if len(sys.argv)>3:
    resultpath=sys.argv[3]
finaldf.to_csv(resultpath, sep="\t", index=False, quoting=csv.QUOTE_MINIMAL)
#except:
#    print("Something went wrong")
