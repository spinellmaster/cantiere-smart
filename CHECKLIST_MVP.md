# Checklist MVP CantiereSmart

Spunta man mano che le funzioni ci sono davvero nell’app (anche in forma base/stub).

## Flusso base
- [ ] **Preventivi**: CRUD + Export PDF + Conversione in Progetto.  (Deriva da Catalogo Lavorazioni)  
- [ ] **Progetti**: KPI di base (avanzamento %, ore, spese), albero lavorazioni istanziato dal catalogo.  
- [ ] **Lavorazioni**: Catalogo Macro → Categoria → Voce; vista operativa trasversale con KPI.  
- [ ] **Timbrature**: Start/Stop, GPS **read-only**, **≥3 foto** obbligatorie per chiusura.  
- [ ] **Report di Cantiere**: calendario Giorno/Settimana/Mese; righe = utente × lavorazione; export PDF con miniature.  
- [ ] **Spese**: CRUD con allegato; stati pending/approved/rejected; totali periodo.  
- [ ] **Flotta**: ritiro/riconsegna con GPS+foto; 1 sessione aperta per utente e per mezzo.  
- [ ] **Documenti HR**: cartelle tematiche; visibilità per utente; presa visione (ack).  
- [ ] **Dashboard (solo Admin)**: KPI principali + attività recenti + sezione lavorazioni.

## RBAC & Vincoli
- [ ] Ruoli attivi: Worker, Supervisor, Manager, Accountant, Admin (viste/azioni coerenti).  
- [ ] Vincoli rigidi: 1 timbratura cantiere aperta/utente; 1 sessione mezzo aperta/utente&mezzo; ≥3 foto; GPS non modificabile.

## Qualità (base)
- [ ] L’app parte in locale senza errori.  
- [ ] Le pagine principali sono raggiungibili dai menu (nessun 404 in giro).  
- [ ] I form salvano (anche in finto/stub) e mostrano i dati a schermo.

> Nota: la checklist è ricavata dai documenti di progetto ufficiali (Road Map, Logica, Interfaccia).
