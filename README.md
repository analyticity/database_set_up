# Pomocné scripty pre nastavanie databázy 

## Merging_files 
- zoberie subory vygenerovane kazde dve minuty z Waze 
- spoji do jedneho vysledneho suboru 
- pre detail, pozri `README.md` v tomto priecinku 

## data_change_in_time_verification.py 
- overuje ako sa menia data v case 
- vystup pise na stdout 
- sluzi iba na kontrolu dat 


## downloader.py 
- stahuje data z Waze for Cities Program
- vzdy novy subor stiahne po 2 minutach (kedy sa data z Waze updatuju)
- Uklada iba dump, nijak dalej so subormi nepracuje 