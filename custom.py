"""This is to make magic numbers easier to deal with."""
import tools
import hashlib


peers = [#['192.241.212.114', 88],
         ['127.0.0.1', 8901],
         ['127.0.0.1', 8902]]


database_name = 'DB.db'
port=8900
truthd_port=8800
version = "VERSION"
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
download_many = 500  # Max number of blocks to request from a peer at the same time.
max_download = 50000
#cmd_prompt_advanced=True
##brainwallet = 'brain wallet'
##privkey = tools.det_hash(brainwallet)
##pubkey = tools.privtopub(privkey)
##address = tools.make_address([pubkey], 1)

'''
def blocktime(length):
    if length * block_reward < premine:
        return 30  # seconds
    else:
        return 60
'''
def blocktime(length): return 10
