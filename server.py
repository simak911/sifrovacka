from flask import Flask, render_template, request, send_file, g
from waitress import serve
import time, os

def gettimestamp():
    timestamp = 1745618400
    return round(time.time() - timestamp)

def tostring(list):
    s = ''
    for elem in list:
        s+=str(elem)+','
    s=s[:-1]
    s+='\n'
    return s

class GlobalVariables():
    def __init__(self):
        self.teams = {'t4e2s0t': Team('test','t4e2s0t')}
        self.uids = []
        self.codes = ["qhdxzrw","btrceym","znlkjwa","uxavqnp","jydltqe","wvhoskg","kapzirn","rsmvqtc","egdywlu",
                      "mhzbkxp","fnyjqwa","ldctugv","xqibsmr","tpvnehc","awjzkml","nevytqs"]
        self.startcodes = ["zqjrytd","mbtxpwa","lkhnzve","yufsdqm","cjwrbxt","gnovkle","xadumpi","qsryjzh","tmezlca",
                           "drkwiqn","vuxcpth","nlbqgye","eawmjuz","hipkxrn","kzlfbvo","sydqacm"]
        self.hintstimes = [
            [900, 1800, 2700],[900, 1980, 2880],[900, 1800, 2700],[1080, 1980, 2880],
            [1080, 1980, 2880],[900, 1980, 2880],[1080, 2160, 3060],[900, 2100, 3000],
            [1080, 2280, 3360],[900, 1800, 2700],[1080, 1980, 2880],[900, 1800, 2700],
            [900, 2100, 3000],[1200, 2400, 3300],[900, 2100, 3000],[1200, 2280, 3180]]
        self.levelcount = len(self.codes)
        self.admcode = 'a6d9m'  

class Team():
    def __init__(self, name, uid):
        self.name = name
        self.uid = uid
        self.level = -1
        self.stats = {}
        self.startlevel = -1
        self.isstarted = False
        self.isended = False

gv = GlobalVariables()
regteams = {}
f = open('./teams.txt','r', encoding='utf-8')
lines = f.readlines()
for line in lines:
    line = line.replace("\n","")
    line = line.replace(" ","")
    teaminfo = line.split(",")
    if len(teaminfo)==2: 
        regteams[teaminfo[1]] = teaminfo[0]
gv.uids = list(regteams.keys())
for uid in gv.uids:
    name = regteams[uid]
    team = Team(name, uid)
    gv.teams[uid] = team
gv.uids.append('t4e2s0t')

def gettn(uid):
    return gv.teams[uid].name

app = Flask(__name__)
@app.route('/')
@app.route('/index')
def get_login_page():
    return render_template('index.html', msg='', msgcolor='neut')

@app.route('/main')
def get_main_page():
    uid = request.args.get('tname').lower()
    if uid == gv.admcode:
        return render_template('admin.html', msg='Logged into admin menu.', msgcolor='pos')
    elif uid in gv.uids:
        return render_template('main.html', msg='Successful login.', msgcolor='pos', tn=gettn(uid))   
    else:
        return render_template('index.html', msg='Wrong team ID.', msgcolor='neg')


@app.route('/entered')
def entered():
    code = request.args.get('code').lower()
    uid = request.args.get('tname').lower()
    if uid in gv.uids:
        if code in gv.codes:
            if not gv.teams[uid].isstarted:
                return render_template('main.html', msg='Game not started yet.', msgcolor='neg', tn=gettn(uid)) 
            else:
                level = gv.codes.index(code)
                gv.teams[uid].level = level
                if level == gv.teams[uid].startlevel and not gv.teams[uid].isended:
                    gv.teams[uid].isended = True
                    gv.teams[uid].stats['e'] = gettimestamp() 
                    gv.teams[uid].stats['t'] = gv.teams[uid].stats['e'] - gv.teams[uid].stats['s']
                    return render_template('main.html', msg='Finish! Go to Jistota!', msgcolor='pos', tn=gettn(uid)) 
                else:
                    stringlevel = str(level)
                    if not (stringlevel in gv.teams[uid].stats.keys()):
                        gv.teams[uid].stats[stringlevel] = gettimestamp()                                
                    return render_template('main.html', msg='Success!', msgcolor='pos', tn=gettn(uid)) 
        elif code in gv.startcodes:
            if not gv.teams[uid].isstarted:
                gv.teams[uid].isstarted = True
                level = gv.startcodes.index(code)
                gv.teams[uid].level = level
                gv.teams[uid].startlevel = level
                stringlevel = str(level)
                gv.teams[uid].stats[stringlevel] = gettimestamp()
                gv.teams[uid].stats['s'] = gettimestamp()   
                return render_template('main.html', msg='Game started!', msgcolor='pos', tn=gettn(uid)) 
            else:
                return render_template('main.html', msg='Code not found.', msgcolor='neg', tn=gettn(uid))      
        else:
            return render_template("main.html", msg="Code not found.", msgcolor='neg', tn=gettn(uid))          
    else:
        return render_template("main.html", msg="Team not found.", msgcolor='neg', tn="")

