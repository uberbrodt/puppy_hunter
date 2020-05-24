# -*- coding: utf-8 -*-
import scrapy


class PuppyCrawler(scrapy.Spider):
    name = "puppyhunter"
    start_urls = [
        "https://ws.petango.com/webservices/adoptablesearch/wsAdoptableAnimals.aspx?species=Dog&gender=A&agegroup=UnderYear&location=&site=&onhold=A&orderby=name&colnum=3&css=http://ws.petango.com/WebServices/adoptablesearch/css/styles.css&authkey=io53xfw8b0k2ocet3yb83666507n2168taf513lkxrqe681kf8&recAmount=&detailsInPopup=No&featuredPet=Include&stageID=&wmode=opaque"
    ]

    def parse(self, response):
        for puppy in response.css("td.list-item"):
            pupper_link = puppy.css("div.list-animal-name>a::attr('href')").get()

            pupperino = {
                "id": puppy.css("div.list-animal-id::text").get(),
                "name": puppy.css("div.list-animal-name>a::text").get(),
                "detail_link": response.urljoin(pupper_link),
                "sex": puppy.css("div.list-animal-sexSN::text").get(),
                "breed": puppy.css("div.list-animal-breed::text").get(),
            }
            yield response.follow(
                pupper_link, self.pupper_info, meta={"pupperino": pupperino}
            )

    def pupper_info(self, response):
        pupperino = response.meta["pupperino"]
        pupperino["size"] = response.css("span#lblSize::text").get()
        pupperino["stage"] = response.css("span#lblStage::text").get()
        yield pupperino
