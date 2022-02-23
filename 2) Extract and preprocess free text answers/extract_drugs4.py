# -*- coding: cp1252 -*-
#This version uses pandas instead of arrays.
#It should be capable of reading 5 or 10 lines for question 24A10TXT without of manual adjustment of the code.
__author__ = "alexander kellmann"
__license__ = "LGPL-3.0 License"
__date__ = "15/05/2020"

# Description:
#
# This program reads the results of the Lifelines Covid Questionnaires. 
# It extracts the results of the free text questions.
#
# This program does not only extract the results, it also does some preproecssing.
# Preprocessing includes a number of steps:
# - a transformation of the text into lower case 
# - adding missing spaces after commas
# - removal/escaping of special and escape characters (tabs, quotes, brackets, semicolon, "--")
# - a removal of Dutch stop words by using the NLP-toolkit 
# - a removal of manufacturers names, descriptions and fill words (e.g., “elke dag”, “plus”) based on a list of terms
# - removal of dosage information, concentrations, volumes (by using regular expressions)
#   (Using regular expressions on free text may lead to unwanted changes !!!)
#
# - splitting the remaining text into words or known word groups (e.g., Vitamin + Space + 1 letter)
# - removal of words with less than 3 letters
# - stripping whitespaces at the beginning and end of an answer
# - replacing multiple whitespaces with a single whitespace
# - removal of empty values, either being empty or containing a code for being empty
#
# The results of the Covid questionnaires are in "../../data/raw/covid_questionnaires/week1/covid19-week1-1.dat"
# this can be changed with the option -d ("--datasources") to specify another path.
#
# The results of this programm are two files per question. (In total there are 8 free text questions (question 2-9) per week).
# The first file contains the participant's ID, a term ("Name") that was split apart from the rest of the answer and a slightly filtered version of the whole answer ("Synonym").
# The second file contains the same information beside that the participant's ID is removed.
# "Name" and "Synonym" are keywords in Molgenis SORTA.
#
# The second file is anonymized (pseudonomized) since it doesn't contain the participants ID anymore.
# It is supposed to be loaded into Molgenis SORTA to map the answers to ATC codes. 
# The first file is to map the results from SORTA back to the participants ID by using the slightly filtered answer as key.





