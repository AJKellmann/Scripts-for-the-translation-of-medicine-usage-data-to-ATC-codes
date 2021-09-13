# -*- coding: cp1252 -*-
__author__ = "alexander kellmann"
__date__ = "26/10/2020"

import pandas as pd
import csv
import sys

#Description:
#This file is supposed to match the SORTA results with the related ATC codes.
#Therefore it uses the SORTA results and the file rainbowtable_all.tsv.
#rainbowtable_all.tsv contains the relationship between the URIs of the ontology used in SORTA to the ATC codes
#There are two ways how to represent multiple ATC codes per drug:
#Each ATC code in a separate line, duplicating the rest of the line for multiple ATC codes (long format)
#Or all ATC codes in the same line with a separator.
#This file generates the long format.


#source for the tidy split function: https://stackoverflow.com/questions/12680754/split-explode-pandas-dataframe-string-entry-to-separate-rows/39946744
def tidy_split(df, column, sep='|', keep=False):
    """
    Split the values of a column and expand so the new DataFrame has one split
    value per row. Filters rows where the column is missing.

    Params
    ------
    df : pandas.DataFrame
        dataframe with the column to split and expand
    column : str
        the column to split and expand
    sep : str
        the string used to split the column's values
    keep : bool
        whether to retain the presplit value as it's own row

    Returns
    -------
    pandas.DataFrame
        Returns a dataframe with the same columns as `df`.
    """
    indexes = list()
    new_values = list()
    df = df.dropna(subset=[column])
    for i, presplit in enumerate(df[column].astype(str)):
        values = presplit.split(sep)
        if keep and len(values) > 1:
            indexes.append(i)
            new_values.append(presplit)
        for value in values:
            indexes.append(i)
            new_values.append(value)
    new_df = df.iloc[indexes, :].copy()
    new_df[column] = new_values
    return new_df





#default:
file=sys.argv[1]

if len(sys.argv)>1:
    file = sys.argv[1]

    #Read the SORTA output
    df = pd.read_csv(file, usecols=['Name', 'Synonym', 'ontologyTermName', 'ontologyTermIRI', 'score','review','validated'], header=0, sep=";")

    #Read the file "rainbowtable_all_long". It contains the link between then ATC codes and the selfmade URIs for the drugs.
    rainbowtable = pd.read_csv('rainbowtable_all.tsv', usecols=['ontologyTermIRI', 'Atccode'], names=['ontologyTermIRI', 'Atccode'], sep="\t")

    #Group all the ATC codes of the rainbowtable to their URI
    rainbowtable=rainbowtable.groupby('ontologyTermIRI')['Atccode'].apply(', '.join).reset_index(name='Atccode')
    #print(rainbowtable)
    #Look up all the ATC codes for the output from SORTA
    final_df = pd.merge(df, rainbowtable[['ontologyTermIRI',
                                    'Atccode']], left_on = ['ontologyTermIRI'], right_on = ['ontologyTermIRI'], how = 'left', validate = "m:m")

    final_df['Atccode']=final_df['Atccode'].apply(lambda x: ', '.join(set([y.strip() for y in str(x).split(',')])))

    #Write the ATC codes in long format
    final_df=tidy_split(df=final_df, column='Atccode', sep=', ')

    #Grouping duplicate lines that may only differ in the Name column.
    final_df = final_df.groupby(['Synonym', 'ontologyTermName', 'ontologyTermIRI', 'score','validated','review','Atccode'])['Name'].apply(', '.join).reset_index(name='Name')

    #Order the columns
    final_df = final_df[['Name','Synonym', 'ontologyTermName','score','validated','Atccode','review']] # 'ontologyTermIRI',

    #Order the results
    final_df=final_df.sort_values(by=["Synonym","review","Atccode","validated","score"],ascending=[False,True,True,False,True])

    #Write the output as tsv file:
    final_df.to_csv(str.replace(file, ".csv", "long_format.tsv"), sep= "\t", index = False, quoting=csv.QUOTE_ALL )

else:
    print("please specify a file")
