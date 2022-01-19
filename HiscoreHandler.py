import concurrent.futures as ft
import requests as rq
import threading
import json
import os.path

SKILLS = [
    "total",
    "attack",
    "defence",
    "strength",
    "hitpoints",
    "ranged",
    "prayer",
    "magic",
    "cooking",
    "woodcutting",
    "fletching",
    "fishing",
    "firemaking",
    "crafting",
    "smithing",
    "mining",
    "herblore",
    "agility",
    "thieving",
    "slayer",
    "farming",
    "runecrafting",
    "hunter",
    "construction",
]
MINIGAMES = [
    "league points",
    "Bounty Hunter Rogue",
    "Bounty Hunter Hunter",
    "Clue Scrolls (all)",
    "Clue Scrolls (beginner)",
    "Clue Scrolls (easy)",
    "Clue Scrolls (medium)",
    "Clue Scrolls (hard)",
    "Clue Scrolls (elite)",
    "Clue Scrolls (master)",
    "Last Man Standing",
    "Soul Wars",
]
BOSSES = [
    "Abyssal Sire",
    "Alchemical Hydra",
    "Barrows Chests",
    "Bryophyta",
    "Callisto",
    "Cerberus",
    "Chambers of Xeric",
    "Chambers of Xeric: Challenge Mode",
    "Chaos Elemental",
    "Chaos Fanatic",
    "Commander Zilyana",
    "Corporeal Beast",
    "Crazy Archaeologist",
    "Dagannoth Prime",
    "Dagannoth Rex",
    "Dagannoth Supreme",
    "Deranged Archaeologist",
    "General Graardor",
    "Giant Mole",
    "Grotesque Guardians",
    "Hespori",
    "Kalphite Queen",
    "King Black Dragon",
    "Kraken",
    "Kree'Arra",
    "K'ril Tsutsaroth",
    "Mimic",
    "Nex",
    "Nightmare",
    "Phosani's Nightmare",
    "Obor",
    "Sarachnis",
    "Scorpia",
    "Skotizo",
    "Tempoross",
    "The Guantlet",
    "The Corrupted Guantlet",
    "Theatre of Blood",
    "Theatre of Blood: Hard Mode",
    "Thermonuclear Smoke Devil",
    "TzKal-Zuk",
    "TzTok-Jad",
    "Venenatis",
    "Vet'ion",
    "Vorkath",
    "Wintertodt",
    "Zalcano",
    "Zulrah",
]
# format of the parsed data
FORMATTING = {
    'SKILLS':['rank', 'level', 'xp'],
    'MINIGAMES': ['rank', 'kc'],
    'BOSSES': ['rank', 'kc']
}
LITE_URL = 'http://services.runescape.com/m=hiscore_oldschool_seasonal/index_lite.ws?player='
TEST_LITE_URL = 'http://services.runescape.com/m=hiscore_oldschool_ironman/index_lite.ws?player='
OS_CACHE_URL = './Res/os.ch'
IR_CACHE_URL = './Res/ir.ch'

cache_lock = threading.Lock()
def __parse_data__(rsn, d):
    if d.startswith('<!'): return None
    d_s = d.split('\n')
    ind = 0
    res = {'rsn':rsn}

    for skill in SKILLS:
        data = list(map(lambda x:int(x)*(int(x) > 0), d_s[ind].split(',')))
        res[skill] = {FORMATTING['SKILLS'][0]:data[0], FORMATTING['SKILLS'][1]:data[1], FORMATTING['SKILLS'][2]:data[2]}
        ind += 1
    for mg in MINIGAMES:
        data = list(map(lambda x:int(x)*(int(x) > 0), d_s[ind].split(',')))
        res[mg] = {FORMATTING['MINIGAMES'][0]:data[0], FORMATTING['MINIGAMES'][1]:data[1]}
        ind += 1
    for boss in BOSSES:
        data = list(map(lambda x:int(x)*(int(x) > 0), d_s[ind].split(',')))
        res[boss] = {FORMATTING['BOSSES'][0]:data[0], FORMATTING['BOSSES'][1]:data[1]}
        ind += 1
    return res

def __get_cache__():
    cache_lock.acquire()
    return \
        json.loads(open(OS_CACHE_URL, 'r').readline()) if os.path.isfile(OS_CACHE_URL) else None, \
        json.loads(open(IR_CACHE_URL, 'r').readline()) if os.path.isfile(IR_CACHE_URL) else None

def __save_cache__(data, IR: bool):
    f = open(IR_CACHE_URL if IR else OS_CACHE_URL, 'w')
    f.write(json.dumps(data))
    f.close()
    cache_lock.release()

def get_data(l, IR:bool):
    res = []
    os_cache, ir_cache = __get_cache__()
    if (ir_cache if IR else os_cache) is None:
        res = update_players_data(l)
    else:
        found = []
        for rsn in l:
            if rsn.endswith(',\n'): rsn = ''.join(rsn[:-2])
            if rsn.endswith(','): rsn = ''.join(rsn[:-1])
            for e in ir_cache if IR else os_cache:
                if e['rsn'] == rsn:
                    res.append(e)
                    found += [rsn]
                    break
        res += update_players_data(list(set(l) - set(found)))
    __save_cache__(res, IR)
    return res

def update_player_data(p): return update_players_data([p])
def update_players_data(l):
    res = []
    def add_user(rsn):
        d = rq.get(LITE_URL+rsn).text
        return __parse_data__(rsn, d)
    # get a thread pool to wait for several api calls at the same time
    ex = ft.ThreadPoolExecutor(max_workers=100)
    ps = []
    for e in l:
        # submit a task for each rsn
        ps += [ex.submit(add_user, e)]
    for e in ft.as_completed(ps):
        try:
            r = e.result()
            if r is not None: res += [r]
        except Exception as e:
            print(e)
    os_cache, ir_cache = __get_cache__()
    if os_cache is not None:
        pairs_found = []
        for e1 in os_cache:
            for e2 in res:
                if e1['rsn'] == e2['rsn']: pairs_found += [(e1, e2)]
        for es in pairs_found:
            os_cache.remove(es[0])
            os_cache.append(es[1])
            res.remove(es[1])
        __save_cache__(os_cache, False)
    if ir_cache is not None:
        pairs_found = []
        for e1 in ir_cache:
            for e2 in res:
                if e1['rsn'] == e2['rsn']: pairs_found += [(e1, e2)]
        for es in pairs_found:
            ir_cache.remove(es[0])
            ir_cache.append(es[1])
            res.remove(es[1])
        __save_cache__(ir_cache, True)
    return res

