"""This is to make magic numbers easier to deal with."""
import tools, hashlib
peers = [['192.241.212.114', 8900]]
database_name = 'DB.db'
port=8900
api_port=8800
version = "VERSION2"
#if you want to boot up more quickly without having to type your brainwallet or pubkey, then uncomment and update one of the following 2 lines.
#brain_wallet='brainwalletInsecureChangeThis'
#pubkey='045f822change_this_insecurea86eb5cdfbbe58198da7ef669f895ab992dd57a2d33337df6a6d763380225887be2cca4c1bb5791808f43cc353db89a70faae37'
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
download_many = 100  # Max number of blocks to request from a peer at the same time.
max_download = 58000
def blocktime(length): return 60
