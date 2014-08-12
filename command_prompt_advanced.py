import sys
from getch import getch
import copy
import time
import tools

def sys_print(txt): return sys.stdout.write(txt)
def row(DB): return DB['output_lengths']+len(DB['previous_commands'])
def move_cursor(DB, column, row): return sys_print('\033['+str(column+1)+';'+str(row+1)+'H')
def set_cursor(DB): return move_cursor(DB, row(DB), DB['string_position'])
def delete_to_end_of_line(DB): return sys_print('\033[K')
def change_line(DB, f):
    move_cursor(DB, row(DB), 0)
    delete_to_end_of_line(DB)
    f(DB)
    sys.stdout.write(DB['command'])
    if DB['string_position']>=DB['command']:
        DB['string_position']=len(DB['command'])
    set_cursor(DB)
def kill(DB):
    def f(DB):
        DB['yank']=DB['command'][DB['string_position']:]
        DB['command']=DB['command'][:DB['string_position']]
    return change_line(DB, f)
def type_letter(l):
    def g(DB):
        DB['command']=DB['command'][:DB['string_position']]+l+DB['command'][DB['string_position']:]
        DB['string_position']+=1
    return lambda DB: change_line(DB, g)
def backspace(DB):
    def g(DB):
        DB['command']=DB['command'][:DB['string_position']-1]+DB['command'][DB['string_position']:]
        DB['string_position']-=1        
    if not DB['string_position']==0:
        change_line(DB, g)
def forward_delete(DB):
    if not DB['string_position']>=len(DB['command']):
        DB['string_position']+=1
        backspace(DB)
def move_vert(n, DB):
    def f(DB):
        DB['command_pointer']+=n
        DB['command']=DB['previous_commands'][DB['command_pointer']]
        DB['string_position']=len(DB['command'])
    change_line(DB, f)
def up_arrow(DB):
    if not DB['command_pointer']==0:
        move_vert(-1, DB)
def down_arrow(DB):
    if DB['command_pointer']<len(DB['previous_commands'])-1:
        move_vert(1, DB)
def right_arrow(DB):
    if not DB['string_position']>=len(DB['command']):
        DB['string_position']+=1
        set_cursor(DB)
def left_arrow(DB):
    if not DB['string_position']==0:
        DB['string_position']-=1
        set_cursor(DB)
def front_of_line(DB):
    DB['string_position']=0
    set_cursor(DB)
def end_of_line(DB):
    DB['string_position']=len(DB['command'])
    set_cursor(DB)
def chunks_of_width(width, s):
    if len(s)<width: return [s]
    else: return [s[:width]]+chunks_of_width(width, s[width:])
def enter(DB):
    print('')
    DB['previous_commands'].append(DB['command'])
    c=copy.deepcopy(DB['command'])
    c=c.split(' ')
    tools.log('c: ' +str(c))
    DB['iq'].put(c)
        #response=truthcoin_api.Do_func(DB)#remove this line till...
        #if type(response)==str:
        #    response_chunks=chunks_of_width(80, response)
        #    for r in response_chunks:
        #        print(r)
        #        DB['output_lengths']+=1#here
    if c[0]=='stop':
        sys.exit(1)
    if len(DB['previous_commands'])>1000:
        DB['previous_commands'].remove(DB['previous_commands'][0])
    front_of_line(DB)
    DB['command']=''
    DB['command_pointer']=len(DB['previous_commands'])
    while DB['oq'].empty():
        time.sleep(0.1)
def special_keys(DB):
    key = ord(getch())
    #print('special key 1: ' +str(key))
    key = ord(getch())
    #print('special key 2: ' +str(key))
    read_letter(key, {'51':forward_delete,
                   '65':up_arrow,
                   '66':down_arrow,
                   '67':right_arrow,
                   '68':left_arrow},
             DB)
keyboard={
    '1':front_of_line,#ctrl+a
    '5':end_of_line,#ctrl+e
    '6':right_arrow,#ctrl+f
    '14':down_arrow,#ctrl+n
    '2':left_arrow,#ctrl+b
    '16':up_arrow,#ctrl+p
    '11':kill,#ctrl+k
    '127':backspace,
    '4':forward_delete,#ctrl+d
    '10': enter,
    '27': special_keys,
    '46':type_letter('.'),
    '32':type_letter(' '),
    '40':type_letter('('),
    '41':type_letter(')'),
    '44':type_letter(','),
    '93':type_letter(']'),
    '91':type_letter('['),
    '95':type_letter('_'),
    '63':type_letter('?'),
}
letters={'\n':enter}
for l in ['.', ' ', '(', ')', ',', ']', '[', '_', '?']:
    letters[l]=type_letter(l)
atoz=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
for l, start in [[['0','1','2','3','4','5','6','7','8','9'], 48],
                 [atoz, 97],
                 [map(lambda x: x.capitalize(), atoz), 65]]:
    for i in range(start, start+len(l)):
        n=i-start
        f=type_letter(l[n])
        keyboard[str(i)]=f
        letters[str(l[n])]=f
def read_letter(key, commands, DB): commands.get(str(key), (lambda DB: 42))(DB)
def yank(DB):
    for l in DB['yank']:
        read_letter(l, letters, DB)
keyboard['25']=yank#ctrl+y
def clear_screen(DB): return sys_print('\033[2J')
def run_script(DB, script):
    DB['yank']=script
    yank(DB)
    DB['yank']=''
def main(i_queue, o_queue, script):
    DB={}
    DB['command']=''
    DB['previous_commands']=[]
    DB['command_pointer']=0
    DB['string_position']=0
    DB['yank']=''
    DB['output_lengths']=0
    DB['args']=[]
    DB['iq']=i_queue
    DB['oq']=o_queue
    clear_screen(DB)
    set_cursor(DB)
    run_script(DB, script)
    while True:
        while not(o_queue.empty()):
            response=o_queue.get()
            tools.log('from o_queue: ' +str(response))
            response_chunks=chunks_of_width(80, str(response))
            for r in response_chunks:
                print(r)
                DB['output_lengths']+=1#here
        time.sleep(0.05)
        key = ord(getch())
        read_letter(key, keyboard, DB)



