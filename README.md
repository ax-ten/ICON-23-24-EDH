# ICON-23-24-EDH
Progetto di Ingegneria della Conoscenza dell'anno accademico 2023-2024 all'Università degli Studi di Bari (Informatica)
## Presentazione
Da qualche anno molti più appassionati del gioco di carte di Magic: the Gathering si sono approcciati al formato di gioco 'Commander'. L'obiettivo principale di questo progetto è semplificare il processo di creazione di mazzi (Deckmaking) per gli utenti meno esperti.
###### Sviluppato da:
<table>
  <tr>
      <td><img src="https://avatars.githubusercontent.com/u/38043310?v=4" height="83" class="Avatar__StyledAvatar-sc-2lv0r8-0 gMUnCp"> </td>
      <td>
        <strong>Damato Luigi Lele</strong><br>
        Matricola: 743476<br>
        l.damato15@uniba.it
      </td>
  </tr>
</table>


## Come funziona 
Consultare la [Documentazione](https://github.com/ax-ten/ICON-23-24-EDH/blob/main/doc/Documentazione.pdf).

#### Reccomender System
Il sistema accetta il profilo dell'utente su un sito di deckbuilding (Archidekt) e consiglia un commander in base alle preferenze degli altri utenti che hanno costruito mazzi simili a quelli sul profilo.
#### Knowledge Base
È stata utilizzata la libreria **PySWIP** per Python, basata sul linguaggio di programmazione logica Prolog.\
Il popolamento di fatti nella KB avviene automaticamente all'aggiornamento dei dataset.

#### Ontologia
Espansa sulla base dell'ontologià già creata da @cmdoret: https://github.com/cmdoret/mtg_ontology.\
Per consultarla e modificarla in Python è stata usata la libreria **Owlready2**.
___

#### Installazione e Avvio
Per installare i requisiti: `pip install -r requirements.txt`.\
Per avviare, esegui `main.py`.

#### Struttura della Repository
- [/data](https://github.com/ax-ten/ICON-23-24-EDH/tree/main/data):  Ontologia, qui verranno salvati i mazzi da Archidekt.
- [/doc](https://github.com/ax-ten/ICON-23-24-EDH/tree/main/doc):  documentazione
- [/src](https://github.com/ax-ten/ICON-23-24-EDH/tree/main/src): codice sorgente Python con le classi utilizzate principalemnte
- [/old](https://github.com/ax-ten/ICON-23-24-EDH/tree/main/old): prove di codice e insieme di snippets, da passare a origin/dev
- [/keywords](https://github.com/ax-ten/ICON-23-24-EDH/tree/main/Keywords): keywords delle carte in YAML, con codice per ottenerle

## Conclusioni
Il progetto può certamente essere esteso :
- Permettere al sistema di ragionare sulle carte, adoperando il dataset di Scryfall per capire quali tattiche possono essere utili.
- Raccomandare all'utente un intero mazzo, dato un commander e altri input come budget, stile di gioco, ecc.
- Espandere l'ontologia.
___
## Altre informazioni
### Cos'è Magic: the Gathering
Si tratta di un [gioco di carte collezionabili](https://it.wikipedia.org/wiki/Gioco_di_carte_collezionabili) la cui prima espansione uscì nel 1993, in cui le carte rappresentano le magie a disposizione di un incantatore che si confronta in una battaglia con uno o più altri maghi. È un sistema di regole molto complesse, in quanto ogni espansione pubblicata aggiunge regole, carte e tipi di carte, ai quali si aggiunge la complessità inventata dai giocatori stessi, che creano nuovi formati, ognuno con regole diverse.

#### Commander
Il formato Commander è nato precedentemente sotto il nome di "Elder Dragon Highlander", poi ribattezzato dalla Wizards of the Coast, vede come protagonista del mazzo il Commander, appunto, una creatura leggendaria con abilità particolari.
Il format non è competitivo (esiste la versione competitiva, ma appunto il fulcro di ogni partita è vincere e giocare in modo efficace ed ottimale), anzi è fulcro di ogni partita divertirsi, fare scelte di gioco tra i giocatori (anche chiamate 'politics'), ed esprimere se stessi attraverso i propri mazzi. 
Il contro di un mazzo in cui oltre al commander sono da scegliere esattamente 99 altre carte diverse, è che bisogna essere veri esperti per decidere quali, in quali proporzioni, quanto devono costare (in termini di gioco e anche nella realtà).

 
