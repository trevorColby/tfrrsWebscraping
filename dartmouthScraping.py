from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import csv
import sys

class Result:
    def __init__(self, event, time , date, meet, placement):
        self.__event = event
        self.__time = time
        self.__date = date.replace(',',' ').replace('|',' ')
        self.__meet = meet.replace(',',' ').replace('|',' ')
        self.__placement = placement
    def getArrayForm(self): 
        return [f'{self.__event}', f'{self.__time}', f'{self.__placement}', f'{self.__meet}', f'{self.__date[3:]}']
    def __repr__(self):
        return f'{self.__event}, {self.__time}, {self.__placement}, {self.__date[3:]}, {self.__meet}\n'

    def __str__(self):
        return f'{self.__event}, {self.__time}, {self.__placement}, {self.__date[3:]}, {self.__meet}\n'


class Athlete:
    def __init__(self, name):
        self.__name = name
        self.__results = []

    def getName(self):
        return self.__name

    def getResults(self):
        return self.__results

    def addResult(self, result):
        self.__results.append(result)

    def __repr__(self):
        athleteString = "\n" + self.__name + ":\n"
        for result in self.__results:
            athleteString = athleteString + repr(result)
        return athleteString

    def __str__(self):
        athleteString = "\n" + self.__name + ":\n"
        for result in self.__results:
            athleteString = athleteString + result
        return athleteString

outputLocation = 'results.csv'
if len(sys.argv) > 1:
    outputLocation = sys.argv[1]
 
DRIVER_PATH = '/usr/local/bin/chromedriver'
driver = webdriver.Chrome(executable_path=DRIVER_PATH)
# driver.get('https://www.tfrrs.org/teams/NH_college_m_Dartmouth.html')
driver.get('https://www.tfrrs.org/teams/NH_college_f_Dartmouth.html')

all_tables = driver.find_elements(By.TAG_NAME, 'table')
teamResults = all_tables[1]
athletes = []
links = teamResults.find_elements(By.TAG_NAME, 'a')
for link in links:
    driver.switch_to.window(driver.window_handles[0])
    athlete = Athlete(link.text.replace(',',''))
    builder = ActionChains(driver);
    openLinkInNewTab = builder.key_down(Keys.COMMAND).click(link).key_up(Keys.COMMAND);
    openLinkInNewTab.perform();
    driver.switch_to.window(driver.window_handles[1])


    athleteResults = driver.find_element(By.CSS_SELECTOR, '#meet-results')
    meets = athleteResults.find_elements(By.TAG_NAME, 'table')
    for meet in meets:
        # Get the title and date of the meet
        header = meet.find_element(By.TAG_NAME, 'thead')
        meetTitle = header.find_element(By.TAG_NAME, 'a').text
        meetDate = header.find_element(By.TAG_NAME, 'span').text
        
        body = meet.find_element(By.TAG_NAME, 'tbody')
        events = body.find_elements(By.TAG_NAME, 'tr')
        for event in events:
            data = event.find_elements(By.TAG_NAME, 'td')
            eventName = data[0].text
            eventTime = data[1].find_element(By.TAG_NAME, 'a').text
            eventPlacement = data[2].text
            resultObject = Result(eventName, eventTime, meetDate, meetTitle, eventPlacement) 
            athlete.addResult(resultObject)
    athletes.append(athlete)
    driver.close()

print(f'Output Location is set to: {outputLocation}')
with open(outputLocation, 'x') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    filewriter.writerow(['Athlete', 'Event', 'Time', 'Placement', 'Meet', 'Date'])
    for athlete in athletes:
        name = athlete.getName()
        for result in athlete.getResults():
            row = []
            row.append(name)
            row = row + result.getArrayForm()
            filewriter.writerow(row)
