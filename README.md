Truthcoin-POW
=============

adding abilities from the truthcoin project to basiccoin. https://github.com/psztorc/Truthcoin

Donations: 1GbpRPE83Vjg73KFvTVZ4EnS2qNkiLY5TT

INSTALL (for Ubuntu)

    sudo apt-get update
    sudo apt-get install python-leveldb python-numpy git
    git clone https://github.com/zack-bitcoin/Truthcoin-POW.git
    cd Truthcoin-POW

INSTALL (for Arch Linux)
    sudo pacman -S python2-numpy python2-pip
    sudo pip2 install leveldb
    git clone https://github.com/zack-bitcoin/Truthcoin-POW.git
    cd Truthcoin-POW    

To run a truthcoin node

    python2 threads.py

Then to talk to truthcoin from the terminal use:

    ./truthd.py

It will take time to download the blockchain.

For now, there is a 20-block cycle.
1-10: votecoin-holders may give encrypted votes on decisions. (in the final version of truthcoin, this step will take 1000+ blocks)
11-15: votecoin-holders may decrypt their votes
16-20: if there are at least 3 votecoin-holders, and at least 5 decisions they have voted on, then we can do SVD to come to consensus about these decisions.