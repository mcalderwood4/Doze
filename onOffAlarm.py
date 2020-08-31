import RPi.GPIO as GPIO
from flask import Flask, render_template, request
from alarm import Alarm
import time
from flask_apscheduler import APScheduler
import threading
import pygame

app = Flask(__name__)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# initiate array to store alarms
lrms = []
# initiate array to store sorted list of alarms
sortLrms= []
sortLrms.sort(key=lambda x: int(str(x.hour) + "" + str(x.minute)))
jobcount = 1

# takes user to main screen
@app.route("/")
def main():
    templateData = {
        'alarms': sortLrms
    }
    return render_template('main.html', **templateData)


# executes when user clicks "turn off" or "turn on" for an alarm
@app.route("/<alarmName>/<action>")
def action(alarmName, action):
    # If the action part of the URL is "on," execute the code below:
    if action == "on":
        # find alarm in the array and set on equal to True, change words to read "turn off"
        for a in lrms:
            if a.name == alarmName:
                a.on = True
                a.turn_on()

    # If the action part of the URL is "off," execute the code below:
    if action == "off":
        # find alarm in the array and set on equal to False, change words to read "turn on"
        for a in lrms:
            if a.name == alarmName:
                a.on = False
                a.turn_off()

    # update data in sorted array
    templateData = {
        'alarms': sortLrms
    }

    # refresh main screen with updated alarm list
    return render_template('main.html', **templateData)


# creates new alarm from form on newAlarm.html
@app.route('/result', methods=['POST', 'GET'])
def result():
    global jobcount
    if request.method == 'POST':
        result = request.form
        nameA = result.get('name')
        #check if user left alarm name blank, defaults to "Alarm"
        if nameA == "":
            nameA = "Alarm"
        ampm = result.get('amPM')
        hourA = str(result.get('hour'))
        minuteA = str(result.get('minute'))
        scent = 'scent' in result
        light = 'light' in result
        sound = result.get('sound')
        if sound == 'none':
            sound_on = False
        else:
            sound_on = True
        # creates new alarm record
        alrm = Alarm(nameA, hourA, minuteA, True, scent, light, sound_on, sound, ampm, jobcount)
        # add to array
        lrms.append(alrm)
        # add to sorted array and resort in chronological order
        sortLrms.append(alrm)
        sortLrms.sort(key=lambda x: int(str(x.hour) + "" + str(x.minute)))
        #update templateData
        templateData = {
            'alarms': sortLrms
        }
        # add new alarm to scheduler
        app.apscheduler.add_job(func=lrms_go, trigger='date', args=[jobcount], id=str(jobcount))
        jobcount += 1
    # refresh page with update alarm list
    return render_template('main.html', **templateData)


@app.route("/<alarmName>/delete")
def delete(alarmName):
   #remove alarm from lrms array and the sorted list
    for al in lrms:
        if al.name == alarmName:
            lrms.remove(al)
    for sa in sortLrms:
        if sa.name == alarmName:
            sortLrms.remove(sa)
    #update templateData
    templateData = {
        'alarms': sortLrms
    }
    # refresh page with update alarm list
    return render_template('main.html', **templateData)

# takes user to form to create a new alarm
@app.route('/addAlarm')
def add_alarm():
    return render_template('newAlarm.html')


# takes user to list of current alarms
@app.route('/to_alarms')
def to_alarms():
    templateData = {
        'alarms': sortLrms
    }
    return render_template('main.html', **templateData)

# takes user to info page
@app.route('/to_info')
def to_info():
    return render_template('info.html')

# when alarm alerts, loads page to turn alarm off
@app.route('/running')
def running():
    return render_template('runAlarm.html')


@app.route('/go_light')
def go_light():
    light()
    templateData = {
        'alarms': sortLrms
    }
    return render_template('main.html', **templateData)


@app.route('/to_account')
def to_account():
    return render_template('account.html')


@app.route('/to_settings')
def to_settings():
    return render_template('settings.html')


@app.route('/home')
def home():
    return render_template('menu.html')

# when user turns off running alarm, stop music and reset lights, go back to main screen
@app.route('/turn_off_alarm')
def off_alarm():
    GPIO.cleanup
    pygame.mixer.music.stop()
    return render_template('main.html')

# checks for active alarms in the scheduler
def lrms_go(task_id):
    task_id = int(task_id)
    for a in lrms:
        if a.idNum == task_id:
                if a.on:
                    alarm_time = a.alarm_time()
                    while True:
                        # runs alarm functions once current time equals the alarm time
                        cur_time = time.strftime("%H%M")
                        if cur_time == alarm_time:
                            a.go()
                            a.turn_off()
                            break


def go_page(a):
    lrmName = a.name
    return render_template("runAlarm.html", **lrmName)


def scheduled_task(task_id):
    for i in range(10):
        time.sleep(1)
        print('Task {} running iteration {}'.format(task_id, i))

if __name__ == '__main__':
    app.run(debug=True)


