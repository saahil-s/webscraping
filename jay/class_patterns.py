#!/usr/local/bin/python3.9
import re

class class_patterns:
    def __init__(self):
        valid_patterns = [
                'NNN JOBS FOUND',
                'Showing 50 of NNN opportunities',
                'NNN open jobs',
                'NNN jobs',
                'NNN Jobs',
                'Displaying 1 to 20 of NNN matching jobs',
                'Showing 1 - 50 of NNN jobs',
                'Result ( s ) : NNN Showing 1 - 25',
                'NNN results',
                'NNN position ( s ) match this search',
                'Results 1 – 25 of NNN Page 1 of 3',
                '1 - 25 of NNN',
                'Job openings 1 - 10 of NNN',
                'Showing : 1 - 20 of NNN jobs',
                'NNN RESULTS',
                'Showing 12 out of NNN',
                'Showing 20 of NNN matches',
                'NNN Open Jobs',
                'NNN Results for',
                'NNN jobs found',
                'Showing 1 – 10 of NNN',
                'Jobs NNN',
                'NNN positions in all locations and teams',
                '1 – 10 of NNN',
                'Current Openings ( 10 of NNN )',
                'All Open Positions ( NNN )',
                'All position types ( NNN )',
                'Currently displaying NNN positions',
                '50 – 50 of NNN items',
                'NNN Items',
                'NNN Job Results',
                'NNN Jobs at Lennar',
                'NNN jobs available',
                'NNN live roles available',
                'NNN openings found',
                'NNN open jobs found',
                'NNN open positions',
                'NNN open position ( s )',
                'NNN Open Positions',
                'NNN Open Roles in 50 Locations',
                'NNN opportunities found',
                'NNN result ( s )',
                'NNN results for your search',
                'NNN Results found',
                'NNN Results found in all locations',
                'NNN Results Found in all locations',
                'NNN Roles',
                'NNN search results',
                'NNN Total Jobs',
                'Displaying 50 of NNN results',
                'Displaying NNN opportunities',
                'Found NNN jobs at Jazz Pharmaceuticals',
                'Found NNN Search Results',
                'Job results ( Showing 50 - 50 of NNN Jobs )',
                'Number of jobs which match your criteria : NNN',
                'OPEN POSITIONS : NNN',
                'Results ( 1–10 of NNN )',
                'Results : NNN',
                'Results ( 50 - 50 of NNN )',
                'Results 50 of NNN',
                'Search Results - NNN Jobs',
                'Search Results : NNN Jobs',
                'Search Results - NNN Jobs Found',
                'Showing 50 - 50 of NNN matching jobs',
                'Showing 50 - 50 of NNN result ( s )',
                'Showing 50 - 50 of NNN Results',
                'Showing NNN Job Results',
                'Showing 50 out of NNN open roles',
                'Showing 50 out of NNN results',
                'Showing NNN results',
                'Showing NNN Results',
                'Showing 50 to 50 of NNN jobs',
                'Showing jobs 50 to 50 of NNN',
                'Showing jobs 50 to 50 of NNN results',
                'Showing Results - NNN Job Results',
                'There are NNN Open Positions',
                'There are NNN open positions available',
                'Total Jobs : NNN',
                'View All Jobs NNN',
                'Viewing 50 – 50 of NNN Results',
                'Viewing NNN job results',
                'We found NNN job openings for you',
                'We found NNN jobs based on your',
                'We found NNN jobs that match your search',
                'Your search for careers matches NNN results',
                '50 - 50 of NNN Results',
                'NNN Jobs Found',
                'NNN Jobs matched your search',
                'NNN open roles',
                'Job Openings ( NNN jobs found )',
                'Number of Jobs : NNN',
                'Open Positions ( NNN )',
                'Positions Open NNN',
                'Showing 50 - 50 of NNN jobs sorted by Date',
                'Showing 50 to 50 of NNN entries',
                'NNN Jobs found',
                'NNN Search Results',
                '50 to 50 of NNN results',
                'We found NNN jobs',
                'Results 50 - 50 of NNN',
                'Search from over NNN opportunities',
                'Showing 50 - 50 of NNN',
                'NNN Results Found',
                'Positions Matched NNN',
                'NNN results found',
                'Displaying NNN positions',
                'Job Openings 50 - 50 of NNN',
                'Refine NNN results',
                'Showing 50 to 50 of NNN matching jobs',
                '50 - 50 of NNN results',
                'NNN Live Results',
                'Job Search Results ( NNN )',
                'Results 50 – 50 of NNN',
                'Displaying 50 - 50 of NNN in total',
                'Showing 50 to 50 of NNN Jobs',
                'Showing 50 - 50 of NNN results',
                'NNN Results',
                'Found NNN jobs at Addus HomeCare',
                'NNN roles across all departments in all locations',
                'Results ( NNN )',
                'Your job search results NNN results',
                'NNN Jobs at Marriott Vacations Worldwide',
                'Results ( 1 – 6 of NNN )',
                'Found NNN results',
                'Showing NNN Job Listings',
                'Results ( 1 – 6 of NNN )',
                'NNN jobs at Sonic Automotive',
                'NNN Jobs match the selections',
                'Below are NNN current open opportunities',
                'Showing 50 to 50 of NNN',
                'Found NNN Results',
                'NNN jobs in all locations and all teams',
                'NNN Job Listings',
                'Results ( NNN )',
                'Search results ( NNN jobs found )',
                'NNN open positions found',
                'Hoot! We found : NNN roles and 50 departments in 50 locations',
                'Current Openings - NNN',
                'NNN across all locations and teams',
                'NNN current job openings',
                'NNN found',
                'NNN Job Openings',
                'NNN jobs : All locations',
                'NNN jobs on 50 teams',
                '50 of NNN Job Opportunities',
                'NNN open positions across all offices and all teams',
                'NNN positions found matching your criteria',
                'NNN positions matching your criteria',
                'NNN roles in 50 countries',
                'NNN roles in 50 locations',
                'NNN Roles in 50 Locations',
                'NNN vacancies found',
                'Found NNN jobs at Papa Johns',
                'Found NNN jobs at UNFI',
                'Jobs : NNN',
                'Jobs 50 - 50 of NNN Found',
                'Results NNN',
                'Results : NNN jobs',
                'Showing 50 - 50 of3 NNN results',
                'Showing 50 - 50 of NNN Jobs',
                'Showing 50 – 50 of NNN Results',
                'Showing 50 - 50 of NNN Search Results',
                'Showing 50 to 50 of NNN Jobs Search results for "" Showing 50 to 50 of 50 Jobs Use the Tab key to navigate the Job List Select to view the full details of the job',
                'Total : NNN',
              ]
        valid_regexs = []
        for p in valid_patterns:
            p = p.split()
            p = '\s*'.join(['\d+' if re.fullmatch('\d+',v) else v.replace('(','\(').replace(')','\)') for v in p])
            p = p.replace('NNN','([0-9,]+)')
            p = f'^{p}$'
            valid_regexs.append(p)
        self.valid_regexs = valid_regexs

    def s2regex(self,p):
        #normalize patterns
        p = p.replace(':',' : ')
        p = p.replace('.',' ')
        p = p.replace('-',' - ')
        p = p.replace('(',' ( ')
        p = p.replace(')',' ) ')
        p = p.strip().replace('  ',' ')
        p = p.split()
        p = '\s*'.join(['\d+' if re.fullmatch('\d+',v) else v.replace('(','\(').replace(')','\)') for v in p])
        p = p.replace('NNN','([0-9,]+)')
        return p

    def get_regex(self,pattern):
        #normalize patterns
        pattern = pattern.replace('NNN','50')
        pattern = pattern.replace(':',' : ')
        pattern = pattern.replace('.',' ')
        pattern = pattern.replace('-',' - ')
        pattern = pattern.replace('(',' ( ')
        pattern = pattern.replace(')',' ) ')
        pattern = pattern.strip().replace('  ',' ')

        #find the matching regex
        for regex in self.valid_regexs:
            if re.fullmatch(regex,pattern):
                return regex[1:-1]