import csv
import pandas as pd
import re
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk import word_tokenize
nltk.download('stopwords')
nltk.download('punkt')
dutch_stopwords = set(stopwords.words("dutch"))
manufacturers=[x.lower() for x in ['ACTAVIS', 'APO', 'APOTEX', 'AUR', 'AURO', 'BIPHA', 'BIPHARMA', 'CF', 'DCB ', 'DUMEX', 'FNA ', 'FOC', 'FRES', 'GL', 'HEXAL', 'HIKMA', 'IDYL', 'KABI', 'LEYDEN', 'MDQ', 'MICRON', 'MYL', 'MYLA', 'MYLAN', 'PCH', 'PFIZ', 'PHARBITA', 'PHB', 'RANB', 'RP', 'SAN', 'SANDOZ', 'SDZ', 'TEVA', 'VOGEL', 'WELEDA', 'lilly', 'janssen-cilag', 'ratiopharm','SADOZ', 'dandoz', 'sandox']]
#other terms consists out of fillwords - they should appear in the Original terms, but not as seperated ones
other_terms=[x.lower() for x in['ALP', 'BERNA', 'BIOTEST', 'BRIST', 'BROC', 'DEP', 'DRP', 'DU', 'EB', 'EBE', 'EU', 'FA', 'FAULD', 'FIS', 'FLACON', 'FLOS', 'FLX', 'FORTE', 'FRE', 'GF', 'HCL', 'HO', 'HOS', 'HOSP', 'HTP', 'HYDROFIELE', 'ICN', 'INTRAFLEX', 'JC', 'JJC', 'JUB', 'KAR', 'KARIB', 'KATW', 'KRI', 'KRIST', 'KTW', 'KW', 'KWIKPEN', 'LIC', 'MAYNE', 'MEDICINAAL', 'MINIPL', 'MP', 'normaal', 'NOVOL', 'NOVOLET', 'NX', 'OP', 'OPG', 'ora', 'OROS', 'PB', 'PENFILL', 'PHBT', 'PSI', 'RADIX', 'RET', 'RETARD', 'RIVM', 'SM', 'SUDCO', 'TRAM', 'TTS', 'WWSP ', 'conc', 'extract', 'geel', 'dis', 'plus', 'hci', 'hcl', 'tert', 'auto', 'combinatie', 'remmer', 'remmers', 'mono', 'neuro','sun','card','car','pro','hart','med','extra','sterk']]
words_to_exclude=[x.lower() for x in['teva', 'accord', 'focus', 'schildklier', 'pd', 'x', 'auro ', 'aurobindo', 'retard', 'foc', 'glenmark', 'glen', 'm/gr', 'glaucoom', 'zonodig', 'microgram', 'ochtend', 'medicijn', 'mcg', 'migraine ', 'profylaxe', 'tegen', 'jicht ', 'pharmathen', 'halve', 'opvliegers', 'allergie', 'pillen', 'van', 'ochtends', 'avonds', 'pompkracht', 'maart', 'mee', 'begonnen', 'hooikoorts', 'i.v.m.', 'eenogigheid', 'ziekte', 'van', 'crohn', 'voor', 'depressie', 'hoge', 'een', 'andere', 'medicatie', 'mijn', 'spiegel', 'was', 'te', 'laag', 'homeopatisch', 'ivm', 'gordelroos', 'om', 'op', 'houden', 'medicijnen', 'hartritme', 'geen', 'idee', 'milli', 'micro', 'gram/ml', 'slijmbeursontsteking', 'hartkloppingen', 'zwangerschap', 'gebruik', 'als', 'onderhoudsmedicatie', 'hoofdpijn', 'migraine', 'plassen', 'middelen', 'weet', 'niet', 'wekelijks', 'bloeddrukverlager', 'houden', 'jeukbestrijding', 'door', 'dermatoloog', 'aangeraden', 'ter', 'voorkoming', 'op', 'voorschrift', 'neuroloog', 'alternatief', 'voor', 'prostaat', 'gewrichten', 'bloeddrukpillen', 'onafhankelijk', 'het', 'preventief', 'heb', 'gehad', 'ritme', 'storing', 'kon', 'ik', 'invullen', 'onderstaande', 'vraag', 'pijnremmers','per', 'dag', 'mylan', 'bloeddruk', 'bloedvaten', 'aurobindo', 'ide','week','elk','nemen','ieder','di e', 'toe','rug','nodig','hom','uur','neus','parkinson','mood','naam','weet','t b v','via','huisarts']]


from optparse import OptionParser

def remove_duplicats_from_list(liste):
    return list( dict.fromkeys(liste) )