@app.route('/get-img')
def get_image():
    try:    
        uid = request.args.get('tname').lower()
        level = gv.teams[uid].level
        if level > -1:
            return send_file(f'./imgs/s{level}.jpg', mimetype='image/jpeg')
        else:
            return send_file('./imgs/loadfail.jpg', mimetype='image/jpeg')
    except:
        return send_file('./imgs/loadfail.jpg', mimetype='image/jpeg')

@app.route('/get-hint')
def get_hint():
    try:    
        uid = request.args.get('tname').lower() 
        level = gv.teams[uid].level
        stringlevel = str(level)
        timeonlevel = gv.teams[uid].stats[stringlevel]
        timenow = gettimestamp()
        timewait = timenow - timeonlevel
        hinttimes = gv.hintstimes[level]
        hintnumber = 0
        if timewait>hinttimes[2]: hintnumber=3
        elif timewait>hinttimes[1]: hintnumber=2
        elif timewait>hinttimes[0]: hintnumber=1
        if level > -1:
            if hintnumber > 0:
                return send_file(f'./imgs/h{level}_{hintnumber}.jpg', mimetype='image/jpeg')
            else:
                return send_file('./imgs/wait.jpg', mimetype='image/jpeg')
        else:
            return send_file('./imgs/loadfail.jpg', mimetype='image/jpeg')
    except:
        return send_file('./imgs/loadfail.jpg', mimetype='image/jpeg')

@app.route('/get-hinttimes')
def get_hinttimes():  
    try: 
        uid = request.args.get('tname').lower() 
        level = gv.teams[uid].level
        stringlevel = str(level)
        timeonlevel = gv.teams[uid].stats[stringlevel]
        timenow = gettimestamp()
        timewait = timenow - timeonlevel
        hinttimes = gv.hintstimes[level]
        htime = 0
        hnumber = 0
        for i in range(3):
            if hinttimes[i] - timewait > 0:
                htime = hinttimes[i] - timewait
                hnumber = i+1
                break  
        return {'status': 'valid', 'htime': htime, 'hnumber': hnumber}
    except:
        return {'status': 'invalid'}

@app.route('/get-stats')
def get_stats():
    adminid = request.args.get('tname').lower()
    if adminid == gv.admcode:
        f = open('./temp.csv', 'w', encoding='utf-8')
        firstline = ['name','s']
        for i in range (gv.levelcount):
            firstline.append(str(i))
        firstline.append('e')
        firstline.append('t')
        f.write(tostring(firstline))
        for uid in gv.teams.keys():
            name = gv.teams[uid].name
            line = [name]
            for key in firstline[1:]:
                if key in gv.teams[uid].stats.keys():
                    line.append(str(gv.teams[uid].stats[key]))
                else:
                    line.append('-')
            f.write(tostring(line))
        f.close()
        return send_file('./temp.csv', mimetype='text/csv', as_attachment=True, download_name='stats.csv')          
    else:
        return render_template('index.html', msg='You have no power here.', msgcolor = 'neg')

@app.route('/reset-game')
def reset_game():
    uid = request.args.get('tname').lower()
    if uid == gv.admcode:
        resetuid = request.args.get('rname').lower()
        if resetuid in gv.uids:
            gv.teams[resetuid].stats = {}
            gv.teams[resetuid].startlevel = -1
            gv.teams[resetuid].level = -1
            gv.teams[resetuid].isstarted = False
            gv.teams[resetuid].isended = False
            return render_template('admin.html', msg=f'Team {gv.teams[resetuid].name} reseted.', msgcolor='pos')
        else:
            return render_template('admin.html', msg=f'Team id not found.', msgcolor='neg')
    else:
        return render_template('index.html', msg='You have no power here.', msgcolor = 'neg')

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)