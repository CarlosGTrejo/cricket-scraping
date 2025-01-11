import scrapy
from Cricket.items import MatchItem

class ScorecardSpider(scrapy.Spider):
    name = "scorecards"
    allowed_domains = ["www.espncricinfo.com"]
    start_urls = ["https://www.espncricinfo.com/records/list-of-match-results-by-year-307852"]

    def parse(self, response):
        # yield from response.follow_all(css="div.ds-w-full:nth-child(2) > div:nth-child(1) a", callback=self.parse_year_table)
        for anchor in response.css('div.ds-w-full:nth-child(2) > div:nth-child(1) a'):
            yield response.follow(anchor, callback=self.parse_year_table)

    def parse_year_table(self, response):
        year = response.css('h1::text').get()
        self.logger.info(f"Parsing matches for year: {year}")
        yield from response.follow_all(css="table tr td:nth-child(7) a", callback=self.parse_scorecard)

    def parse_scorecard(self, response):
        # Get Date
        date = response.css('h1.ds-text-title-xs ::text').getall()[-3]
        
        # Get winner
        winner_text = response.css('p.ds-text-tight-s:nth-child(3) ::text').get()
        winner = winner_text.split(' won')[0]

        # Get main divs
        main_divs = response.css('div.ds-w-full div.ds-w-full.ds-bg-fill-content-prime.ds-overflow-hidden.ds-rounded-xl.ds-border.ds-border-line.ds-mb-4')

        # Get team names
        heading = response.css('h1.ds-text-title-xs ::text').extract_first()
        teams = heading.split(',')[0]
        team_1_name, team_2_name = teams.split(' vs ')

        # Get runs and wickets for each team
        try:
            # TEAM 1
            team_1 = main_divs[0]
            team_1_table = team_1.css('table')[0]  # Get team 1 table
            row = search_rows(team_1_table, 'Total')
            ov1_raw = row.css('::text').getall()[1]  # Format: ## Ov
            ov1 = ov1_raw.split()[0]
            row_data = row.css('td:nth-child(3) ::text').getall()  # Get runs and wickets
        except (AttributeError, IndexError) as e:
            self.logger.warning(f"Error parsing team 1 in {response.url} - Setting runs, wickets, and overs to empty strings")
            self.logger.warning(e)
            team_1_runs = ''
            team_1_wickets = ''
            ov1 = ''
        else:
            if row_data[-1].startswith('/'):  # if the last element is a '/' then we have runs and wickets
                team_1_runs, team_1_wickets = row_data[-2], row_data[-1].strip('/')
            else:
                team_1_runs = row_data[0]
                team_1_wickets = '10'  # default value

        try:
            # TEAM 2
            team_2 = main_divs[1]
            team_2_table = team_2.css('table')[0]  # Get team 2 table
            row = search_rows(team_2_table, 'Total')
            ov2_raw = row.css('::text').getall()[1]  # Format: ## Ov
            ov2 = ov2_raw.split()[0]
            row_data = row.css('td:nth-child(3) ::text').getall()  # Get runs and wickets
        except (AttributeError, IndexError) as e:
            self.logger.warning(f"Error parsing team 2 in {response.url} - Setting runs, wickets, and overs to empty strings")
            self.logger.warning(e)
            team_2_runs = ''
            team_2_wickets = ''
            ov2 = ''
        else:
            if row_data[-1].startswith('/'):  # if the last element is a '/' then we have runs and wickets
                team_2_runs, team_2_wickets = row_data[-2], row_data[-1].strip('/')
            else:
                team_2_runs = row_data[0]
                team_2_wickets = '10'  # default value


        # Get match details section
        for div in main_divs:
            if div.css('div:first-child ::text').get().strip() == 'Match Details':
                MATCH_DETAILS = div
                break

        # Get ground
        details_table = MATCH_DETAILS.css('table')[0]
        ground = details_table.css('tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) ::text').get()
        # Get toss
        toss_text = details_table.css('tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2) ::text').get()
        toss_team = toss_text.split(',')[0]


        # Get match ID
        row = search_rows(details_table, 'Match number')
        match_id_raw = row.css('td:nth-child(2) ::text').get()
        match_id = match_id_raw.split()[-1]

        # Get daytime
        day_night = ''  # default value
        row = search_rows(details_table, 'Match days')
        if row is not None:
            day_night_raw = ''.join(
                row
                .css(' ::text')
                .getall()[1:]  # Exclude 'Match days'
                )
            # This seemed to be the most reliable way to get the daytime
            if 'daynight' in day_night_raw.lower():
                day_night = 'daynight'
            elif 'day' in day_night_raw.lower():
                day_night = 'day'
            elif 'night' in day_night_raw.lower():
                day_night = 'night'


        # Create item
        item = MatchItem()
        item['ID'] = match_id
        item['Date'] = date
        item['Ground'] = ground
        item['Toss'] = toss_team
        item['Winner'] = winner
        item['Bat1'] = team_1_name
        item['Runs1'] = team_1_runs
        item['Wickets1'] = team_1_wickets
        item['Over1'] = ov1
        item['Bat2'] = team_2_name
        item['Runs2'] = team_2_runs
        item['Wickets2'] = team_2_wickets
        item['Over2'] = ov2
        item['Daytime'] = day_night

        yield item


def search_rows(table, search_text):
    for row in table.css('tr'):
        if search_text in row.css(' ::text').getall():
            return row
    return None

# TODO:
# - Fix edge cases (no details for team 2): https://www.espncricinfo.com/series/hungary-in-austria-2022-1317132/austria-vs-hungary-2nd-t20i-1317141/full-scorecard