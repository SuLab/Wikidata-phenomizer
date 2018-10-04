"""
Get the disease phenotypes from wikidata,
merge them with disease phenotypes HPO GAF file
Feed them into ontologizer
"""
import pandas as pd

from wikidataintegrator import wdi_core

wikidata_all_query = """
SELECT ?hpo_id ?symptom_wdLabel ?orphanet_id ?disease_wdLabel WHERE {
    ?disease_wd wdt:P780 ?symptom_wd .
    ?symptom_wd wdt:P3841 ?hpo_id .
    ?disease_wd wdt:P1550 ?orphanet_id .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}"""

df_wd = wdi_core.WDItemEngine.execute_sparql_query(wikidata_all_query, as_dataframe=True)

tab_colnames = ['DB', 'DB_Object_ID', 'DB_Name', 'Qualifier', 'HPO_ID', 'DB_Reference',
                'Evidence_Code', 'Onset modifier', 'Frequency', 'Sex', 'Modifier',
                'Aspect', 'Date_Created', 'Assigned_By']
gaf = pd.read_csv("phenotype_annotation.tab", delimiter="\t", names=tab_colnames)

"""
GAF file
OMIM	101120	ACROCEPHALOPOLYSYNDACTYLY TYPE III		HP:0000303	OMIM:101120	IEA				O		HPO:iea[2009-02-17]
"""
df_wd['DB'] = 'ORPHA'
df_wd['DB_Object_ID'] = df_wd.orphanet_id.str.split(":").map(lambda x: x[0])
df_wd['DB_Name'] = df_wd.disease_wdLabel
df_wd['Qualifier'] = ""
df_wd['HPO_ID'] = df_wd.hpo_id
df_wd['DB_Reference'] = df_wd['DB'] + ":" + df_wd['DB_Object_ID']
df_wd['Evidence_Code'] = "IEA"
df_wd['Onset modifier'] = ""
df_wd['Frequency'] = ""
df_wd['Sex'] = ""
df_wd['Modifier'] = "O"
df_wd['Aspect'] = df_wd.disease_wdLabel
df_wd['Date_Created/Assigned_By'] = "wd:xxx[2018-10-04]"
# df_wd['Assigned_By'] = 'wd'

df_wd_gaf = df_wd.append(gaf)

df_wd_gaf[tab_colnames].to_csv("phenotype_annotation_wd.tab", sep="\t", header=False, index=False)
