#!/usr/bin/env -S conda run -n workload python

import argparse
import yaml 
import sys, os
import datetime
import requests
from bs4 import BeautifulSoup
import re

month_length = {"1": 31, "3":31, "4":30, "5":31, "6":30, "7":31, "8":31, "9":30, "10":31, "11":30, "12":31}
month_name={1: "January", 2: "February", 3: "March", 4: "April", 5:"May", 6:"June", 7:"July", 8:"August", 9:"September", 10:"October", 11:"November", 12:"December"}

def get_info_from_yaml(info): #extract information from yaml file
    path = sys.argv[0][:-11]
    with open (path+'config.yaml', 'r') as c:                    
        p=yaml.safe_load(c)
        return p[info]

def translate_current_time(unit, time=datetime.datetime.today()):
    if unit=="h":
        return time.hour
    elif unit=="min":
        return str(time.minute)
    elif unit=="d":
        return str(time.day)
    elif unit=="mo":
        return str(time.month)
    elif unit == "y":
        return str(time.year)
    elif unit=="wd": 
        return int(time.isocalendar()[2]-1)
    elif unit=="week":
        return int(time.isocalendar()[1])
    elif unit=="date":
        return str(time.date())
    elif unit=="time":
        return str(time.hour)+":"+str(time.minute)

def get_current_task(folder, filename=False): # get running task
    for f in os.listdir(folder):
        if "helper" in f:
            name_task=str(f).split("_")[1]
            if filename:
                return folder+"/"+f, name_task
            else:
                return name_task
    else:
        raise FileNotFoundError("There is no current task!")

def get_hours_spent(start, end=get_info_from_yaml("goal"), printing=False):
    # calculate difference between two amounts of time, negtive time is goal is exceeded
    FM = "%H:%M"
    tdelta = datetime.datetime.strptime(end, FM)-datetime.datetime.strptime(start, FM)
    if tdelta.days < 0: #in case end is bigger than start
        tdelta = datetime.timedelta(
            days=0,
            seconds=tdelta.seconds,
            microseconds=tdelta.microseconds
        )
    return str(tdelta)

def start(task): #starting the time measuring y creating a helpfer file and writing start time to specific task file
    folder=get_info_from_yaml("folder")
    try:
        try: # to guarantee only on task
            task = get_current_task(folder)
            if task:
                raise FileExistsError
        except FileNotFoundError:
            pass
        helper = open(folder+"/.helper_"+task, 'x')
        with open(folder+"/tasks/"+task, 'a') as f:
            f.write(translate_current_time("date")+","+translate_current_time("time")+","+translate_current_time("time")+",0:0\n")
            print("Task", task, "started at", translate_current_time("time"), "o'clock.")
    except FileExistsError:
        print("Something went awfully wrong! You can't start a new task if you're already doing one! Keep focused, no multi-tasking!")
        task = get_current_task(folder)
        print("You seem to currently work on the following task:", task)

def end(): #end current task and write spent time in task file
    folder=get_info_from_yaml("folder")
    try: #check if there is a task running
        current_task, name= get_current_task(folder, True)
        os.remove(current_task)
    except FileNotFoundError:
        print("There is no task you could possibly end! Maybe you should start working before quitting.")
        exit()
    try:
        with open(folder+"/tasks/"+name, 'r') as f: #get information about running task
            lines=f.readlines()
        entry=lines[-1].split(",")
        
        if get_hours_spent(end=translate_current_time("time"), start=entry[1])[:-3] == "0:00": #check for tasks that are stopped immediately
            raise ValueError

        with open(folder+"/tasks/"+name, 'w') as f: #write new information
            for line in lines[:-1]:
                f.write(line)
            f.write(entry[0]+","+entry[1]+","+translate_current_time("time")+","+get_hours_spent(end=translate_current_time("time"), start=entry[1])[:-3]+"\n")
        
        print("Task", name, "finished at", translate_current_time("time"), "o'clock.")
        print("You spent:", get_hours_spent(end=translate_current_time("time"), start=entry[1])[:-3], "hours with the task.")
    
    except ValueError: # don't count if time less than a minute, error thrown by function
        print("Less than a minute? We won't count that, will we?")
        with open(folder+"/tasks/"+name, 'r') as f:
            lines=f.readlines()
        with open(folder+"/tasks/"+name, 'w') as f:
            for line in lines[:-1]:
                f.write(line)

def get_hours_day(date=translate_current_time("date"), printing=False):
    tasks = get_info_from_yaml("acronyms")
    hours="0:0"
    if printing:
        print("Date: ", date,"\n")

    for task in tasks:
        try:
            hours_task = get_hours_task_day(task=task, date=date)
            hours=add_hours(hours, hours_task)
            if printing:
                print("\t"+task.upper()+"\t"+hours_task)
        except FileNotFoundError:
            continue
        
    if printing:
        print("\nHours Total:", hours)

    return hours

def add_hours(h1, h2):
    h1 = h1.split(":")
    h2 = h2.split(":")
    
    hour=0
    minute=int(h1[1])+int(h2[1])
    
    while minute>59:
        hour+=1
        minute-=60

    hour+=int(h1[0])+int(h2[0])

    return str(hour)+":"+str(minute)

