"""This is to make magic numbers easier to deal with."""
import tools, hashlib
peers = [['192.241.212.114', 8900]]
database_name = 'DB.db'
port=8900
truthd_port=8800
version = "VERSION"
#either brain_wallet, or pubkey must be uncommented. They need 'quotes' around them. Do not use any spaces ' ', underscore is better '_'. If ynou want to mine, then you need to uncomment the first one. If you want to leave your computer unattended, then you should use the second one.
brain_wallet='brainwallet'
#pubkey='045f822change_this_insecurea86eb5cdfbbe58198da7ef669f895ab992dd57a2d33337df6a6d763380225887be2cca4c1bb5791808f43cc353db89a70faae37'
#pubkey='041811b6f26040385c7f2a9fde1b716e9fb5505bed514ecd6a670d2c56f857f75a1f89da79afc916875012f525b0fefd2cc91ed69d18d22e36eaa01db6eff68365'
block_reward = 10 ** 5
premine = 5 * 10 ** 6
fee = 10 ** 3
propose_decision_fee = 10 ** 5
create_jury_fee=10**4
jury_vote_fee=500
reveal_jury_vote_fee=500
SVD_consensus_fee=0
buy_shares_fee=10**5
collect_winnings_reward=5*10**4
# Lower limits on what the "time" tag in a block can say.
mmm = 100
# Take the median of this many of the blocks.
# How far back in history do we look when we use statistics to guess at
# the current blocktime and difficulty.
history_length = 400
# This constant is selected such that the 50 most recent blocks count for 1/2 the
# total weight.
inflection = 0.985
download_many = 50  # Max number of blocks to request from a peer at the same time.
max_download = 50000
def blocktime(length): return 30
