from flask import Flask, render_template, request, send_file, g
from waitress import serve
import time, os
import csv

def format(text):
    text = text.replace(" ", "").lower()
    return text

def gettimestamp():
    return round(time.time())

def timestamptostring(ts):
    lts = time.localtime(ts)
    h = lts.tm_hour 
    m = lts.tm_min
    s = lts.tm_sec
    return f"{h:02d}:{m:02d}:{s:02d}"

def tostring(list):
    s = ''
    for elem in list:
        s+=str(elem)+';'
    s=s[:-1]
    s+='\n'
    return s

def numberize(text):
    try:
        return int(text)
    except:
        return 0

def readit(file_path):
    f = open(file_path, encoding = 'utf-8')
    r = csv.reader(f, delimiter=';')
    lines = []
    for line in r:
        lines.append(line)
    return lines

def getteamsdata(lines):
    teams = {}
    for line in lines:
        if len(line) == 2:
            name = format(line[0])
            uid = format(line[1])
            team = Team(name, uid)
            teams[uid] = team
    return teams

def gethintdata(lines):
    stages = {}
    for line in lines:
        stage_id = numberize(line[0])
        code = format(line[1])
        hints = []
        for i in range(2, len(line)-1):
            if i%2 == 0:
                hint_text = line[i]
                hint_time = numberize(line[i+1])
                hint = {"text": hint_text, "time": hint_time}
                if hint["text"] != "":
                    hints.append(hint)
        if stage_id != 0:
            stages[str(stage_id)] = {"code": code, "hints": hints}
    return stages

class Team():
    def __init__(self, name, uid):
        self.name = name
        self.uid = uid
        self.level = 0
        self.stats = {}

class GlobalVariables():
    def __init__(self):
        self.teams = getteamsdata(readit("./data/teams.csv"))
        self.uids = list(self.teams.keys())
        self.stages = gethintdata(readit("./data/hints.csv"))
        self.admcode = 'lucienjeborec'  

gv = GlobalVariables()

def gettn(uid):
    return gv.teams[uid].name


def get_hint_string(uid):
    try:
        level = gv.teams[uid].level
        stringlevel = str(level)
        timeonlevel = gv.teams[uid].stats[stringlevel]
        timenow = gettimestamp()
        timewait = timenow - timeonlevel

        #how many hints should they get
        hints = gv.stages[stringlevel]["hints"]
        hintstext = ""

        if len(hints) < 1:
            return ("No hints. Try entering code first.", False)

        for i in range (len(hints)):
            if timewait > hints[i]['time']:
                timewait -= hints[i]['time']
                hinttext = hints[i]['text']
                hintstext += f"{i+1}. nápověda: \n {hinttext} \n \n"
            else:
                missingtime = hints[i]['time'] - timewait
                nexthinttime = timenow + missingtime
                stringtime = timestamptostring(nexthinttime)
                hintstext += f"{i+1}. nápověda: \n Dostaneš ji v {stringtime}"
                break
        return (hintstext, True)
    except:
        return ("No hints. Try entering code first.", False)

app = Flask(__name__)
@app.route('/')
@app.route('/index')
def get_login_page():
    return render_template('index.html', msg='', msgcolor='neut')

@app.route('/main')
def get_main_page():
    uid = format(request.args.get('tname'))
    if uid == gv.admcode:
        return render_template('admin.html', msg='Logged into admin menu.', msgcolor='pos')
    elif uid in gv.uids:
        return render_template('main.html', msg='Successful login.', msgcolor='pos', tn=gettn(uid))   
    else:
        return render_template('index.html', msg='Wrong team ID.', msgcolor='neg')

@app.route('/entered')
def entered():
    code = format(request.args.get('code'))
    uid = format(request.args.get('tname'))
    if uid in gv.uids:
        for stageid in gv.stages.keys():
            stage = gv.stages[stageid]
            stagecode = stage['code']
            if code == stagecode:
                levelid = int(stageid)
                gv.teams[uid].level = levelid
                if levelid < 0:
                    (hintstring, status) = get_hint_string(uid)
                    color = 'neg'
                    if status: color = 'pos'
                    return render_template('main.html', msg='Success! \n \n' + hintstring, msgcolor=color, tn=gettn(uid))
                elif not (stageid in gv.teams[uid].stats.keys()):
                    gv.teams[uid].stats[stageid] = gettimestamp()
                    (hintstring, status) = get_hint_string(uid)
                    color = 'neg'
                    if status: color = 'pos'
                    return render_template('main.html', msg='Success! \n \n' + hintstring, msgcolor=color, tn=gettn(uid)) 
                else:
                    return render_template('main.html', msg='Code already entered', msgcolor='neg', tn=gettn(uid)) 
        return render_template("main.html", msg="Code not found.", msgcolor='neg', tn=gettn(uid))          
    else:
        return render_template("main.html", msg="Team not found.", msgcolor='neg', tn="")

@app.route('/get-hint')
def get_hint():
    try:    
        uid = format(request.args.get('tname'))
        (hintstring, status) = get_hint_string(uid)
        color = 'neg'
        if status: color = 'neut'
        return render_template('main.html', msg=f'\n \n {hintstring}', msgcolor=color, tn=gettn(uid))
    except:
        try:
            uid = format(request.args.get('tname'))
            return render_template('main.html', msg='', msgcolor='neut', tn=gettn(uid))
        except:
            return render_template('main.html', msg='Invalid teamname.', msgcolor='neg', tn=gettn(uid))

@app.route('/get-stats')
def get_stats():
    adminid = format(request.args.get('tname'))
    if adminid == gv.admcode:
        f = open('./temp.csv', 'w', encoding='utf-8')
        firstline = ['name']
        for stageid in gv.stages.keys():
            if int(stageid) > 0:
                firstline.append(stageid)
        f.write(tostring(firstline))
        for uid in gv.teams.keys():
            name = gv.teams[uid].name
            line = [name]
            for key in firstline[1:]:
                if key in gv.teams[uid].stats.keys():
                    line.append(timestamptostring(gv.teams[uid].stats[key]))
                else:
                    line.append('-')
            f.write(tostring(line))
        f.close()
        return send_file('./temp.csv', mimetype='text/csv', as_attachment=True, download_name='stats.csv')          
    else:
        return render_template('index.html', msg='You have no power here.', msgcolor = 'neg')

@app.route('/reset-game')
def reset_game():
    uid = format(request.args.get('tname'))
    if uid == gv.admcode:
        resetuid = format(request.args.get('rname'))
        if resetuid in gv.uids:
            gv.teams[resetuid].stats = {}
            gv.teams[resetuid].level = 0
            return render_template('admin.html', msg=f'Team {gv.teams[resetuid].name} reseted.', msgcolor='pos')
        else:
            return render_template('admin.html', msg=f'Team id not found.', msgcolor='neg')
    else:
        return render_template('index.html', msg='You have no power here.', msgcolor = 'neg')

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8080)