def splitItUp(df, name):
    df["Original"] = df[name]
    df[name]=df[name].apply(word_tokenize)
    df[name]=df[name].apply(lambda text: " ".join([x for x in text if x not in dutch_stopwords]))
    df[name]=df[name].apply(word_tokenize)
    df[name]=df[name].apply(lambda text: " ".join([x for x in text if x not in manufacturers]))
    df.columns=['PSEUDOIDEXT', name, "Original"]
    target_column=name
    separator=r"(?<!rode)(?<!multi )(?<!multi)(?<!vitamin)(?<!vitamine)(?!<vit)(?!<vit\.)(?<!tert-)(?<!tert)[ \\\/](?!aerosol)(?!applicatievl)(?!applicatievloeist)(?!applicatievlst)(?!applvlst)(?!blaassp)(?!blaasspoeling)(?!bruisgr)(?!bruisgran)(?!bruisgranulaat)(?!bruistab)(?!bruistablet)(?!capsule)(?!caps)(?!chew)(?!concentraat)(?!creme)(?!dispertabl)(?!disp)(?!dsp)(?!dragee)(?!drank)(?!druppels)(?!emulsie)(?!gel)(?!gorgeldrank)(?!granulaat)(?!huidspray)(?!implantaat)(?!implantatiestift)(?!inf)(?!infopl)(?!infusievloeistof)(?!infusion)(?!infuus)(?!infvls)(?!infvlst)(?!inhalatiepoeder)(?!inhalatievloeistof/gas)(?!inhalatievlst/gas)(?!inhalcaps)(?!inhpdr)(?!inj)(?!inj/infopl)(?!injectie)(?!injectie/infuus)(?!injectiepoeder)(?!injpdr)(?!injsusp)(?!injv)(?!injvls)(?!kauw-/dispertab)(?!kauwtab)(?!kauwtablet)(?!kauwtb)(?!klysma)(?!lotion)(?!mondpasta)(?!mondspoeling)(?!mondspray)(?!neusspray)(?!omh tabl)(?!omh)(?!oogdruppel)(?!ooginsert)(?!oogwassing)(?!oogzalf)(?!oordr)(?!oordrup)(?!oordrupp)(?!oordruppel)(?!oog druppels)(?!oordruppels)(?!opl)(?!OPLOS)(?!oplossing)(?!pasta)(?!pdr)(?!pleister)(?!poeder)(?!schudmixtuur)(?!SIROOP)(?!smeersel)(?!smelttablet)(?!SOLUTAB)(?!spoeling)(?!spray)(?!strooipoeder)(?!STROOP)(?!SUPP)(?!sus)(?!susp)(?!susp.)(?!suspensie)(?!tabl omh)(?!tab)(?!tablet)(?!tabletten)(?!tabl)(?!tandpasta)(?!tea)(?!tinctuur)(?!vaginaalcapsule)(?!vaginaalcreme)(?!vaginaaltablet)(?!vernevel)(?!vernevelvlst)(?!vlst)(?!Weefsellijm)(?!zalf)(?!zetpil)(?!zuigtablet)(?!OLEOGEL)"
    def splitListToRows(row,row_accumulator,target_column,separator):
        split_row = re.split(separator,row[target_column])
        for s in split_row:
            new_row = row.to_dict()
            new_row[target_column] = s
            row_accumulator.append(new_row)
    new_rows = []
    df.apply(splitListToRows,axis=1,args = (new_rows,target_column,separator))
    new_df = pd.DataFrame(new_rows)
    print(new_df.head())
    return new_df



class Extractor:
    def __init__(self):
        # Open file
        parser = OptionParser()
        parser.add_option("-d","--datasources",  help="load the datasource file")
        (options, args) = parser.parse_args()

        defaultPath = "../../data/raw/covid_questionnaires/week1/covid19-week1-1.dat"
        path = defaultPath


        if options.datasources:
            path=options.datasources
        print(path)
        #Open file
        df = pd.read_csv(path, sep="\t", encoding="iso-8859-1", dtype=np.dtype('str'))

        #Specify all the relevant columns that could potentially be in the file:
        #The ID is there:
        potential_columns = ['PSEUDOIDEXT']
        #Question 2-9 have 2 text fields
        for question in range(2, 10):
            potential_columns.append(str('COVID24A'+ str(question) +'TXT'))
            for line in range(1, 3):
                potential_columns.append(str('COVID24A'+ str(question) +'TXT' + str(line)))
        #Question 10 is special, it can have a variing amount of text fields
        for line in range(1, 11):
            potential_columns.append(str('COVID24A'+ str(10) +'TXT' + str(line)))
        potential_columns.append(str('COVID24A'+ str(10) +'TXT'))

        #Reading the answers
        df = pd.read_csv(path, sep="\t", encoding="iso-8859-1", dtype=np.dtype('str'))
        #Filtering the columns that exist out of the expected
        df_col = [col for col in df.columns if re.search('|'.join(potential_columns), col)]

        #Data cleaning
        words = words_to_exclude
        for x in range(0, len(words)):
            words[x] = re.escape(words[x].strip()) 
        #print(words)
        for col in df_col:
            #skip the PSEUDOIDEXT column
            if col in ['PSEUDOIDEXT']:
                continue

            #use lowercase for all the relevant columns
            df[col]= df[col].str.lower()

            #add a space after commas without of a space
            df[col] = df[col].str.replace(r',\w', ', ')

