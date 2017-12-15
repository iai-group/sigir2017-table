# sigir2017-table

This repository provides reources developed within the following paper:
> S. Zhang and K. Balog. EntiTables: Smart Assistance for Entity-Focused Tables. - SIGIR'17 

This study is an effort aimed at reproducing the result presented in the Smart table paper.


This repository is structured as follows:

- Data: This folder has the table id files, and will be updated late on!
- Population: All the core evaluation of population tasks are provided here.
- Output: The output files can only be requested by email now.

## Data
The data we used are public data sets:
- DBpedia 2015-10
- WikiTable from http://websail-fe.cs.northwestern.edu/TabEL/

## Population
[NOTE] We are using elstic 2 ( > 2.3), elasticsearch 5 will encounter some minor problems with elastic.py wrapper.
To score the column labels, we need to build an table index with multiple fields using elasticsearch.
An exmaple indexer is provided for indexing. Index your table corpus data following this example and start your population:)

## Citation
```
@inproceedings{Zhang:2017:ESA,
 author = {Zhang, Shuo and Balog, Krisztian},
 title = {EntiTables: Smart Assistance for Entity-Focused Tables},
 booktitle = {Proceedings of the 40th International ACM SIGIR Conference on Research and Development in Information Retrieval},
 series = {SIGIR '17},
 year = {2017},
 isbn = {978-1-4503-5022-8},
 location = {Shinjuku, Tokyo, Japan},
 pages = {255--264},
 numpages = {10},
 url = {http://doi.acm.org/10.1145/3077136.3080796},
 doi = {10.1145/3077136.3080796},
 acmid = {3080796},
 publisher = {ACM},
 address = {New York, NY, USA},
 keywords = {intelligent table assistance, semantic search, table completion},
}
```


## Contact
If you have any question, please contact Shuo Zhang at shuo.zhang@uis.no or Krisztian Balog at krisztian.balog@uis.no
