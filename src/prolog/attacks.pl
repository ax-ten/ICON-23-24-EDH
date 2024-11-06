
combat(ActivePlayer, OtherPlayers, Attackers, Blockers, Targets) :-
    declare_attackers(Attackers, Targets),
    declare_blockers(Blockers, Attackers),
    handle_damages(Attackers),
    clean_board(Permanents).


% Dichiarazione degli attaccanti
declare_attackers([], []).
declare_attackers([Attacker | OtherAttackers], [Target | OtherTargets]) :-
    declare_attacker(Attacker, Target),
    declare_attackers(OtherAttackers, OtherTargets).



declare_attacker(Attacker, Target) :-
    creature(Attacker),
    \+ tapped(Attacker),
    \+ keyword(Attacker, 'defender'),
    (player(Target); planeswalker(Target); battle(Target)),
    format("Vuoi che ~w attacchi ~w? (s/n): ", [Attacker, Target]), read(Response),
    ( Response == s ->
        tap(Attacker),
        assert(attacking(Attacker, Target))
    ; Response \= n ->
        format("Input non valido.~n"),
        declare_attacker(Attacker, Target)
    ).



% Dichiarazione dei bloccanti
declare_blockers([], []).
declare_blockers([Blocker | OtherBlockers], [Attacker | OtherAttackers]) :-
    declare_blocker(Blocker, Attacker),
    declare_blockers(OtherBlockers, OtherAttackers).

declare_blocker(Blocker, Attacker) :-
    creature(Blocker),
    attacking(Attacker, Target),
    controller(Target, Player),
    controller(Blocker, Player),
    \+ tapped(Blocker),
    \+ blocking(_, Blocker),
    (   \+ keyword(Attacker, flying)
    ;   keyword(Blocker, flying)
    ;   keyword(Blocker, reach)
    ),
    format("Bloccare ~w con ~w? ~w è il bersaglio. (s/n): ", [Attacker, Blocker, Target]), read(Response),
    ( Response == s ->
        assert(blocking(Attacker, Blocker))
    ; Response \= n ->
        format("Input non valido.~n"),
        declare_blocker(Blocker, Attacker)
    ).



% per ottenere i bloccanti
blockers(Attacker, Blockers) :-
    findall(Blocker, blocking(Attacker, Blocker), Blockers).



% Gestione dei danni
handle_damages([]).
handle_damages([Attacker | OtherAttackers]) :-
    attacking(Attacker, Target),
    blockers(Attacker, Blockers),
    damage(Attacker, AttackerDamage),
    ( Blockers = [] ->
        apply_damage(Target, AttackerDamage),
        format("~w attacca direttamente ~w infliggendo ~d danni~n", [Attacker, Target, AttackerDamage])
    ;   damage_distribution(Attacker, AttackerDamage, Blockers, Target)
    ),
    handle_damages(OtherAttackers).



% Distribuzione dei danni
damage_distribution(_, _, []).
damage_distribution(Attacker, AttackerDamage, [Blocker | OtherBlockers], Target) :-
    length(OtherBlockers, NumBlockers),
    required_damage(Blocker, RequiredDamage),
    ( AttackerDamage >= RequiredDamage ->
        format("Assegna massimo ~d danni a ~w, ~d altri bloccanti. Richiesti: ~d~n", [AttackerDamage, Blocker, NumBlockers, RequiredDamage]),
        read(AssignedDamage),
        ( AssignedDamage < 0 ; AssignedDamage > AttackerDamage ->
            format("Assegnazione non valida.~n"),
            damage_distribution(Attacker, AttackerDamage, [Blocker | OtherBlockers], Target)
        ;   format("Inflitti ~d danni a ~w.~n", [AssignedDamage, Blocker]),
            NewAttackerDamage is AttackerDamage - AssignedDamage,
            apply_damage(Blocker, AssignedDamage),
            damage_distribution(Attacker, NewAttackerDamage, OtherBlockers, Target)
        )
    ;   apply_damage(Blocker, AttackerDamage),
        damage_distribution(Attacker, 0, OtherBlockers, Target)
    ).


% Calcolo del danno richiesto
required_damage(Target, RequiredDamage) :-
    ( creature(Target) ->
        toughness(Target, Toughness),
        ( keyword(Target, 'deathtouch') ->
            RequiredDamage is 1
        ;   RequiredDamage is Toughness
        )
    ; planeswalker(Target) ->
        loyalty(Target, RequiredDamage)
    ; battle(Target) ->
        defense(Target, RequiredDamage)
    ).


% Applicazione del danno
apply_damage(Target, Damage) :-
    required_damage(Target, RequiredDamage),
    ( Damage >= RequiredDamage ->
        kill(Target)
    ; creature(Target) ->
        toughness(Target, Toughness),
        TempToughness is Toughness - Damage,
        retractall(temp_toughness(Target, _)),
        assert(temp_toughness(Target, TempToughness))
    ; (planeswalker(Target); battle(Target)) ->
        counters(Target, Counters),
        NewCounters is Counters - Damage,
        retractall(counters(Target, _)),
        assert(counters(Target, NewCounters))
    ).
