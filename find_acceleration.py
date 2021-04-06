import pandas as pd
import requests
import socket
import os
import datetime as dt
import time
import math

#Functions to print in terminal as a different color. Not important
def prRed(skk): return "\033[91m {}\033[00m" .format(skk)
def prGreen(skk): return "\033[92m {}\033[00m" .format(skk)
def prYellow(skk): return "\033[93m {}\033[00m" .format(skk)
def prLightPurple(skk): return "\033[94m {}\033[00m" .format(skk)
def prPurple(skk): return "\033[95m {}\033[00m" .format(skk)
def prCyan(skk): return "\033[96m {}\033[00m" .format(skk)
def prLightGray(skk): return "\033[97m {}\033[00m" .format(skk)
def prBlack(skk): return "\033[98m {}\033[00m" .format(skk)

#Constants
CSV_NAME = 'India.csv'
URL_FOR_INDIA_CSV = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/country_data/India.csv'
POPULATION_50 = 500000000
POPULATION_70 = 700000000
POPULATION_100 = 1000000000

def printPercentage(percentage):
    percentage = float(percentage)
    if (percentage >=0):
        return prGreen("increased by " + "{:,.2f}".format(percentage)+'%')
    return prRed("decreased by " + "{:,.2f}".format(percentage)+'%')

# Check if there is internet connection
def is_connected():
    try:
        socket.create_connection(("1.1.1.1", 53))
        return True
    except OSError:
        pass
    return False

#Check if file was fetched today. Then no need to fetch it again today
def is_file_fetched_today():
    today = dt.datetime.now().date()
    try:
        filetime = dt.datetime.fromtimestamp(
                os.path.getmtime(CSV_NAME))
    except:
        return False
    if filetime.date() == today:
        return True
    return False

start_time = time.time()

# Check if internet is connected and if file was fetched today
if(not is_connected()): exit()
if (not is_file_fetched_today()):
    r = requests.get(URL_FOR_INDIA_CSV,allow_redirects=True)
    open(CSV_NAME, 'wb').write(r.content)
df = pd.read_csv(CSV_NAME, parse_dates=['date'])

#   Creating extra columns for computation - Main Logic
df['vaccine_administered'] = df['people_vaccinated'] -df['people_vaccinated'].shift(1)
first_day = df.iloc[0]['date']
df['avg_vaccinations_per_day'] = df['vaccine_administered'].rolling(window=2).mean()
df['vaccination_rate_acceleration'] = ((df['avg_vaccinations_per_day'] -df['avg_vaccinations_per_day'].shift(1))*100 / df['avg_vaccinations_per_day']).round(2) 

last_row = df.iloc[-1]

# Calulated variables 
vaccination_rate_acceleration = last_row['vaccination_rate_acceleration']
last_date = last_row['date']
avg_vaccinations_per_day = last_row['avg_vaccinations_per_day']
vaccine_administered = last_row['vaccine_administered']
people_vaccinated = last_row['people_vaccinated']
mean_vaccination_rate_acceleration = df['vaccination_rate_acceleration'].mean()

## Calculating days remaining using equations of motion 

#v2=u2+2as
#v=u+at
def calculate_days_remaining(population,acceleration,initial_velocity):
    people_remaining = population - last_row['people_vaccinated']
    final_velocity_squared = 2*acceleration*people_remaining + initial_velocity*initial_velocity
    final_velocity = math.sqrt(final_velocity_squared)
    days_needed = (final_velocity - initial_velocity) / acceleration
    return days_needed

days_50 = calculate_days_remaining(POPULATION_50,mean_vaccination_rate_acceleration,avg_vaccinations_per_day)
days_70 = calculate_days_remaining(POPULATION_70,mean_vaccination_rate_acceleration,avg_vaccinations_per_day)
days_100 = calculate_days_remaining(POPULATION_100,mean_vaccination_rate_acceleration,avg_vaccinations_per_day)

##  Uncomment line below if you want to see the changes in a csv file
df.to_csv('India_altered.csv')

## Printing the data in a clean way

print("\n\n\n******************************************************************************* \n\n")
print("\t\tVaccination rate"+printPercentage("{:,.2f}".format(vaccination_rate_acceleration)))
print("\t\tVaccinations per day :"+prYellow("{:,.2f}".format(avg_vaccinations_per_day)))
print("\t\tPeople vaccinated on "+last_date.strftime('%d %B, %Y')+" : "+ "{:,.0f}".format(vaccine_administered))
print("\t\tTotal vaccinated : "+ "{:,}".format(people_vaccinated))
print("\t\tAcceleration mean : "+ prYellow("{:,.2f}".format(mean_vaccination_rate_acceleration)+"%"))
print("\t\tEstimated days for vaccinating 50% : "+ prYellow("{:,.2f}".format(days_50) +" (" +"{:,.2f}".format(days_50/30) + " months)"))
print("\t\tEstimated days for vaccinating 70% : "+ prYellow("{:,.2f}".format(days_70) +" (" +"{:,.2f}".format(days_70/30) + " months)"))
print("\t\tEstimated days for vaccinating 100% : "+ prYellow("{:,.2f}".format(days_100) +" (" +"{:,.2f}".format(days_100/30) + " months)"))
print("\n\n\n******************************************************************************* \n\n")
print('\n\nTime taken : '+"{:,.3f}".format(time.time()-start_time)+' seconds')
