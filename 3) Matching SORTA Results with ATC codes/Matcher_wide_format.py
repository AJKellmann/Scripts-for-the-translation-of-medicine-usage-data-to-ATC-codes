# -*- coding: cp1252 -*-
__author__ = "alexander kellmann"
__date__ = "04/11/2020"

import pandas as pd
import csv
import sys
import string

#Description:
#This file is supposed to match the SORTA results with the related ATC codes.
#Therefore it uses the SORTA results and the file rainbowtable_all.tsv.
#rainbowtable_all.tsv contains the relationship between the URIs of the ontology used in SORTA to the ATC codes
#There are two ways how to represent multiple ATC codes per drug:
#Each ATC code in a separate line, duplicating the rest of the line for multiple ATC codes (long format)
#Or all ATC codes in the same line with a separator.
#This file generates the wide format. The wide format can be used for the manual curation step in Excel.
#The intention was also to group the SORTA results by the "synonym" and list groups with terms flagged for review at the top.

#default:
file=sys.argv[1]

if len(sys.argv)>1:
    file = sys.argv[1]

    #Read the SORTA output
    df = pd.read_csv(file, usecols=['Name', 'Synonym', 'ontologyTermName', 'ontologyTermIRI', 'score','validated','review'], header=0, sep=";")

    #Read the file "rainbowtable_all_long". It contains the link between then ATC codes and the selfmade URIs for the drugs.
    rainbowtable = pd.read_csv('rainbowtable_all.tsv', usecols=['ontologyTermIRI', 'Atccode'], names=['ontologyTermIRI', 'Atccode'], sep="\t")

    #Group all the ATC codes of the rainbowtable to their URI
    rainbowtable=rainbowtable.groupby('ontologyTermIRI')['Atccode'].apply(', '.join).reset_index(name='Atccode')

    #Look up all the ATC codes for the output from SORTA
    final_df = pd.merge(df, rainbowtable[['ontologyTermIRI',
                                    'Atccode']], left_on = ['ontologyTermIRI'], right_on = ['ontologyTermIRI'], how = 'left', validate = "m:m")

    final_df['Atccode']=final_df['Atccode'].apply(lambda x: ', '.join(set([y.strip() for y in str(x).split(',')])))

    #Order the results
#    final_df=final_df.sort_values(by=["Synonym","review","Atccode","validated","score"],ascending=[False,True,True,False,True])

    final_df=final_df.sort_values(by=["review","Synonym","Atccode","validated","score"],ascending=[False,True,True,False,True])
    final_df=final_df.groupby('Synonym', sort=False).apply(lambda x: x.sort_values('review'))

    #Write the output to a tsv file:
    final_df.to_csv(str.replace(file, ".csv", "_wide_format.tsv"), sep= "\t", index = False, quoting=csv.QUOTE_ALL )
else:
    print("please specify a file")

