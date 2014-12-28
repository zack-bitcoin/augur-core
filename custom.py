"""This is to make magic numbers easier to deal with."""
import multiprocessing, os
import cdecimal
peers={'192.241.212.114:8900':{'port':8900, 'blacklist':0, 'lag':40.0, 'diffLength':"0", 'length':0},
       '127.0.0.1:8900':{'port': 8900, 'blacklist':0, 'lag':40.0, 'diffLength':"0", 'length':0}}
#'69.164.196.239:8900':{'port': 8900, 'blacklist':0, 'lag':0.15, 'diffLength':"0", 'length':0}}
current_loc=os.path.dirname(os.path.abspath(__file__))
database_name = os.path.join(current_loc, 'DB')
log_file=os.path.join(current_loc, 'log')
port=8900
api_port=8899
database_port=8898
version = "0.0012"
max_key_length=6**4
total_votecoins=6**4
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
inflection = cdecimal.Decimal('0.985')
download_many = 50  # Max number of blocks to request from a peer at the same time.
max_download = 58000
#buy_shares_target='0'*4+'1'+'9'*59
buy_shares_target='0'*3+'1'+'9'*60
blocktime=60
DB = {
    'reward_peers_queue':multiprocessing.Queue(),
    'suggested_blocks': multiprocessing.Queue(),
    'suggested_txs': multiprocessing.Queue(),
    'heart_queue': multiprocessing.Queue(),
}
#seconds_per_week=604800
#cycle_length=seconds_per_week/blocktime#cycle_length
cycle_length=40
vote_reveal_length=cycle_length/10
SVD_length=cycle_length/40
voting_length=cycle_length-vote_reveal_length-SVD_length