#           #remove special signs and escape characters)
            spec_chars = ['"',"'","`","\t","--"]
            for char in spec_chars:
                df[col] = df[col].str.replace(char, ' ')
            
            print("#remove things like volume or weight")
            df[col] = df[col].replace(to_replace ='(elke( +)?)?\d+((,\d*)|(\.\d*))?( *)?(m?\.?((gram)|(gr)|(g)|(l)))?\.?( *)?\/?( +)?(m?\.?((gram)|(gr)|(g)|(l)))?\.?( +)?(half(e)?)?(pch)?(pcn)?(ie)?(keer)?(kker)?(st)?(st\.)?((( +)?(per\W|x|\*))+)?( +)?((dag)(\w{0,2}))?(p\/d)?(p\/dag)?( +)?(daags)?(dgs)?(dg)?(smorgens)?(savonds)?(\d?( +)?dd( +)?\d?( +)?t?)?(dgs)?( +)?(week)?', value = '', regex = True)

            #replace semicoli with comma, since this is a key for SORTA
            df[col] = df[col].str.replace(';', ',' , regex = False)

            #remove entries with less than 3 letters
            df[col] = df[col].str.replace(r'^(\W*)?[a-zA-Z]{0,2}(\W*)?$', '')

            #remove kommas at the end of the line
            df[col] = df[col].str.replace("(,|( \.))\s*$", "")

            #Strip whitspaces at beginning and end
            df[col]= df[col].str.strip()
           
            #replace multiple Whitespaces
            df[col] = df[col].str.split().str.join(" ")

            #replace some regex symbols
            df[col] = df[col].str.replace("()", ' ', regex = False)
            df[col] = df[col].str.replace("( )", ' ', regex = False)
            df[col] = df[col].str.replace("( / )", ' ', regex = False)
            df[col] = df[col].str.replace("+", ' ', regex = False)
            df[col] = df[col].str.replace("i.v.m.", ' ', regex = False)

        #Concatenate the answers for each questions with and without the PSEUDOINDEX
        #Removing irrelevant lines and duplicate entries
        for question in range(2,11):
            print("Question:COVID24A"+str(question))
            #Get all the columns for this question
            filter_col = [col for col in df if col.startswith('COVID24A'+str(question)+"TXT")]

            #Create a new dataframe that consists out of 2 Columns: PSEUDOINDEX and the matching column for this question
            #It contains the answers of all Text field belonging to the actual question
            df_qn = pd.DataFrame()
            for n in range(0, len(filter_col)):
                df_tmp = df.loc[:,['PSEUDOIDEXT', filter_col[n]]]
                df_tmp.columns = ['PSEUDOIDEXT', 'COVID24A'+str(question)+"TXT"]
                df_qn = df_qn.append(df_tmp,  ignore_index=True)
            #for debugging purpose:
            #print(df_qn.head())

            # Removing irrelevant lines
            irrelevant_terms=["9999", "8888", " ", "", np.nan]
            for term in irrelevant_terms:
                indexNames = df_qn[df_qn['COVID24A'+ str(question)+ "TXT"] == term ].index
                df_qn.drop(indexNames, inplace=True)

            #Remove rows with empty values
            df_qn.dropna(how='any')

            #split the whole line into words and remove stopwords
            df_qn = splitItUp(df_qn, 'COVID24A'+ str(question)+ "TXT")

            if df_qn.shape[1]==0:
                print("skipping empty table")
                continue
