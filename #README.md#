Truthcoin-POW
=============

If you are not a programmer, then you are lost, and should click this link: http://www.augur.net/prototype/

adding abilities from the truthcoin project to basiccoin. https://github.com/psztorc/Truthcoin
A podcast interview where I describe this project: http://economicsdetective.com/2014/10/truthcoin-prediction-markets-and-anarchy-with-zack-hess/

Donations: 1GbpRPE83Vjg73KFvTVZ4EnS2qNkiLY5TT

=====INSTALL 
for Mac

    sudo pip install m3-cdecimal 
    git clone https://github.com/zack-bitcoin/Truthcoin-POW.git
    cd Truthcoin-POW

for Ubuntu

    sudo apt-get update
    sudo apt-get install libpython-dev
    sudo pip2 install m3-cdecimal 
    sudo pip install six
    git clone https://github.com/zack-bitcoin/Truthcoin-POW.git
    cd Truthcoin-POW

====RUN A NODE

    python2.7 truth_cli.py start

It will take time to download the blockchain.

====TALK TO THE NODE

    python2.7 truth_cli.py

====About this software

For now, there is a week-long cycle.
for the first 7/8ths of the cycle: votecoin-holders may give encrypted votes on decisions. (in the final version of truthcoin, this step will take 1000+ blocks)
for the next 1/10th of the cycle: votecoin-holders may decrypt their votes
for the final 1/40th of the cycle: if there are at least 3 votecoin-holders, and at least 5 decisions they have voted on, then we can do SVD to come to consensus about these decisions.

Security assumption for truthcoin-pow is a lot weaker than bitcoin. It is only
secure if there is always at least one person mining for blocks.
If more than 2 hours pass where no-one is mining, then it becomes far easier to attack.

This blockchain currently has a bad retargetting algorithm. Because of this, it is not
suitable for holding real value. It is still good for testing and developing a truthcoin
system.
Long term goal is to use proof-of-stake anyway.