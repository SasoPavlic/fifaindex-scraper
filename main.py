import scrapy
from scrapy.cmdline import execute

class FifaScrapper(scrapy.Spider):
    name = "FIFA_spyder"
    allowed_domains = ['fifaindex.com']
    start_urls = ['https://www.fifaindex.com/players/1']
    custom_settings = {
        'concurrent_requests ': '1',
    }

    def parse(self, response):
        all_players_on_page = response.xpath(
            "//table[@class='table table-striped table-players']/tbody/tr[@data-playerid]")

        for player in all_players_on_page:
            player_link = player.xpath(".//td[@data-title='Name']/a/@href").extract()[0]
            yield scrapy.Request(str(response.urljoin(player_link)), callback=self.parsePlayer)

        length = len(response.xpath("//nav/ul//li").getall())
        navigation_element = 0

        if length >= 2:
            if response.xpath("//nav/ul//li/a/text()").extract()[1] == "Next Page":
                navigation_element = 1
        else:
            if response.xpath("//nav/ul//li/a/text()").extract()[0] == "Next Page":
                navigation_element = 0

        if response.xpath("//nav/ul//li/a/text()").extract()[0] == "Previous Page" and length < 2:
            print("SCRAPY REACHED THE END")
        else:
            next_page = response.xpath("//nav/ul//li")[navigation_element].xpath("a/@href").extract()[0]
            next_page_link = response.urljoin(next_page)
            yield response.follow(str(next_page_link), callback=self.parse)

    def parsePlayer(self, response):
        player = {}
        index = response.request.url.split('/')
        player['index'] = index[4]
        player['name'] = response.xpath("/html/body/main/div/div[2]/div[2]/div[2]/div[2]/div/h5/text()").get()
        player['nationality'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[2]/div[1]/div[1]/div[2]/h2/a[2]/text()").get()
        # Personal details
        player['ovr'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[2]/div[2]/div/h5/span/span[1]/text()").get()
        player['pot'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[2]/div[2]/div/h5/span/span[2]/text()").get()
        player['height'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[2]/div[2]/div/div/p[1]/span/span[1]/text()").get()
        player['weight'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[2]/div[2]/div/div/p[2]/span/span[1]/text()").get()
        player['preferred_foot'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[2]/div[2]/div/div/p[3]/span/text()").get()
        player['birth_date'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[2]/div[2]/div/div/p[4]/span/text()").get()
        player['age'] = response.xpath("/html/body/main/div/div[2]/div[2]/div[2]/div[2]/div/div/p[5]/span/text()").get()
        player['preferred_positions'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[2]/div[2]/div/div/p[6]/span/a/span/text()").get()
        player['player_work_rate'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[2]/div[2]/div/div/p[7]/span/text()").get()

        weak_foot_calc_full_stars = len(
            response.xpath("/html/body/main/div/div[2]/div[2]/div[2]/div[2]/div/div/p[8]/span/span/i").getall())
        weak_foot_calc_empty_stars = len(response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[2]/div[2]/div/div/p[8]/span/span/i[@class='far fa-star fa-lg']").getall())
        player['weak_foot'] = weak_foot_calc_full_stars - weak_foot_calc_empty_stars

        skill_moves_calc_full_stars = len(
            response.xpath("/html/body/main/div/div[2]/div[2]/div[2]/div[2]/div/div/p[9]/span/span/i").getall())
        skill_moves_calc_empty_stars = len(response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[2]/div[2]/div/div/p[9]/span/span/i[@class='far fa-star fa-lg']").getall())
        player['skill_moves'] = skill_moves_calc_full_stars - skill_moves_calc_empty_stars

        player['value'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[2]/div[2]/div/div/p[10]/span/text()").get()
        player['wage'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[2]/div[2]/div/div/p[13]/span/text()").get()

        # National team info
        player['national_team_name'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[3]/div[1]/div/h5/a[2]/text()").get()
        player['national_team_position'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[3]/div[1]/div/div/p[1]/span/a/span/text()").get()
        player['national_team_kit_num'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[3]/div[1]/div/div/p[2]/span/text()").get()

        # Club team info
        player['club_team_name'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[3]/div[2]/div/h5/a[2]/text()").get()
        player['club_team_position'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[3]/div[2]/div/div/p[1]/span/a/span/text()").get()
        player['club_team_kit_num'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[3]/div[2]/div/div/p[2]/span/text()").get()
        player['club_team_joined_date'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[3]/div[2]/div/div/p[3]/span/text()").get()
        player['club_team_contract_end'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[3]/div[2]/div/div/p[4]/span/text()").get()

        # Sometimes national team is empty (player is only playing in club team)
        if player['club_team_name'] is None:
            # Get club team new values
            player['club_team_name'] = response.xpath(
                "/html/body/main/div/div[2]/div[2]/div[3]/div/div/h5/a[2]/text()").get()
            player['club_team_position'] = response.xpath(
                "/html/body/main/div/div[2]/div[2]/div[3]/div/div/div/p[1]/span/a/span/text()").get()
            player['club_team_kit_num'] = response.xpath(
                "/html/body/main/div/div[2]/div[2]/div[3]/div/div/div/p[2]/span/text()").get()
            player['club_team_joined_date'] = response.xpath(
                "/html/body/main/div/div[2]/div[2]/div[3]/div/div/div/p[3]/span/text()").get()
            player['club_team_contract_end'] = response.xpath(
                "/html/body/main/div/div[2]/div[2]/div[3]/div/div/div/p[4]/span/text()").get()

            # Change national team to empty
            player['national_team_name'] = None
            player['national_team_position'] = None
            player['national_team_kit_num'] = None

        # Sometimes club team is empty (player is only playing in national team)
        if player['national_team_name'] == "Free Agents":
            player['national_team_name'] = response.xpath("/html/body/main/div/div[2]/div[2]/div[3]/div[2]/div/h5/a[2]/text()").get()
            player['national_team_position'] = response.xpath("/html/body/main/div/div[2]/div[2]/div[3]/div[2]/div/div/p[1]/span/a/span/text()").get()
            player['national_team_kit_num'] = response.xpath("/html/body/main/div/div[2]/div[2]/div[3]/div[2]/div/div/p[2]/span/text()").get()

            player['club_team_name'] = response.xpath("/html/body/main/div/div[2]/div[2]/div[3]/div[1]/div/h5/a[2]/text()").get()
            player['club_team_position'] = response.xpath("/html/body/main/div/div[2]/div[2]/div[3]/div[1]/div/div/p[1]/span/a/span/text()").get()
            player['club_team_kit_num'] = response.xpath("/html/body/main/div/div[2]/div[2]/div[3]/div[1]/div/div/p[2]/span/text()").get()
            player['club_team_joined_date'] = response.xpath("/html/body/main/div/div[2]/div[2]/div[3]/div[1]/div/div/p[3]/span/text()").get()
            player['club_team_contract_end'] = response.xpath("/html/body/main/div/div[2]/div[2]/div[3]/div[1]/div/div/p[4]/span/text()").get()

        # Ball Skills
        player['ball_control'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[1]/div/div/p[1]/span/span/text()").get()
        player['dribbling'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[1]/div/div/p[2]/span/span/text()").get()

        # Defence
        player['marking'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[2]/div/div/p[1]/span/span/text()").get()
        player['slide_tackle'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[2]/div/div/p[2]/span/span/text()").get()
        player['stand_tackle'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[2]/div/div/p[3]/span/span/text()").get()

        # Mental
        player['aggression'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[3]/div/div/p[1]/span/span/text()").get()
        player['reactions'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[3]/div/div/p[2]/span/span/text()").get()
        player['att_position'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[3]/div/div/p[3]/span/span/text()").get()
        player['interceptions'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[3]/div/div/p[4]/span/span/text()").get()
        player['vision'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[3]/div/div/p[5]/span/span/text()").get()
        player['composure'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[3]/div/div/p[6]/span/span/text()").get()

        # Passing
        player['crossing'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[4]/div/div/p[1]/span/span/text()").get()
        player['short_pass'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[4]/div/div/p[2]/span/span/text()").get()
        player['long_pass'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[4]/div/div/p[3]/span/span/text()").get()

        # Physical
        player['acceleration'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[5]/div/div/p[1]/span/span/text()").get()
        player['stamina'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[5]/div/div/p[2]/span/span/text()").get()
        player['strength'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[5]/div/div/p[3]/span/span/text()").get()
        player['balance'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[5]/div/div/p[4]/span/span/text()").get()
        player['sprint_speed'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[5]/div/div/p[5]/span/span/text()").get()
        player['agility'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[5]/div/div/p[6]/span/span/text()").get()
        player['jumping'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[5]/div/div/p[7]/span/span/text()").get()

        # Shooting
        player['heading'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[6]/div/div/p[1]/span/span/text()").get()
        player['shoot_power'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[6]/div/div/p[2]/span/span/text()").get()
        player['finishing'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[6]/div/div/p[3]/span/span/text()").get()
        player['long_shots'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[6]/div/div/p[4]/span/span/text()").get()
        player['curve'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[6]/div/div/p[5]/span/span/text()").get()
        player['FK_acc'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[6]/div/div/p[6]/span/span/text()").get()
        player['penalties'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[6]/div/div/p[7]/span/span/text()").get()
        player['volleys'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[6]/div/div/p[8]/span/span/text()").get()

        # Goalkeeper
        player['GK_positioning'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[7]/div/div/p[1]/span/span/text()").get()
        player['GK_diving'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[7]/div/div/p[2]/span/span/text()").get()
        player['GK_handling'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[7]/div/div/p[3]/span/span/text()").get()
        player['GK_kicking'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[7]/div/div/p[4]/span/span/text()").get()
        player['GK_reflexes'] = response.xpath(
            "/html/body/main/div/div[2]/div[2]/div[4]/div[7]/div/div/p[5]/span/span/text()").get()

        if response.xpath("/html/body/main/div/div[2]/div[2]/div[4]/div[9]/div/h5/text()").get() == "Traits":
            player['traits'] = response.xpath(
                "/html/body/main/div/div[2]/div[2]/div[4]/div[9]/div/div/p/node()").extract()
        if response.xpath("/html/body/main/div/div[2]/div[2]/div[4]/div[8]/div/h5/text()").get() == "Specialities":
            player['specialities'] = response.xpath(
                "/html/body/main/div/div[2]/div[2]/div[4]/div[8]/div/div/p/node()").extract()

        player['link'] = response.request.url

        yield player


execute("scrapy runspider main.py -o players.json".split())
