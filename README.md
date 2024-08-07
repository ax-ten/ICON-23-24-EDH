# ICON-23-24-EDH
Progetto di Ingegneria della Conoscenza dell'anno accademico 2023-2024 all'Università degli Studi di Bari (Informatica)
## Presentazione
Da qualche anno il bacino di utenti del gioco di carte di Magic: the Gathering è cresciuto a dismisura, così come l'attenzione dei giocatori veterani al formato di gioco 'Commander'. L'obiettivo principale di questo progetto è semplificare il processo di creazione di mazzi (Deckmaking) per gli utenti meno esperti.
###### Sviluppato da:
<table>
  <tr>
      <td><img src="https://avatars.githubusercontent.com/u/38043310?v=4" height="83" class="Avatar__StyledAvatar-sc-2lv0r8-0 gMUnCp"> </td>
      <td>
        <span><strong>Damato Luigi Lele</strong></span><br>
        <span>Matricola: 743476</span><br>
        <span>l.damato15@uniba.it</span>
      </td>
  </tr>
</table>


## Come funziona 
Consultare la [Documentazione](https://github.com/ax-ten/ICON-23-24-EDH/blob/main/doc/Documentazione.pdf)

#### Reccomender System
Esistono due sistemi di raccomandazione nel progetto:\
il primo accetta il nome di un commander e consiglia all'utente le migliori carte da inserire nel mazzo\
il secondo accetta invece il profilo dell'utente su un sito di deckbuilding (come Archidekt, Moxfield, EDHREC, eccetera) e consiglia\ un commander in base alle preferenze degli altri utenti che hanno costruito mazzi simili a quelli sul profilo.\

#### Knowledge Base
È stata utilizzata la libreria Pytholog per Python, basata sul linguaggio di programmazione logica Prolog.\
Il popolamento di fatti nella KB avviene automaticamente all'aggiornamento dei dataset

#### Ontologia
Espansa sulla base dell'ontologià già creata da @cmdoret: https://github.com/cmdoret/mtg_ontology\
È stato utilizzato l'editor visivo open source Protégé per la sua creazione, per consultarla in Python è stata invece usata la libreria Owlready2
___

#### Installazione e Avvio
`pip install -r requirements.txt`\
è necessario eseguire il file `main.py`

#### Struttura della Repository
- [/data](https://github.com/ax-ten/ICON-23-24-EDH/tree/main/data):  mazzi scaricati da Archidekt e l'Ontologia
- [/src](https://github.com/ax-ten/ICON-23-24-EDH/tree/main/src): codice sorgente Python

## Conclusioni
Il progetto può certamente essere esteso : #to-do
___
## Altre informazioni
### Cos'è Magic: the Gathering.
Si tratta di un [gioco di carte collezionabili](https://it.wikipedia.org/wiki/Gioco_di_carte_collezionabili) la cui prima espansione uscì nel 1993, in cui le carte rappresentano le magie a disposizione di un incantatore che si confronta in una battaglia con uno o più altri maghi. È un sistema di regole molto complesse, in quanto ogni espansione pubblicata aggiunge regole, carte e tipi di carte, ai quali si aggiunge la complessità inventata dai giocatori stessi, che creano nuovi formati, ognuno con regole diverse.

#### Commander
Il formato Commander è nato precedentemente sotto il nome di "Elder Dragon Highlander", poi ribattezzato dalla Wizards of the Coast, vede come protagonista del mazzo il Commander, appunto, una creatura leggendaria con abilità particolari.
Il format non è competitivo (esiste la versione competitiva, ma appunto il fulcro di ogni partita è vincere e giocare in modo efficace ed ottimale), anzi è fulcro di ogni partita divertirsi, fare scelte di gioco tra i giocatori (anche chiamate 'politics'), ed esprimere se stessi attraverso i propri mazzi. 
Il contro di un mazzo in cui oltre al commander sono da scegliere esattamente 99 altre carte diverse, è che bisogna essere veri esperti per decidere quali, in quali proporzioni, quanto devono costare (in termini di gioco e anche nella realtà).

 