#            print(df_qn.head())
#           Filter after splitting:

            #Strip whitspaces at beginning and end
            df_qn['COVID24A'+ str(question)+ "TXT"]= df_qn['COVID24A'+ str(question)+ "TXT"].str.strip()

            #remove words
            pat = r'\b(?:{})\b'.format('|'.join(words))
            df_qn['COVID24A'+str(question)+"TXT"] = df_qn['COVID24A'+str(question)+"TXT"].str.replace(pat, '')

            #remove words with less than 3 letters
            df_qn['COVID24A'+str(question)+"TXT"].replace(r'^[\(\/\\]', ' ', regex=True, inplace=True)
            df_qn['COVID24A'+str(question)+"TXT"].replace(r'[\)\/\\,]$', ' ', regex=True, inplace=True)
            df_qn['COVID24A'+str(question)+"TXT"].replace(r'(^-( ?)*$)|(?!-)\W+', ' ', regex=True, inplace=True)
            df_qn['COVID24A'+str(question)+"TXT"]= df_qn['COVID24A'+str(question)+"TXT"].str.strip()
            pat=r'^(\W*)?[a-zA-Z Ã¢]{1,2}?(\W*)?$'
            df_qn["COVID24A"+str(question)+"TXT"] = df_qn['COVID24A'+str(question)+"TXT"].str.replace(pat, '')

            #Remove rows with empty values
            df_qn.replace(r'^ ', "", inplace=True)
            df_qn.replace("", np.nan, inplace=True)
            df_qn.dropna(how='any', axis=0, inplace=True)

            #Remove entries that are just application forms:
            application_forms = ['aerosol', 'applicatievl', 'applicatievloeist', 'applicatievlst', 'applvlst', 'blaassp', 'blaasspoeling', 'bruisgr', 'bruisgran', 'bruisgranulaat', 'bruistab', 'bruistablet', 'capsule', 'concentraat', 'creme', 'dispertabl', 'dragee', 'drank', 'druppels', 'emulsie', 'gel', 'gorgeldrank', 'granulaat', 'huidspray', 'implantaat', 'implantatiestift', 'inf', 'infopl', 'infusievloeistof', 'infusion', 'infuus', 'infvls', 'infvlst', 'inhalatiepoeder', 'inhalatievloeistof/gas', 'inhalatievlst/gas', 'inhalcaps', 'inhpdr', 'inj', 'inj/infopl', 'injectie', 'injectie/infuus', 'injectiepoeder', 'injpdr', 'injsusp', 'injv', 'injvls', 'kauw-/dispertab', 'kauwtab', 'kauwtablet', 'kauwtb', 'klysma', 'lotion', 'mondpasta', 'mondspoeling', 'mondspray', 'neusspray', 'oogdruppel', 'ooginsert', 'oogwassing', 'oogzalf', 'oordr', 'oordrup', 'oordrupp', 'oordruppel', 'oordruppels', 'opl', 'OPLOS', 'oplossing', 'pasta', 'pdr', 'poeder', 'schudmixtuur', 'SIROOP', 'smeersel', 'smelttablet', 'SOLUTAB', 'spoeling', 'spray', 'strooipoeder', 'STROOP', 'SUPP', 'sus', 'susp', 'susp.', 'suspensie', 'tab', 'tablet', 'tabletten', 'tandpasta', 'tinctuur', 'vaginaalcapsule', 'vaginaalcreme', 'vaginaaltablet', 'vernevel', 'vernevelvlst', 'vlst', 'Weefsellijm', 'zalf', 'zetpil', 'zuigtablet', 'OLEOGEL']
            df_qn = df_qn[~df_qn['COVID24A'+str(question)+"TXT"].isin(application_forms)]

            #Remove entries that are just manufacturers::
       	    df_qn = df_qn[~df_qn['COVID24A'+str(question)+"TXT"].isin(manufacturers)]

            #Remove entries that are other terms - fillwords like "plus":
            df_qn = df_qn[~df_qn['COVID24A'+str(question)+"TXT"].isin(other_terms)]

            #Saving the File with 3 Columns
            df_qn.to_csv("./extractedColumns4/"+'COVID24A'+str(question)+"TXT"+"_column.csv", sep= "\t", index = False, quotechar='"', quoting = csv.QUOTE_MINIMAL )

            #Taking just the answers
            #Changing the column head to "Name" because this is a keyword for SORTA.
            df_qn.columns = ['PSEUDOIDEXT', 'Name', 'Synonym']
            #Drop the Identifiers
            df_qn_anonymous = df_qn.drop("PSEUDOIDEXT", 1)

            #Remove duplicates
            df_qn_anonymous.drop_duplicates(inplace = True)

            #Write the second file
            df_qn_anonymous.to_csv("./extractedColumns4/anonymous/"+'COVID24A'+str(question)+"TXT"+"_column_anonymous.csv", sep= ";", header = True, index = False, quotechar='"', quoting = csv.QUOTE_MINIMAL )
            

if __name__ == '__main__':
    Extractor()

