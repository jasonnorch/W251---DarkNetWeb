
# General libraries.
import string
import numpy as np
import pandas as pd

from elasticsearch import Elasticsearch

# create ES client, create index
ES_HOST = {"host" : "158.85.217.74", "port" : 9200}
es = Elasticsearch(hosts = [ES_HOST], timeout=300)

INDEX_NAME = 'darknetmarket'
TYPE_NAME = 'product_test'
ID_FIELD = 'title_date'

#Clears data in the current index before loading
if es.indices.exists(INDEX_NAME):
    print("deleting '%s' index..." % (INDEX_NAME))
    res = es.indices.delete(index = INDEX_NAME)
    print(" response: '%s'" % (res))

#since we are running locally, use one shard and no replicas
request_body = {
    "settings" : {
        "number_of_shards": 1,
        "number_of_replicas": 0
    }
}

#Creates index
print("creating '%s' index..." % (INDEX_NAME))
res = es.indices.create(index = INDEX_NAME, body = request_body)
print(" response: '%s'" % (res))

#Read in cleaned data
all2 = pd.read_csv("modeled_subcategories.csv")

#Kibana will not load rows with NaN values
#Replace null strings with "Missing" and null numerics with -1
all2["category"] = all2["category"].fillna("Missing")
all2["vendor"] = all2["vendor"].fillna("Missing")
all2["ships_from"] = all2["ships_from"].fillna("Missing")
all2["ships_to"] = all2["ships_to"].fillna("Missing")
all2["SubCat2"] = all2["SubCat2"].fillna("Missing")
all2["Cat2"] = all2["Cat2"].fillna("Missing")

all2["Weight"] = all2["Weight"].fillna(-1)
all2["PPW"] = all2["PPW"].fillna(-1)
all2["PPWC"] = all2["PPWC"].fillna(-1)


bulk_data2 = []
#Read through each listing in the data
for row in range(0,all2.shape[0]/10): 
	data_dict = {}
	#For each field in the row
	for i in range(0,all2.shape[1]):
		#Adds field to the dictionary
		if all2.columns.values[i] == "Cat2": data_dict[all2.columns.values[i]] = unicode(str(all2.iloc[row][i]), "utf-8", errors="ignore") 
        elif all2.columns.values[i] == "SubCat2": data_dict[all2.columns.values[i]] = unicode(str(all2.iloc[row][i]), "utf-8", errors="ignore")
        else: data_dict[all2.columns.values[i]] = all2.iloc[row][i]
	#Creates a dictionary of Index, Type, and ID
    op_dict = {
        "index": {
            "_index": INDEX_NAME, 
            "_type": TYPE_NAME, 
            "_id": data_dict[ID_FIELD]
        }
    }
	#Adds dictionaries to the bulk data load file
    bulk_data2.append(op_dict)
    bulk_data2.append(data_dict)
	
	if row%1000==0: print row
	
	if row%5000==0:
		# bulk index the data
		print("bulk indexing...")
		res = es.bulk(index = INDEX_NAME, body = bulk_data2, refresh = True, timeout=300)		
		bulk_data2 = []
		
# Load final batch
print("bulk indexing...")
res = es.bulk(index = INDEX_NAME, body = bulk_data2, refresh = True, timeout=300)		
bulk_data2 = []