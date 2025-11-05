from flask import Flask, render_template, request, g
from waitress import serve
import time, os
from helper import Helper

def format(text):
    text = text.replace(" ", "").lower()
    return text

def gettimeobj():
    zone = ZoneInfo("Europe/Prague")
    timeobj = datetime.now(zone)
    return timeobj

def tabletostring(headerline, lines):
    content = ''
    th = ''
    for elem in headerline:
        th += f'<th>{elem}</th>'
    content += f'<tr>{th}</tr>'    
    for row in lines:
        tr = ''
        for elem in row:
            tr += f'<td>{elem}</td>'
        content += f'<tr>{tr}</tr>'
    return f'<table id="restable">{content}</table>'

h = Helper()

class GlobalVariables():
    def __init__(self):
        storage = h.loaddata()
        for name, value in storage.items():
            setattr(self, name, value)
        
gv = GlobalVariables()

def gettn(uid):
    return gv.teams[uid].name


def get_hint_string(uid):
    try:
        level = gv.teams[uid].level
        stringlevel = str(level)
        timeonlevel = gv.teams[uid].stats[stringlevel]
        timenow = gettimeobj()
        timewait = (timenow - timeonlevel).total_seconds()

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
                nexthinttime = timenow + timedelta(seconds=missingtime)
                stringtime = nexthinttime.strftime("%H:%M:%S")
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
        return render_template('admin.html', msg='Info: Logged into admin menu.', msgcolor='pos')
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
                lastlevelid = gv.teams[uid].level
                if levelid < 0 and levelid == lastlevelid or levelid > 0 and stageid in gv.teams[uid].stats.keys():
                    return render_template('main.html', msg='Code already entered', msgcolor='neg', tn=gettn(uid))
                else:
                    gv.teams[uid].level = levelid
                    gv.teams[uid].stats[stageid] = gettimeobj()
                    (hintstring, status) = get_hint_string(uid)
                    color = 'neg'
                    if status: color = 'pos'
                    return render_template('main.html', msg='Success! \n \n' + hintstring, msgcolor=color, tn=gettn(uid))
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
        header = '<h2 id="tableheader">Results: \n </h2>'
        firstline = ['Team name']
        for stageid in gv.stages.keys():
            if int(stageid) > 0:
                firstline.append(stageid)
        lines = []
        for uid in gv.teams.keys():
            name = gv.teams[uid].name
            line = [name]
            for key in firstline[1:]:
                if key in gv.teams[uid].stats.keys():
                    timestring = gv.teams[uid].stats[key].strftime("%H:%M:%S")
                    line.append(timestring)
                else:
                    line.append('-')
            lines.append(line)
        stringtable = tabletostring(firstline, lines)
        return render_template('admin.html', msg=header + stringtable, msgcolor='neut')          
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
            return render_template('admin.html', msg=f'Info: Team {gv.teams[resetuid].name} reseted.', msgcolor='pos')
        else:
            return render_template('admin.html', msg=f'Info: Team id not found.', msgcolor='neg')
    else:
        return render_template('index.html', msg='You have no power here.', msgcolor = 'neg')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    serve(app, host="0.0.0.0", port=port)