def get_hours_task_day(task, date=translate_current_time("date")):
    folder = get_info_from_yaml("folder")
    result="0:0"
    with open(folder+"/tasks/"+task, "r") as taskHours:
        lines = taskHours.readlines()
        for line in lines:
            line = line.split(",")
            if line[0] == date:
                if line[3][:-1] == "0:0": #last line if task is current
                    if task == get_current_task(folder):
                        done = get_hours_spent(end=translate_current_time("time"), start=line[1])[:-3]
                        result=add_hours(h1=result, h2=done)
                else:
                    result = add_hours(h1=result, h2=line[3])
    return result

def get_hours_week(week=translate_current_time("week"), printing=False):
    total="0:0"
    weekdays = get_dates_from_weeknumber(week)
    if printing:
        print("Week:", weekdays[0], "to", weekdays[-1], "\n")
    for day in weekdays:
        hours_day = get_hours_day(day, False)
        
        if printing:
            print("\t", day, "", hours_day)

        total=add_hours(total,  hours_day)
    
    if printing:
        print("\nHours Total:", total)

    return total

def get_hours_month(month=translate_current_time("mo"), year=translate_current_time("y"), printing=False):
    total = "0:0"
    if month in ["2", 2]: # get length of month
        if int(year)  % 4 == 0:
            length=29
        else:
            length=28
    else:
        length = month_length[str(month)]
    if int(month) < 10:
        month = "0"+str(month)
    else:
        month = str(month)

    if printing:
        print("Month:", month)
        print("Only Dates are shown that show some sign of work.")
        print()

    for i in range(length):
        if i+1 < 10:
            day = "0"+str(i+1)
        else:
            day = str(i+1)
        day_hours = get_hours_day(year+"-"+month+"-"+day)
        total=add_hours(total, day_hours)
        if printing:
            if int(day_hours.split(":")[0]) > 0 or int(day_hours.split(":")[1]) > 0:
                print("\t", year+"-"+month+"-"+day, "", day_hours)

    if printing:
        print()
        print("Hours Total:", total)
    return total

def get_hours_year(year=translate_current_time("y"), printing=False):
    total = "0:0"
    if printing:
        print("Year:", year)
        print("Only Dates are shown that show some sign of work.\n")
    for month in range(12):
        hours = get_hours_month(month+1, year, False)
        total=add_hours(total, hours)
        if printing:
            if int(hours.split(":")[0]) >0 or int(hours.split(":")[1]) >0:
                print("\t",month_name[int(month+1)], hours)

    if printing:
        print("\nHours Total:",total)

def get_dates_from_weeknumber(week=translate_current_time("week"), year=translate_current_time("y")): # calculates the dates given a week
    # get html of kalenderwoche-website
    url= 'https://www.aktuelle-kalenderwoche.org/kalenderwochen/{}'.format(str(year))
    res= requests.get(url)
    html= res.content
    soup = str(BeautifulSoup(html, 'html.parser'))
    
    # find entry for week
    html_regex = '<td><a href="https://www.aktuelle-kalenderwoche.org/'+str(year)+'/'+str(week)+'">'+str(week)+'</a></td>(.*\n){8}'
    html_m = re.search(html_regex, soup)
    html_days = html_m.group(0).split("\n")
    
    # transform in friendly format
    week_days=[]
    for elem in html_days[1:-1]:
        date_rough = elem.split(">")[1].split("<")[0].split(".")
        week_days.append(str(year)+"-"+date_rough[1]+"-"+date_rough[0])
    
    return week_days


def print_goal(goal=get_info_from_yaml("goal")):
    spent=get_hours_day()
    print("Your goal are\t", goal, "hours")
    print("Already Done\t", spent, "hours")
    if int(goal.split(":")[0]) < int(spent.split(":")[0]):
        print("Still to do\t", "-"+get_hours_spent(goal, spent)[:-3], "hours")
    else:
        print("Still to do\t", get_hours_spent(spent, goal)[:-3], "hours")

parser = argparse.ArgumentParser(description='Simplistic Measurement for Working Time', prog="workload")
parser.add_argument('--version', '-v', action='version', version='%(prog)s v0.1')

subparsers = parser.add_subparsers()

subparser_start = subparsers.add_parser("start", help="Starting a Time Measurement")
subparser_start.add_argument("task", choices=get_info_from_yaml("acronyms"))

subparser_end = subparsers.add_parser("end", help="Ending a Time Measurement")
subparser_end.add_argument("end", default=True, action="store_true")

subparser_overview = subparsers.add_parser("overview", help="Getting an Overview over Spent Time")
subparser_overview.add_argument("o", choices=["day", "week", "month", "year", "goal"])
#subparser_overview.add_argument("-p", "--plot", help="Plotting the Time Management", action="store_true") another version

args = parser.parse_args()

if len(sys.argv) == 1:
    parser.print_help(sys.stderr)
    sys.exit(1)
elif len(sys.argv)==2:
    if args.end:
        end()
    else:
        parser.print_help(sys.stderr)
        sys.exit(1)
elif len(sys.argv)==3:
    try:
        if args.task:
            start(args.task)
    except AttributeError:
        if args.o:
            if args.o == "day":
                get_hours_day(printing=True)
            elif args.o == "week":
                get_hours_week(printing=True)
            elif args.o == "month":
                get_hours_month(printing=True)
            elif args.o == "year":
                get_hours_year(printing=True)
            elif args.o == "goal":
                print_goal()
            else:
                parser.print_help(sys.stderr)
                sys.exit(1)
else:
    parser.print_help(sys.stderr)
    sys.exit(1)