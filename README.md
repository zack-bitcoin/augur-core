Truthcoin-POW
=============

adding abilities from the truthcoin project to basiccoin. https://github.com/psztorc/Truthcoin

Donations: 1GbpRPE83Vjg73KFvTVZ4EnS2qNkiLY5TT

INSTALL (for ubuntu)

    sudo apt-get install git
    sudo apt-get install python-leveldb
    sudo apt-get install python-rpy2
    git clone https://github.com/zack-bitcoin/Truthcoin-POW.git
    cd Truthcoin-POW

To run a truthcoin node

    python threads.py

Then to talk to truthcoin use:

    python truthd.py



For now, there is a 20-block cycle.
1-10: votecoin-holders may give encrypted votes on decisions. (in the final version of truthcoin, this step will take 1000+ blocks)
11-15: votecoin-holders may decrypt their votes
16-20: if there are at least 3 votecoin-holders, and at least 5 decisions they have voted on, then we can do SVD to come to consensus about these decisions.