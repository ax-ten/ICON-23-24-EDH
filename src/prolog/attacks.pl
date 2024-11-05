combat(ActivePlayer, OtherPlayers, Attackers, Blockers, Targets) :-
    declare_attackers(Attackers, Targets),
    declare_blockers(OtherPlayers, Attackers, Blockers),
	handle_damage(ActivePlayer, Attackers, Blockers, Targets).

declare_attackers([], []),
declare_attackers([Attacker | OtherAttackers], [Target | OtherTargets]):-
    declare_attacker(Attacker, Target),
    declare_attackers(OtherAttackers, OtherTargets).

declare_attacker(Attacker, Target) :-
    creature(Attacker),
	\+ tapped(Attacker),
	\+ keyword(Attacker, 'defender'),
    player(Target),
    planeswalker(Target),
    battle(Target),
    format("~w attacca ~w~n", [Attacker, Target]).


handle_attacks([], _),
handle_attacks([Attacker | OtherAttackers], [BlockingA | OtherBlockers]) :-
	single_attack(Attacker, Blocker)
	handle_attacks(OtherAttackers, OtherBlockers)