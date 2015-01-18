P+E, E attacks:
suppose there is a game where you can vote 0 or 1
if you vote with the majority you get P, else you get 0
let's say for this round 1 is supposed to be the "correct" answer
attacker makes a contract
says:
if you vote 0, then if the majority votes 1 you get P + ϵ, if the majority votes 0 you get ϵ
if you vote 1, then get nothing from the contract
hence, it's now a dominant strategy to vote 0
because your reward is higher either way
hence everyone votes 0
hence attacker only pays ϵ
so attacker takes over the contract for free
there's also a fairly obvious variant for double-spending PoW 

P+E, E attacks can only work against truthcoin if the attacker has the ability to give money to the jury. If they jury has no public keys, then there is no way to give money to them.

Cryptocurrency does not depend on public/private key crypto. We can do it with hash functions alone. 

Each juror keeps 2 secrets. These secrets get revealed one at a time. Every time a secret is revealed, they generate a new secret, so that they still have 2.
Before publishing a spend tx=T, they need to publish a tx that contains hash(T).
Every time they publish any tx, they need to include hash(both secrets), and their oldest secret. Txs don't update the chain until both secrets used in creating that tx are revealed.

This alternative cryptography for securing funds has the property we need. It is impossible for coin-holders to prove their identity, unless they reveal both secrets. If they reveal both secrets, then the attacker can steal all their votecoins, and doesn't need to bribe them.

It is very important that the jury be unable to write anything in their txs besides what is necessary. Even a single bit per tx would be enough to reveal a public key over time.