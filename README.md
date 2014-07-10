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

To run 1 node

    python workers.py
    and send your browser to: http://localhost:8701

To quickly run 5 nodes

    ./go.sh

Then send your browser to 

    http://localhost:8701
    http://localhost:8702
    http://localhost:8703
    http://localhost:8704
    http://localhost:8705


For now, there is a 20-block cycle.
1-10: votecoin-holders may give encrypted votes on decisions. (in the final version of truthcoin, this step will take 1000+ blocks)
11-15: votecoin-holders may decrypt their votes
16-20: if there are at least 3 votecoin-holders, and at least 5 decisions they have voted on, then we can do SVD to come to consensus about these decisions.