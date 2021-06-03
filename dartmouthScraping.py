from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import csv
import sys

# Data object to hold each individual result
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

# Data object to hold each athlete with an array of results 
class Athlete:
    def __init__(self, name):
        self.__name = name.replace(',','')
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

def athleteNotSearched(name, athletes):
    for athlete in athletes:
        if athlete.getName() == name:
            return False 
    return True 
# Setup selenium driver using chrome
DRIVER_PATH = '/usr/local/bin/chromedriver'
driver = webdriver.Chrome(executable_path=DRIVER_PATH)

# pages = ['https://www.tfrrs.org/teams/NH_college_m_Dartmouth.html']
# IMPORTANT: uncomment/comment below to swap between men and women's result scraping

driver.get('https://www.tfrrs.org/teams/NH_college_f_Dartmouth.html')
# driver.get('https://www.tfrrs.org/teams/NH_college_m_Dartmouth.html')
selectors = ['[text="2019 Outdoor"]', '[text="2018 Outdoor"]', '[text="2017 NCAA Outdoor"]']

athletes = []
for selector in selectors:
    driver.switch_to.window(driver.window_handles[0])
    select = WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.TAG_NAME, 'select')))
    actions = ActionChains(driver)
    actions.move_to_element(select).perform()
    # select = driver.find_elements(By.TAG_NAME, 'select')[0]
    select.click()
    outdoorOption = select.find_elements(By.CSS_SELECTOR, selector)[0]
    outdoorOption.click()

    # actionBuilder = ActionChains(driver);
    #  = actionBuilder.click(select);
    # openLinkInNewTab.perform();

    # Once we have navigated to the team page, pull all of the tables on the page 
    all_tables = driver.find_elements(By.TAG_NAME, 'table')
    # The second table in our array is our team results
    teamResults = all_tables[1]
    # Pull out all of the links in the team results table, these will be our athlete names
    # as well as our links to each athlete's individual results
    links = teamResults.find_elements(By.TAG_NAME, 'a')
    # links = links[:3]

    for link in links:
        # make sure we are in the team homepage tab when we start each iteration
        driver.switch_to.window(driver.window_handles[0])
        # create a new athlete object with the text from the link (i.e their name)
        # Note: the constructor parses out the ',' to prevent malformating in the csv
        if athleteNotSearched(link.text.replace(',',''), athletes):
            athlete = Athlete(link.text)
            # open the link to the athlete's results in a new tab
            builder = ActionChains(driver);
            openLinkInNewTab = builder.key_down(Keys.COMMAND).click(link).key_up(Keys.COMMAND);
            openLinkInNewTab.perform();
            # switch to the newly opened tab
            driver.switch_to.window(driver.window_handles[1])

            # navigate to the list of the specific athlete's results 
            athleteResults = driver.find_element(By.CSS_SELECTOR, '#meet-results')
            # collect all of the meets, each meet is its own table
            meets = athleteResults.find_elements(By.TAG_NAME, 'table')
            for meet in meets:
                # Get the title and date of the meet
                header = meet.find_element(By.TAG_NAME, 'thead')
                meetTitle = header.find_element(By.TAG_NAME, 'a').text
                meetDate = header.find_element(By.TAG_NAME, 'span').text
                if ('2017' in meetDate) or ('2018' in meetDate) or  ('2019' in meetDate):
                    # the body of the table contains the rows of events
                    body = meet.find_element(By.TAG_NAME, 'tbody')
                    events = body.find_elements(By.TAG_NAME, 'tr')
                    for event in events:
                        data = event.find_elements(By.TAG_NAME, 'td')
                        # each row is split into 3 data parts, event name, time, and placement
                        eventName = data[0].text
                        eventTime = data[1].find_element(By.TAG_NAME, 'a').text.replace(',','')
                        eventPlacement = data[2].text

                        # create a new result with the scraped info and add it to the athlete's array of results
                        resultObject = Result(eventName, eventTime, meetDate, meetTitle, eventPlacement) 
                        athlete.addResult(resultObject)
            # Add our athlete to the array of athletes after we have iterated through all of their races
            athletes.append(athlete)
            driver.close()

# Check sys arguments to decide where to write our data to 
outputLocation = 'results.csv'
if len(sys.argv) > 1:
    outputLocation = sys.argv[1]
print(f'Output Location is set to: {outputLocation}')

#Create the csv file to write to
with open(outputLocation, 'x') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    # These are our column headers
    filewriter.writerow(['Athlete', 'Event', 'Time', 'Placement', 'Meet', 'Date'])
    # Iterate through each athlete and build one row for each result
    for athlete in athletes:
        name = athlete.getName()
        for result in athlete.getResults():
            row = []
            row.append(name)
            row = row + result.getArrayForm()
            # Write to our csv file with the current row
            filewriter.writerow(row)
