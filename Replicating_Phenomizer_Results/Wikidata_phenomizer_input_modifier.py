# The goal of this script is to query OMIM id's from the Wikidata. Running this  script will return a GAF files modified with OMIM id's.  To see which are the top ranked returned diseases after Wikidata query, use BOQA (https://github.com/sulab/boqa ). 
# Note: This is a copy of phenomizer (https://github.com/SuLab/Wikidata-phenomizer). The difference between this and phenomizer is it has an input to accept any hpo.tab file, which makes it easier to load in files.  Additionally, it Queries for OMIM id's instead of Orphanet id's.  Lastly, the file is more appropriately named making it less confusing.
# To run this script:
# python3 Wikidata_phenomizer_input_modifier.py [Put your phenotype_annotation.tab file name here without brackets]
"""
Get the disease phenotypes from wikidata,
merge them with disease phenotypes HPO GAF file
Feed them into ontologizer
"""
import pandas as pd
import sys

# Check if there is a phenotype_annotation file appended with command. If not, default=phenotype_annotation.tab.
if len(sys.argv) == 1:
    fname = "phenotype_annotation"
else:
    fname = sys.argv[1]
    fname = fname[0:-4]

# WikiData Query    
from wikidataintegrator import wdi_core

wikidata_all_query = """
SELECT ?hpo_id ?symptom_wdLabel ?omim_id ?disease_wdLabel WHERE {
    ?disease_wd wdt:P780 ?symptom_wd .
    ?symptom_wd wdt:P3841 ?hpo_id .
    ?disease_wd wdt:P492 ?omim_id .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
  }"""

df_wd = wdi_core.WDItemEngine.execute_sparql_query(wikidata_all_query, as_dataframe=True)

tab_colnames = ['DB', 'DB_Object_ID', 'DB_Name', 'Qualifier', 'HPO_ID', 'DB_Reference',
                'Evidence_Code', 'Onset modifier', 'Frequency', 'Sex', 'Modifier',
                'Aspect', 'Date_Created', 'Assigned_By']
gaf = pd.read_csv(fname + ".tab", delimiter="\t", names=tab_colnames, dtype=str)
disease_label = dict(zip(gaf.DB_Reference, gaf.DB_Name))

"""
GAF file
OMIM	101120	ACROCEPHALOPOLYSYNDACTYLY TYPE III		HP:0000303	OMIM:101120	IEA				O		HPO:iea[2009-02-17]
"""
df_wd['DB'] = 'OMIM'
df_wd['DB_Object_ID'] = df_wd.omim_id.str.split(":").map(lambda x: x[0])
df_wd['DB_Name'] = df_wd.disease_wdLabel
df_wd['Qualifier'] = ""
df_wd['HPO_ID'] = df_wd.hpo_id
df_wd['DB_Reference'] = df_wd['DB'] + ":" + df_wd['DB_Object_ID']
df_wd['Evidence_Code'] = "IEA"
df_wd['Onset modifier'] = ""
df_wd['Frequency'] = ""
df_wd['Sex'] = ""
df_wd['Modifier'] = "O"
df_wd['Aspect'] = ""
df_wd['Date_Created'] = "wd:xxx[2018-12-10]"
df_wd['DB_Name_hpo'] = df_wd.DB_Reference.map(disease_label.get)
df_wd['DB_Name'] = df_wd.DB_Name_hpo.combine_first(df_wd.DB_Name)

df_wd_gaf = gaf.append(df_wd)

df_wd_gaf[tab_colnames].to_csv(fname + "_wd.tab", sep="\t", header=False, index=False)

########
# drop dupes for counting purposes
gaf = gaf.drop_duplicates(['DB_Object_ID', 'HPO_ID'])
df_wd = df_wd.drop_duplicates(['DB_Object_ID', 'HPO_ID'])
df_wd_gaf = gaf.append(df_wd)

print("number of hpo annotations: {}".format(len(gaf)))
print("number of wikidata annotations: {}".format(len(df_wd)))

dupes = df_wd_gaf[df_wd_gaf.duplicated(subset=['HPO_ID', 'DB_Reference'], keep="last")].sort_values(['HPO_ID', 'DB_Reference'])
dupes = dupes[['DB_Name', 'DB_Reference', 'HPO_ID', 'symptom_wdLabel']]
print("number overlap annotations: {}".format(len(dupes)))

# ones in wikidata, but not in hpo:
wd = set(tuple(zip(df_wd.HPO_ID, df_wd.DB_Reference)))
hpo = set(tuple(zip(gaf.HPO_ID, gaf.DB_Reference)))
new_wd = wd-hpo

new_df = df_wd[df_wd.apply(lambda row: (row.HPO_ID, row.DB_Reference) in new_wd, axis=1)]
new_df = new_df[['DB_Name', 'DB_Reference', 'HPO_ID', 'symptom_wdLabel']]

print("\ntop unique disease-phenotypes in wd:")
print(new_df.DB_Name.value_counts()[:10])
