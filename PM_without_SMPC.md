P+E, E attacks can only work against truthcoin if the attacker has the ability to give money to the jury. If they jury has no public keys, then there is no way to give money to them.

Cryptocurrency does not depend on public/private key crypto. We can do it with hash functions alone. 

Each juror keeps 2 secrets. These secrets get revealed one at a time. Every time a secret is revealed, they generate a new secret, so that they still have 2.
Before publishing a spend tx=T, they need to publish a tx that contains hash(T).
Every time they publish any tx, they need to include hash(both secrets), and their oldest secret. Txs don't update the chain until both secrets used in creating that tx are revealed.

This alternative cryptography for securing funds has the property we need. It is impossible for coin-holders to prove their identity, unless they reveal both secrets. If they reveal both secrets, then the attacker can steal all their votecoins, and doesn't need to bribe them.

It is very important that the jury be unable to write anything in their txs besides what is necessary. Even a single bit per tx would be enough to reveal a public key over time.