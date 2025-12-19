#Augment_dataset_2025.py
import pandas as pd
import joblib
import sys
import os
from collections import Counter


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Changed_Solution.Changed_feature_extractor import ChangedURLFeatureExtractor

print("\n" + "="*70)
print(" 📦 AUGMENTING MODEL 2025 TRAINING DATASET")
print("="*70)

# Complex legitimate URLs
complex_legitimate_urls = [
    "https://www.britannica.com/biography/Che-Guevara",
    "https://plato.stanford.edu/entries/ethics-ai/",
    "https://www.khanacademy.org/math/algebra/x2f8bb11595b61c86:systems-of-equations",
    "https://scholar.google.com/scholar?hl=en&q=phishing+detection",
    "https://www.baseball-almanac.com/teamstats/roster.php?y=1988&t=MON",
    "https://docs.google.com/document/d/1A9f8KJ9P2wQxU4Y/edit",
    "https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow",
    "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise",
    "https://github.com/openai/gpt-4/blob/main/system_card.md",
    "https://auth0.com/docs/flows/authorization-code-flow",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://medium.com/@user/how-machine-learning-detects-phishing-8f92a9c12",
    "https://www.reddit.com/r/netsec/comments/15f9k2m/phishing_detection_models/",
    "https://vimeo.com/76979871",
    "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
    "https://accounts.google.com/o/oauth2/v2/auth",
    "https://www.nsf.gov/awardsearch/showAward?AWD_ID=2033955",
    "https://www.apu.edu.my/research/publications/2023/ai-security-models",   
    "https://www.sbsmnlaw.com/attorney-profiles/",
    "https://www.encyclopedia.com/video/dr_g23qi9hg-che-guevara-song-hasta-siempre.aspx",
    "https://www.californiabeat.org/2010/08/02/the-end-of-an-era-farewell-to-the-transbay-terminal",
    "https://www.ccdr.org/joan_p_kealiinohomoku.html",
    "https://www.myspace.com/vylan",
    "https://www.en.wikipedia.org/wiki/Place_du_Portage",
    "https://www.hikercentral.com/campgrounds/109226.htm",
    "https://www.facebook.com/people/Conrad-Black/100000600135988",
    "https://www.theplace4mortgages.com/",
    "https://www.timeanddate.com/library/abbreviations/timezones/au/est.html",
    "https://www.kansascitymissouri.diningandspirits.com/mexican.php",
    "https://www.montrealgazette.com/sports/Grands+Prix+Cycliste+Quebec+Montreal+relying+names+success/5296196/story.html",
    "https://www.en.wikipedia.org/wiki/Premier_League",
    "https://www.fandango.com/tommyrall/filmography/p58568",
    "https://www.oakland.athletics.mlb.com/spring_training/ballpark.jsp?c_id=oak",
    "https://www.upcoming.yahoo.com/venue/574862/WA/Olympia/Emilie-Gamelin-Pavilion",
    "https://www.tarnoffartcenter.org/TarnoffArtCenter/Instructors_%26_Staff.html",
    "https://www.tripadvisor.com/ShowUserReviews-g44535-d390916-r81865923-Savoy_Grill-Kansas_City_Missouri.html",
    "https://www.en.wikipedia.org/wiki/Category:American_musical_comedy_films",
    "https://www.tour.suite703.com/scenes/adam_russo_and_dodger_wolf/11794/",
    "https://www.stadiumjourney.com/stadiums/oracle-arena-s118/",
    "https://www.store.heavyartillery.us/index.php?main_page=product_music_info&products_id=451",
    "https://www.history.ca/ontv/titledetails.aspx?titleid=21273",
    "https://www.uk.movies.yahoo.com/artists/g/Gary-Goldman/index-323890.html",
    "https://www.ticketseating.com/more-cirque-du-soleil-tickets/",
    "https://www.montreal.ctv.ca/servlet/an/local/CTVNews/20110526/mtl_laval_metro_110526/20110526/?hub=MontrealHome",
    "https://www.letrs.indiana.edu/cgi/t/text/text-idx?c=wright2;cc=wright2;view=text;rgn=main;idno=Wright2-2391v1",
    "https://www.freepages.genealogy.rootsweb.ancestry.com/~obitsindex/obits_nh_coos_01.htm",
    "https://www.findagrave.com/cgi-bin/fg.cgi?page=gr&GRid=1194",
    "https://www.sweetslyrics.com/901582.Macklemore%20-%20Can't%20Hold%20Us.html",
    "https://www.litigation-essentials.lexisnexis.com/webcd/app?action=DocumentDisplay&crawlid=1&doctype=cite&docid=38+U.B.C.+L.+Rev.+353&srctype=smi&srcid=3B15&key=3158f575af75edf086104f52835ddbb1",
    "https://www.amazon.com/Big-Bang-Theory-Complete-Second/dp/B001FB4VXU",
    "https://www.mahoganysoulonline.com/?page_id=125",
    "https://www.business.financialpost.com/2011/05/25/national-bank-financial-to-buy-wellington-west-source/",
    "https://www.imdb.com/name/nm0601450/",
    "https://www.klwines.com/detail.asp?sku=1047841",
    "https://www.theoriginalhorsetackcompany.com/ProductDetails.asp?ProductCode=BY9104",
    "https://www.tvtrip.com/Hospital+17-info/Centre-hospitalier-intercommunal-de-Poissy-Saint-Germain-en-Laye+u1HStT",
    "https://www.btjunkie.org/torrent/Beneath-The-Massacre-Mechanics-Of-Dysfunction/55305ef1ed09b059fd31c875210c4cab4750c39aafa8",
    "https://www.english.turkcebilgi.com/Saint-Jean-sur-Richelieu%2c+Quebec",
    "https://www.betheboss.ca/Thai-Express-Franchise.cfm",
    "https://www.marketwire.com/press-release/SENSIO-Technologies-Acquires-Algoliths-Intellectual-Property-Secures-Integration-Key-TSX-VENTURE-SIO-1361949.htm",
    "https://www.news.nationalpost.com/2011/10/27/tory-bill-would-add-30-new-mps-to-house-of-commons/",
    "https://www.classmates.com/directory/public/memberprofile/list.htm?regId=8696008867",
    "https://www.mirror.co.uk/news/royal-wedding/2011/10/14/the-queen-to-be-great-grandmother-again-as-peter-and-autumn-phillips-expect-2nd-child-115875-23489492/",
    "https://www.en.wikipedia.org/wiki/The_Concert_(Creedence_Clearwater_Revival_album)",
    "https://www.redux.com/stream/item/12000/Marshawn-Lynch-The-Mayne-Event",
    "https://www.classmates.com/directory/public/memberprofile/list.htm?regId=8696008867",
    "https://www.absoluteastronomy.com/topics/KCWY",
    "https://www.evri.com/person/william-sutherland-maxwell-0x70d53",
    "https://www.rafiki-kenya.blogspot.com/2010/09/pumzi-kenyan-sci-fi-movie.html",
    "https://www.stevestennisworld.com/",
    "https://www.youtube.com/watch?v=ws4NobWHHaU",
    "https://www.document.mitrasites.com/sidney-hickox.html",
    "https://www.lawyers.justia.com/lawyers/divorce/rhode-island/newport-county",
    "https://www.mirror.co.uk/news/royal-wedding/2011/10/14/the-queen-to-be-great-grandmother-again-as-peter-and-autumn-phillips-expect-2nd-child-115875-23489492/",
    "https://www.en.wikipedia.org/wiki/Restigouche_class_destroyer",
    "https://www.americaeast.com/SportSelect.dbml?DB_OEM_ID=14000&SPID=6550&SPSID=59747",
    "https://www.dramaclubfilms.com/",
    "https://www.atlanticbassmasters.com/Lake%20Records/Lake%20Records%201.htm",
    "https://www.youtube.com/watch?v=ITaLSeSkB5c",
    "https://www.dbpedia.openlinksw.com:8890/resource/John_Bain",
    "https://www.en.wikipedia.org/wiki/Category:Tourism_in_the_Republic_of_Ireland",
    "https://www.phoenix.jobing.com/company_profile.asp?i=13869",
    "https://www.jefferson.nygenweb.net/childell.htm",
    "https://www.amazon.com/Twin-Cities-Then-Now-Minnesota/dp/0873513274",
    "https://www.wonderlandparty.com/Costume-Favourites/Storybook/costumes-1-20-2.aspx",
    "https://www.extension.missouri.edu/publications/DisplayPub.aspx?P=DM4003-21",
    "https://www.socialdiligence.com/person/r/r-mo/r-mo336.html",
    "https://www.touchreading.com/business/list/bid/4951814",
    "https://www.oddjack.com/2008/will-tennessee-titans-quarterback-kerry-collins-win-the-2008-nfl-most-valuable-player-of-the-year-award-11-30.php",
    "https://www.linkedin.com/pub/doug-jenson/8/172/9a7",
    "https://www.foswms.com/families/rabb.html",
    "https://www.slayton.govoffice.com/index.asp?Type=B_BASIC&SEC={EB27F97D-258E-4BC6-BC4C-578D3BC0D0A4}&DE={46FA7543-3BCA-49F8-BD73-A4BCE049369E}",
    "https://www.layart-games.de/",
    "https://www.mixcloud.com/donald-isaac/",
    "https://www.zoominfo.com/people/Roberts_Curt_742206342.aspx",
    "https://www.dudleyhewittcuphuntsville.com/about-the-cup.html",
    "https://www.findagrave.com/php/famous.php?page=date&globalSearchCriteria=&globalSearchType=&FSlastinitial=&FSstateid=&FSctf=&firstName=&lastName=&FScemeteryid=&FScityid=&FScountryid=&FScountyid=&FSstartrow=81&FSbirthmonth=7&FSbirthday=14&FSbirthyear=&FSdeathmonth=&FSdeathday=&FSdeathyear=",
    "https://www.fileknow.net/lesa+lewis",
    "https://www.frumforum.com/occupy-wall-street-is-going-nowhere",
    "https://www.tunein.com/radio/Mix-933-s34196/",
    "https://www.archive.org/stream/cihm_00147/cihm_00147_djvu.txt",
    "https://www.article.wn.com/view/2008/04/15/Philip_Morris_USA_RJR_make_payments_on_tobacco_settlement/",
    "https://www.wellness.com/dir/2458760/orthopedic-surgeon/tx/denton/major-blair-jr-md",
    "https://www.montrealvip.com/info/attractions/la-ronde-amusement-park.html",
    "https://www.pastebin.com/vZv8ZDei",
    "https://www.youtube.com/watch?v=RTPI-zKWZ_M",
    "https://www.lowkick.blitzcorner.com/tags/UFC/UFC-124",
    "https://www.fieldgulls.com/2011/7/29/2303018/dt-brandon-mebane-re-signs-with-the-seahawks",
    "https://www.wn.com/John_Ray_(Missouri)",
    "https://www.public.asu.edu/~moore/archibald/archindex.html",
    "https://www.highbeam.com/doc/1G1-153860100.html",
    "https://www.frankmattauch.ifunnyblog.com/abdulfrompascagoula/",
    "https://www.en.wikipedia.org/wiki/Johnny_Carpenter",
    "https://www.markettorrent.com/community/viewtopic.php?f=44&t=5002",
    "https://www.christianpost.com/news/conservative-hollywood-celebs-endorse-perry-bachmann-and-paul-62226/",
    "https://www.en.wikipedia.org/wiki/Dystopia_(Beneath_the_Massacre_album)",
    "https://www.allmusic.com/album/the-immortal-mississippi-john-hurt-r88766",
    "https://www.amazon.com/Star-Trek-Next-Generation-Collection/dp/B00023P4F6",
    "https://www.nhl.com/ice/player.htm?id=8467731",
    "https://www.en.memory-alpha.org/wiki/Clint_Howard",
    "https://www.diccionario.sensagent.com/práxedis+g.+guerrero+(municipality)/en-en/",
    "https://www.liveguide.com.au/Tours/707076/Pam_Ayres/A_Fun_Filled_Evening_With_Pam_Ayres",
    "https://www.filmexperience.blogspot.com/2010/02/actors-on-actors-zoes-lust-tobeys.html",
    "https://www.frankenstein1931.com/cast/cast.html",
    "https://www.newjerseycarclassifieds.com/",
    "https://www.facebook.com/people/Edward-Chen/1360080270",
    "https://www.frankmarinodesign.com/",
    "https://www.debmurray.tripod.com/dearborn/dearinsura-g.html",
    "https://www.123people.com/s/walter+george",
    "https://www.amazon.com/Drawn-Quarterly-Anthology-Vol-5/dp/1896597610",
    "https://www.uk.ask.com/wiki/Paul_Kiernan",
    "https://www.gloryofzion.org/",
    "https://www.chaiandyoga.com/yoga-teacher-profile-lisa-steele/",
    "https://www.seriesandtv.com/late-night-with-jimmy-fallon-%e2%80%93-21-recap-ice-cube-and-leighton-meester/5050",
    "https://www.wssurams.com/sports/m-footbl/mtt/goldston_tyrone00.html",
    "https://www.dslreports.com/forum/r24749926-TV-Fibe-TV-Questions",
    "https://www.rootsweb.ancestry.com/~pasulliv/",
    "https://www.filmcritic.com/reviews/2005/the-constant-gardener/",
    "https://www.usengineering.com/our-work/markets/government/united-states-courthouse",
    "https://www.enotes.com/contemporary-musicians/macdermot-galt-biography",
    "https://www.giantcamera.com/",
    "https://www.irht.cnrs.fr/en/institut/GIS",
    "https://www.spokeo.com/David+Dreier",
    "https://www.visitlondon.com/attractions/detail/189947-docklands-dry-cleaning-and-laundry-service",
    "https://www.rockshockpop.com/forums/content.php?1466-Blood-Bath-Burn-Witch-Burn-And-More-From-The-MGM-Limited-Edition-Collection",
    "https://www.mtroyal.ca/EmploymentCareers/index.htm",
    "https://www.chantillyvirginia.com/",
    "https://www.manta.com/c/mt5wmlx/perry-plumbing",
    "https://www.bennetlaw.com/about-us/attorneys/robert-a-silverman/",
    "https://www.timezoneguide.com/tz-distance.php",
    "https://www.modrojezero.org/dalmacija/Dubrovnik/index.html",
    "https://www.tweetdeck.com/twitter/4L_FI3/~WgXru",
    "https://www.loyolacollege.edu/",
    "https://www.slovenia.info/en/vinska-cesta/Gornjedolenjska-Wine-Road-in-Trebnje-Municipality.htm?vinska_cesta=428&lng=2",
    "https://www.spartanburg2.k12.sc.us/chs/",
    "https://www.martialarts.about.com/od/mmaandufc/ss/Ufc-124-Predictions.htm",
    "https://www.staffspolicerecruitment.com/",
    "https://www.answers.com/topic/della-rocca",
    "https://www.facebook.com/pages/21st-Century-Breakdown/103092893064130",
    "https://www.123people.com/s/don+poirier",
    "https://www.en.memory-alpha.org/wiki/Michael_Sarrazin",
    "https://www.usfamily.net/web/trombleyd/SaintsRoster.htm",
    "https://www.rentmoney.com/State/TX/Metro/Dallas/City/Dallas/Property/The%20Greens%20of%20Kessler%20Park/ApartmentForRent.aspx",
    "https://www.linkedin.com/in/wwjohnston",
    "https://www.myspace.com/notesplussounds",
    "https://www.soundstage.com/revequip/oracle_si1000.htm",
    "https://www.socalmartialarts.com/los-angeles-martial-arts.html",
    "https://www.bcbst.com/",
    "https://www.fandango.com/leogorcey/filmography/p27744",
    "https://www.byownermls.com/MONMOUTHcounty_NJ.htm",
    "https://www.imdb.com/name/nm0216755/",
    "https://www.pcmichiganhistory.blogspot.com/",
    "https://www.songlyrics.com/casual-lyrics/",
    "https://www.librarything.com/author/lakejohng",
    "https://www.healthgrades.com/physician/dr-yvonne-nelson-xykdt/",
    "https://www.basicfamouspeople.com/index.php?aid=1779",
    "https://www.fotopedia.com/albums/ESh4WOcjIFc",
    "https://www.uk.linkedin.com/pub/norman-robertson/13/256/9a1",
    "https://www.landoftalk.com/",
    "https://www.jacquesamand.com/",
    "https://www.amazon.com/Amelia-Blu-ray-Scott-Anderson/dp/B0030E5NLY",
    "https://www.en.wikipedia.org/wiki/Biutiful",
    "https://www.utahstateaggies.com/sports/m-baskbl/spec-rel/102907aac.html",
    "https://www.oursaviourslutheran.com/",
    "https://www.sports.espn.go.com/nba/playoffs/2010/columns/story?columnist=hollinger_john&page=FranchiseRankings2010-Lakers",
    "https://www.richardroeper.com/reviews/theswitch.aspx",
    "https://www.mylife.com/c-1244326884",
    "https://www.hispanicbusiness.com/news/2008/5/6/krzz_933_fm_la_raza_enjoys.htm",
    "https://www.corkin.com/listings/viewlisting.cfm?listingid=273829",
    "https://www.ussoccer.com/News/Mens-National-Team/2009/03/U-S-Mens-National-Team-Heads-To-El-Salvador-For-FIFA-World-Cup-Qualifier.aspx",
    "https://www.ziplocal.ca/find/machine-tools-in-montreal",
    "https://www.nashvillecitypaper.com/content/city-news/judge-dismisses-former-councilwoman-pam-murrays-defamation-lawsuit",
    "https://www.newenglandvacationtours.com/?CONTENT=tours/ne_nova",
    "https://www.article.wn.com/view/2010/03/18/Strawberry_Mansion_boys_get_past_St_Pius_X/",
    "https://www.ultimatecheerleaders.com/2010/10/2010-11-tampa-bay-buccaneers-cheerleaders/",
    "https://www.glassdoor.com/Reviews/America-First-Credit-Union-Reviews-E25674.htm",
    "https://www.hispanictips.com/2011/04/08/miami-based-latino-sales-company-ondamax-films-has-sold-a-10-film-package-to-u-s-and-latin-american-spanish-language-premium-paybox-cine-latino/",
    "https://www.homefinder.com/NY/Phoenicia/",
    "https://www.randomhouse.com/book/24841/negaholics-by-cherie-carter-scott",
    "https://www.gopetition.com/petitions/put-big-wolf-on-campus-on-dvd.html",
    "https://www.leduc.realestatesurfing.com/",
    "https://www.xtube.com/community/profile.php?user=xtube_sponsor",
    "https://www.emp3world.com/mp3/94471/Gwen%20Stefani/Cool",
    "https://www.en.wikipedia.org/wiki/Category:American_short_films",
    "https://www.rightmove.co.uk/developer/branch/Persimmon-Homes/Broad-Sands-64820.html",
    "https://www.cheapflights.com/airports/montreal-pierre-elliott-trudeau/",
    "https://www.spiritus-temporis.com/20-june/births.html",
    "https://www.youtube.com/watch?v=kdV26lz3yT8",
    "https://www.answers.com/topic/the-rainmakers-kansas-city-missouri-band",
    "https://www.hoovers.com/company/St_Ritas_Medical_Center/rtfjhri-1.html",
    "https://www.pornqq.com/straight-porn/77568-lesa-lewis-two-clips.html?pagenumber=",
    "https://www.archiver.rootsweb.ancestry.com/th/read/METISGEN/2003-06/1056315852",
    "https://www.thehindubusinessline.in/2011/01/15/stories/2011011551241000.htm",
    "https://www.thestarphoenix.com/life/Tory+senator+remains+critical+unilingual+appointment/5672551/story.html",
    "https://www.ca.sports.yahoo.com/cfl/news?slug=montgaz-ca-5590610",
    "https://www.mp3fundoo.com/bollywood/index.php?action=album&id=530",
    "https://www.guardian.co.uk/sport/blog/2011/oct/19/rugby-world-cup-final-1987",
    "https://www.youtube.com/watch?v=6iGi-FM-fnQ",
    "https://www.katyelliott.com/blog/2009/05/weck-canning-jars.html",
    "https://www.youtube.com/watch?v=km1-6CGszto",
    "https://www.whitepages.com/name/Dan-Delisle",
    "https://www.oakknoll.com/detail.php?d_booknr=89013&d_currency=",
    "https://www.lawfolks.com/three-fifths_compromise/encyclopedia.htm",
    "https://www.ps3grid.net/forum_thread.php?id=513",
    "https://www.hockeyfights.com/players/7",
    "https://www.agenceartistiquehelena.com/fr/adultes.php",
    "https://www.en.wikipedia.org/wiki/Tour_Scotia",
    "https://www.mlb.mlb.com/news/article.jsp?ymd=20081125&content_id=3691944&fext=.jsp&partnerId=rss_mlb",
    "https://www.autoblog.com/2011/07/29/unconfirmed-next-generation-ford-and-gm-truck-powertrain-details/",
    "https://www.en.wikipedia.org/wiki/Greg_Foster",
    "https://www.people.famouswhy.com/bruce_springsteen/",
    "https://www.jcedc.org/Pages/uezcertification.html",
    "https://www.generasia.com/wiki/Hey!_Say!_JUMP",
    "https://www.oursportscentral.com/usfl/oak85.htm",
    "https://www.tracksounds.com/reviews/eastwest.htm",
    "https://www.elyrics.net/read/m/madonna-lyrics/like-a-prayer-lyrics.html",
    "https://www.jobtrio.com/site-maps/california/torrance/general-contractors/",
    "https://www.allaboutjazz.com/php/profile_editor_list.php?id=1",
    "https://www.horizontrails.com/",
    "https://www.blog2ico.wordpress.com/2011/05/04/team-performance-assessment/",
    "https://www.bookfinder.com/author/diane-dufour/",
    "https://www.youtube.com/watch?v=tSWRrLl3cBM",
    "https://www.last.fm/music/GGFH",
    "https://www.web1.ctaa.org/webmodules/webarticles/anmviewer.asp?a=861&z=5",
    "https://www.guitaretab.com/v/vermillion-lies/253193.html",
    "https://www.en.wikipedia.org/wiki/Charles_le_Moyne_de_Longueuil_et_de_Ch%C3%A2teauguay",
    "https://www.torrentz.eu/97db919c9063290183111916d0efcd7900ff0f48",
    "https://www.rbr.com/tv-cable/newport-television-sees-core-ads-pacing-up-in-q4.html",
    "https://www.examiner.com/conservative-in-chicago/illinois-inmates-receive-hand-delivered-ballots-for-2010-midterm-elections",
    "https://www.waatp.com/people/edna-bouchard/27876821/",
    "https://www.automobilemag.com/features/news/0909_david_e_davis_jr_vs_brock_yates_great_rivalries/index.html",
    "https://www.wn.com/Spike_Lee",
    "https://www.video.v2load.de/164839/",
    "https://www.healthgrades.com/physician/dr-william-adrion-yr28q/",
    "https://www.facebook.com/people/Ray-Walters/775937206",
    "https://www.superstock.com/stock-photography/teapot",
    "https://www.iwu.edu/",
    "https://www.funnyordie.com/videos/b5fc3e30fa/white-trash-heroes-3-nascar-mullets-from-ttowners",
    "https://www.en.wikipedia.org/wiki/Border_Break",
    "https://www.start.cortera.com/company/research/k2j6kun4s/superior-coach-sales-inc/",
    "https://www.collegebaseballdaily.com/2011/05/20/ncbwa-announces-dick-howser-trophy-semifinalists-2/",
    "https://www.bonjourquebec.com/qc-en/tourist-services-directory/shuttle-service/gray-line-of-montreal-coach-canada-south-shore-of-montreal_7205247.html",
    "https://www.amazon.com/s?ie=UTF8&keywords=Phyllis%20Diller&rh=i%3Aaps%2Ck%3APhyllis%20Diller&page=1",
    "https://www.boards.ancestry.netscape.com/thread.aspx?mv=flat&m=9&p=surnames.glaspie",
    "https://www.spirit-of-metal.com/album-groupe-Europe-nom_album-Le_baron_boys_(Out_of_the_prisoners_in_paradise_session)-l-en.html",
    "https://www.absoluteastronomy.com/topics/Football_at_the_1984_Summer_Olympics",
    "https://www.ca.linkedin.com/pub/claude-dessureault/4/309/308",
    "https://www.oakland.athletics.mlb.com/oak/ticketing/tickets_landing.jsp",
    "https://www.fleetwoodmac-uk.com/albums/gos/GOS.html",
    "https://www.croonet.com/start/M_ODQyODAx/",
    "https://www.topix.com/city/rose-creek-mn",
    "https://www.daylilydiary.com/",
    "https://www.linkedin.com/pub/jean-fran%C3%A7ois-pouliot/13/560/305",
    "https://www.uk-ufo.co.uk/2010/01/fiddlers-ferry-power-station-warrington-29th-january-2010/",
    "https://www.star500.com/store/home.php?cat=2940",
    "https://www.rodandcustommagazine.com/featuredvehicles/0910rc_1950_oldsmobile_futuramic_88_deluxe_club_coupe/viewall.html",
    "https://www.sportsillustrated.cnn.com/football/ncaa/teams/iowa-st-cyclones/",
    "https://www.skyscrapercity.com/showthread.php?t=1401220",
    "https://www.deadspin.com/5838004/phillies-of-john-mayberry-jr-has-requested-that-his-agents-set-him-up-with-the-sexy-mermaid-from-pirates-of-the-caribbean",
    "https://www.bleacherreport.com/articles/1851-mlb-history-contest-the-all-time-oakland-athletics-roster",
    "https://www.dublin.ratemyarea.com/places/dr-liam-power-5450",
    "https://www.hyecal.com/events/index.php?com=location",
    "https://www.genforum.genealogy.com/glasco/",
    "https://www.youtube.com/watch?v=meA2I9plWxE",
    "https://www.gazettenet.com/2011/08/31/lee-langevin",
    "https://www.pipl.com/directory/name/Gordon/Lionel",
    "https://www.boffinms.com/~omega/genealogy/binnie/binnie.htm",
    "https://www.pipl.com/directory/name/Arraj",
    "https://www.wiki.answers.com/Q/What_school_did_Cheryl_Tweedy_attend",
    "https://www.shoesinview.com/2011/06/25/charles-keith-spring-summer-2011/",
    "https://www.discogs.com/search?type=all&q=Walt+Winston",
    "https://www.worthpoint.com/worthopedia/tony-lema-signed-cut-autograph-jsa-auth",
    "https://www.vh1.com/artists/az/kingston_trio/lyrics.jhtml",
    "https://www.scores.espn.go.com/nfl/recap?gameId=301226012",
    "https://www.icehockey.wikia.com/wiki/Brian_Mullen",
    "https://www.chambermusicsocietyofporttownsend.org/?page_id=232",
    "https://www.en.wikipedia.org/wiki/Category:Novels_by_John_Dickson_Carr",
    "https://www.fattoneguitars.com/default.asp",
    "https://www.lyricsty.com/one-way-dont-stop-lyrics.html",
    "https://www.goliath.ecnext.com/coms2/product-compint-0001227878-page.html",
    "https://www.baseball-reference.com/bullpen/Montr%C3%A9al_Expos",
    "https://www.legendsofamerica.com/we-explorerindex.html",
    "https://www.youtube.com/watch?v=yIa1U_Clyfk",
    "https://www.frequency.com/topic/political+scientist",
    "https://www.elcaminocentral.com/showthread.php?t=43884",
    "https://www.wave3.com/story/16049484/video-mel-gibson-jamie-foxx-and-garry-shandling-brainstorm-a-tribute-for-robert-downey-jr",
    "https://www.the700level.com/08/23/11/Shane-Victorino-and-John-Mayberry-Jr-Kil/landing_phillies.html?blockID=553150",
    "https://www.amazon.com/Volcanoes-Human-History-Far-Reaching-Eruptions/dp/0691050813",
    "https://www.listal.com/list/best-german-language-films",
    "https://www.classmates.com/directory/public/memberprofile/list.htm?regId=7417606727",
    "https://www.freepages.genealogy.rootsweb.ancestry.com/~devalter/Audoir/dat311.htm",
    "https://www.legacy.com/obituaries/bostonglobe/obituary.aspx?n=lynne-caleigh-cali-healey&pid=121126008",
    "https://www.trails.com/city-trails.aspx?keyword=Quinault&state=WA",
    "https://www.siris-archives.si.edu/ipac20/ipac.jsp?&profile=all&source=~!siarchives&uri=full=3100001~!228467~!0",
    "https://www.umgoblue.com/index.php/2011/11/m-football-2011-michigan-football-returned-in-november-to-the-big-house-saturday-as-the-18th-ranked-wolverines-demolished-nebraskas-16th-ranked-cornhuskers-45-17",
    "https://www.bampfa.berkeley.edu/filmseries/british_crime_films",
    "https://www.corkin.com/listings/viewlisting.cfm?listingid=197998",
    "https://www.search.ancestry.com/search/db.aspx?dbid=8744",
    "https://www.nevadalabor.com/barbwire/barb08/barb8-31-08.html",
    "https://www.yelp.com/biz_photos/OfvbkMjwxLBWRMIMPuowaA?select=_-kkWK44L4eYORFdYg-I1w",
    "https://www.neoseeker.com/forums/49/t1639596-being-human-north-american-tv-series/",
    "https://www.yellowpages.lycos.com/search?what=asian+massage+parlor&where=Long+Branch%2C+New+Jersey",
    "https://www.archive.org/stream/memoriatechnica00greyiala/memoriatechnica00greyiala_djvu.txt",
    "https://www.sports-clubs.net/Sport/Clubs.aspx?County=Wiltshire",
    "https://www.worldcat.org/title/contemporary-black-american-playwrights-and-their-plays-a-biographical-directory-and-dramatic-index/oclc/16225458?referer=brief_results",
    "https://www.servinghistory.com/topics/Vincent_Meredith::sub::Family",
    "https://www.florida.rivals.com/cviewplayer.asp?Player=441505",
    "https://www.seattlebeerweek.com/events/366-Yard-Grand-Opening-SBW-Closing-",
    "https://www.cbc.ca/news/politics/inside-politics-blog/2011/11/liveblog-cbc-president-hubert-lacroix-talks-accountability-and-transparency-at-the-national-press-cl.html",
    "https://www.classmates.com/directory/public/memberprofile/list.htm?regId=8706231611",
    "https://www.facebook.com/pages/Head-Royce-School/105491302817425",
    "https://www.magicvalley.com/news/local/west-end/after-pilot-program-filer-seeks-feedback-on-recycling/article_4bb91626-05d6-11e1-89b2-001cc4c03286.html",
    "https://www.wwe.com/inside/titlehistory/divas/9009844",
    "https://www.ehow.com/how_7566057_reset-pontiac-grand-prix-2003.html",
    "https://www.amazon.co.uk/bernard-jordan-Books/s?ie=UTF8&keywords=bernard%20jordan&rh=n%3A266239%2Ck%3Abernard%20jordan&page=1",
    "https://www.findagrave.com/php/famous.php?page=date&globalSearchCriteria=&globalSearchType=&FSlastinitial=&FSstateid=&FSctf=&firstName=&lastName=&FScemeteryid=&FScityid=&FScountryid=&FScountyid=&FSstartrow=81&FSbirthmonth=&FSbirthday=&FSbirthyear=&FSdeathmonth=4&FSdeathday=25&FSdeathyear=",
    "https://www.footymania.com/player.phtml?playerID=3292",
    "https://www.1albums.com/album.php?album=&artist=Tyrese+(A.K.A.+Black-Ty)+Alter+Ego",
    "https://www.councilofelrond.com/modules.php?op=modload&name=Lit&file=index&req=viewarticle&lartid=21",
    "https://www.pibetaphi.org/pibetaphi/unt/chapters.aspx?id=9076",
    "https://www.ferommok.com/search.php?search=music+IVAN+VILLAZON+mentirosa+weight+10&action=search",
    "https://www.beemp3.com/download.php?file=4350089&song=Hieroglyphics+with+Souls+of+Mischief+-+cab+fare",
    "https://www.baseball-almanac.com/players/player.php?p=cannich01",
    "https://www.isthisyour.name/directory/fullnames/ma~theriault.htm",
    "https://www.familytreemaker.genealogy.com/users/n/o/r/Philip--Norfleet/BOOK-0001/0005-0006.html",
    "https://www.newsstore.fairfax.com.au/apps/viewDocument.ac?sy=afr&pb=all_ffx&dt=selectRange&dr=1month&so=relevance&sf=text&sf=headline&rc=10&rm=200&sp=brs&cls=1320&clsPage=1&docID=NCH100218164OP10T4HM",
    "https://www.findmyaccident.com/missouri/2011/09/19/nicholas-a-mcferren-20-dies-in-jackson-county-u-s-route-50-wreck/",
    "https://www.articles.sfgate.com/2008-10-21/entertainment/17137373_1_format-high-definition-radio-receivers-san-francisco-station",
    "https://www.wc.rootsweb.ancestry.com/cgi-bin/igm.cgi?op=REG&db=aubinroger&id=I7480",
    "https://www.videosurf.com/videos/miss+pettigrew+lives+day+full+movie",
    "https://www.songmeanings.net/songs/view/3530822107858724927/",
    "https://www.trulia.com/homes/California/Oakland/sold/2596731-721-55th-St-Oakland-CA-94609",
    "https://www.amazon.com/Notebooks-Laptop-Computers/b?ie=UTF8&node=565108",
    "https://www.ogi.edu/bme/news/dsp_news.cfm?news_id=7D819E37-B173-9075-5409509CF53506CD",
    "https://www.usdcoyotes.com/sports/mbball/release.asp?RELEASE_ID=6728",
    "https://www.m24digital.com/en/2009/11/25/tv-series-botineras-debuts-on-telefe/",
    "https://www.arcadja.com/auctions/en/harris_robert_george/artist/78516/",
    "https://www.destinations-uk.com/scotland.php?regionid=22&articletitle=Grampian%20(Aberdeenshire%20and%20Moray)",
    "https://www.offside442.blogspot.com/2010/02/worlds-top-ten-fat-footballers-revealed.html",
    "https://www.eventful.com/toronto/events/evening-jodi-picoult-and-live-music-ellen-wilber-/E0-001-036690597-8",
    "https://www.oliverwillis.com/2007/03/19/the-politicos-mike-allen-democrats-are-bloodthirsty-dogs-gushes-over-fox-news-matt-drudge-makes-fat-jokes-about-al-gore/",
    "https://www.thedetroiter.com/b2evoArt/blogs/index.php?blog=2&p=112&more=1&c=1&tb=1&pb=1",
    "https://www.descendantsdepierrelefebvre.blogspot.com/2008/08/jean-baptiste-lefebvre-marie-louise.html",
    "https://www.caryl.com/pressreleases.cfm?pressID=3390&homelink=1",
    "https://www.legis.state.sd.us/statutes/DisplayStatute.aspx?Type=StatuteChapter&Statute=34A-16",
    "https://www.dmvanswers.com/questions/1092/How-far-back-do-driving-records-go",
    "https://www.aveleyman.com/ActorCredit.aspx?ActorID=18212",
    "https://www.publicbackgroundchecks.com/searchresponse.aspx?view=NM&BasicString=AN%20HALE&IsAdvanceSearch=0",
    "https://www.playbill.com/news/article/154174-Mike-Farrell-Catherine-Hicks-Megan-Ward-Will-Be-Part-of-Blanks-Windows-On-The-World-Reading",
    "https://www.movies.nytimes.com/movie/387566/Honeymoon-Travels-Pvt-Ltd-/credits",
    "https://www.hockeydb.com/ihdb/stats/pdisplay.php?pid=92206",
    "https://www.espn.go.com/mlb/team/salaries/_/name/kc/kansas-city-royals",
    "https://www.dictionary.sensagent.com/list%c4%83+de+scriitori+rom%c3%a2ni/ro-ro/",
    "https://www.doctorcheckup.org/doctors/specialty/33-Ophthalmology?page=19",
    "https://www.beernews.org/2009/10/boulevard-brewing-orval-to-collaborate-on-imperial-pilsner/",
    "https://www.quod.lib.umich.edu/cgi/t/text/text-idx?c=moa;cc=moa;rgn=main;view=text;idno=AFC6228.0001.001",
    "https://www.ebay.com/sch/Fan-Apparel-Souvenirs-/24409/i.html?_nkw=kansas+city+athletics",
    "https://www.airforcetimes.com/news/2007/06/airforce_combatactionmedal_070608/",
    "https://www.store.livenation.com/Product.aspx?pc=FXAMOOS50436",
    "https://www.store.turningpointtickets.com/servlet/-strse-294/Corky-Laing-%26-The/Detail",
    "https://www.nz.answers.yahoo.com/question/index?qid=20080420091743AAol9CF",
    "https://www.factbites.com/topics/Dickie-Moore-(hockey-player)",
    "https://www.profilecanada.com/companydetail.cfm?company=762609_Ecole_Superieure_DE_Mode_Montral_QC",
    "https://www.nosorigines.org/genealogielistfirstname.aspx?ancestor=3&Family=Valois_2260&lng=en",
    "https://www.farmgoodsforkids.com/ou-04642-breyer-stablemates-red-stable-set.html",
    "https://www.tesla.liketelevision.com/liketelevision/tuner.php?channel=954&format=movie&theme=guide",
    "https://www.trenchreynolds.me/2010/08/26/michael-anthony-abbott-gets-six-years-for-being-a-kiddie-toucher/",
    "https://www.standard.net/stories/2011/11/02/warm-soles-credit-unions-help-provide-shoes-utah-children",
    "https://www.efloors.com/product/1437/6376/congoleum-connections-plank-classic-oak-harvest-glueless-floor-system-cn001.htm",
    "https://www.movieline.com/2011/09/jane-fonda-biographer-patricia-bosworth-talks-about-the-actress-her-movies-and-the-horny-prowess-of.php",
    "https://www.dailytelegraph.com.au/sport/rugby-gold/wallaby-five-eighth-quade-cooper-believes-his-six-month-lay-off-will-help-him-grow-as-a-footballer-and-a-person/story-fn8ti7yn-1226174003371",
    "https://www.railpictures.net/showphotos.php?railroad=Pacific%20Electric",
    "https://www.healthgrades.com/physician/dr-gregory-schlegel-ygbcw/",
    "https://www.broadwayworld.com/bwidb/productions/Avenue_X_9042/",
    "https://www.amazon.com/Mosaic-Select-Bob-Brookmeyer/dp/B000639WN2",
    "https://www.forums.fayettevillenc.com/cgi-bin/forums/ultimatebb.cgi?ubb=print_topic;f=1;t=002108",
    "https://www.youtube.com/watch?v=29s7OfHlDc0",
    "https://www.blindness.org/index.php?option=com_content&view=category&id=69&Itemid=139",
    "https://www.desjardins.com/en/votre_caisse/coordonnees/index.jsp?transit=81592278",
    "https://www.gossip.whyfame.com/jason-seagal-french-kisses-paul-rudd-on-snl-14426",
    "https://www.bestmalevideos.com/studio/authenticfootballers/",
    "https://www.youtube.com/watch?v=5S6m2W_L2WY",
    "https://www.mts.ca/portal/site/mts/menuitem.15bd89d0a465617cb60c5ee8408021a0/?vgnextoid=caefa7afa78f9210VgnVCM1000002a040f0aRCRD",
    "https://www.winnipegfreepress.com/canada/breakingnews/three-criminal-charges-for-tony-tomassi-ex-member-of-charest-cabinet-in-quebec-131548798.html",
    "https://www.jetphotos.net/showphotos.php?airline=Australia%20-%20Royal%20Australian%20Air%20Force%20(RAAF)",
    "https://www.harpers.org/subjects/RepublicanNationalConvention1976KansasCityMo",
    "https://www.ctidirectory.com/search/company.cfm?company=140971",
    "https://www.legacy.com/obituaries/hometownannapolis/obituary.aspx?n=richard-l-ay&pid=154036853&fhid=9944",
    "https://www.sports.espn.go.com/nhl/news/story?id=6713393",
    "https://www.soccernet.espn.go.com/news/story/_/id/945024/wolfsburg-sign-former-west-ham-midfielder-thomas-hitzlsperger",
    "https://www.vhpamuseum.org/companies/190ahc/190ahc.shtml",
    "https://www.boards.ancestry.netscape.com/thread.aspx?mv=flat&m=318&p=surnames.auger",
    "https://www.billboard.com/news/lady-antebellum-talk-album-s-huge-expectations-1005348862.story",
    "https://www.familyorigins.com/users/s/t/g/Bob--Stgelais/FAMO1-0001/d714.htm",
    "https://www.theoaklandpress.com/articles/2011/08/13/news/local_news/doc4e46f8a302044940945676.txt",
    "https://www.thecanadianencyclopedia.com/index.cfm?PgNm=TCE&Params=A1ARTA0008090",
    "https://www.nosorigines.qc.ca/genealogielistfirstname.aspx?ancestor=3&Family=Charbonneau_117&lng=en",
    "https://www.boards.ancestry.com/thread.aspx?mv=flat&m=2500&p=surnames.brock",
    https://www.courts.arkansas.gov/,0
https://www.teagames.com/games/fancypants/play.php,0
https://www.wn.com/1978_Stanley_Cup_Finals,0
https://www.onlinelibrary.wiley.com/journal/10.1111/(ISSN)1541-0064,0
https://www.findarticles.com/p/articles/mi_m1208/is_14_225/ai_72960661/,0
https://www.sertomadb.org/,0
https://www.quanloi.org/Maps/CMapBenCatPhuLoi.htm,0
https://www.movieweb.com/movie/paranorman/trailer,0
https://www.genforum.genealogy.com/bourcier/,0
https://www.metrolyrics.com/whats-next-lyrics-filter.html,0
https://www.w9wi.com/fmweb/frequencies/257.htm,0
https://www.rallye-info.com/driverprofile.asp?driver=1563,0
https://www.britishpathe.com/record.php?id=35644,0
https://www.movies.com/actors/dan-aykroyd/dan-aykroyd-movies/p281337,0
https://www.causes.com/causes/17420-multiple-sclerosis,0
https://www.classmates.com/directory/school/Bishop%20Guertin%20High%20School?org=8778,0
https://www.credit-agricole.com/en/Finance-and-Shareholders/Corporate-governance/Executive-committee/Deschenes-Alain,0
https://www.commons.wikimedia.org/wiki/Category:Television_channels,0
https://www.sportsmemorabilia.com/player/Mike_Bossy/index2.html,0
https://www.youtube.com/watch?v=Lg6xvp3iLnA,0
https://www.mvswanson.com/deadline-november-6th-joyce-elaine-grant-annual-juried-exhibition.html,0
https://www.dvdtalk.com/dvdsavant/s2936jack.html,0
https://www.en.wikipedia.org/wiki/Kaiser_Engineering_Building,0
https://www.last.fm/event/1936942+Roger+Hodgson+formerly+of+Supertramp+at+24th+Gatineau+Hot+Air+Ballon+Festival+with+Band%21,0
https://www.washingtonlife.com/directories/photos/?letter=S&name=SHARON-PERCY-ROCKEFELLER,0
https://www.ortegobirds.com/articles/banding/the-texas-bird-banding-team-activities-for-2005/,0
https://www.tokyograph.com/news/kato-shigeaki-joshima-shigeru-cast-as-brothers-in-comedy-play/,0
https://www.coursehero.com/textbooks/121297-Short-History-of-Syriac-Literature-Gorgias-Reprint/,0
https://www.hollywoodreporter.com/race/paramounts-jason-reitman-directed-young-231462,0
https://www.mujzpravodaj.cz/ObjectCategories.aspx?Category=ACTOR,0
https://www.facebook.com/pages/The-PeeChees/104009019636982,0
https://www.theochocolate.com/store/products/specialty-chocolate/cocoa-nibs,0
https://www.metalsucks.net/2011/02/14/slayer-touring-without-jeff-hanneman-wwwwweeeeeiiiiirrrrdddd/,0
https://www.fanpop.com/spots/nfl/images/17677888/title/new-arrowhead-stadium-wallpaper,0
https://www.youtube.com/watch?v=EbDP6QdXL0Q,0
https://www.divatv.co.uk/section_article.aspx?ProgrammeID=258678&ArticleID=1545,0
https://www.musicwn.com/browse.php?artist=Saafir,0
https://www.ncbuy.com/videos/oscars/short_live_1950.html,0
https://www.uk.ask.com/wiki/The_Detroit_Tigers_Radio_Network,0
https://www.facebook.com/manuchayer,0
https://www.en.wikipedia.org/wiki/Papineau-Leblanc_Bridge,0
https://www.sportsillustrated.cnn.com/2009/extramustard/hotclicks/10/14/blackhawks-ice-girls-kid-scores-amazing-hockey-goal/index.html,0
https://www.harborsquaregallery.com/?p=107,0
https://www.ultimategto.com/,0
https://www.top40.about.com/b/2010/11/05/black-eyed-peas-reveal-the-beginning-cover-art-and-more-album-details.htm,0
https://www.myspace.com/swampfoxphoto,0
https://www.thewatchstores.com/baume___mercier,0
https://www.wrestlingwiththetruth.com/jonathan-coachman-in-espn-news/,0
https://www.nme.com/artists/kate-and-anna-mcgarrigle,0
https://www.wwe.com/shows/summerslam/1988/results,0
https://www.robesonian.com/view/full_story/15058030/article-Lebeau-Locklear?instance=weddings_lead_story,0
https://www.amazon.com/Dracula-Jacob-Tierney/dp/B00062IYLE,0
https://www.top-topics.thefullwiki.org/African_American_pornographic_film_actors,0
https://www.famguardian1.org/Publications/InvisibleContracts/InvContrcts--06-AdmiraltyJurisdiction.htm,0
https://www.greatschools.org/california/oakland/208-Fruitvale-Elementary-School/,0
https://www.chemfeeds.com/cf-search.php?search=Howard%20Alper,0
https://www.facebook.com/people/Jocelyn-Black/511766893,0
https://www.booooooom.com/2011/10/11/drawn-and-quarterly-the-death-ray-by-daniel-clowes-giveaway/,0
https://www.iofilm.co.uk/fm/i/inside_im_dancing_2004_r3.shtml,0
https://www.ndtv.f1pulse.com/circuits/Circuit_Gilles_Villeneuve/3C3C/circuits_profile.aspx,0
https://www.rmclean.org/first_vestal/vestal65_gelfand.htm,0
https://www.bbc.co.uk/wales/southeast/halloffame/public_life/roy_jenkins.shtml,0
https://www.directory.kidookid.com/,0
https://www.uncoached.com/2009/03/12/shes-uncoachable-my-favorite-paraguayan-model-cindy-taylor/,0
https://www.mylife.com/c-544127967,0
https://www.internationalairportguide.com/mirabel_ymx.html,0
https://www.facebook.com/people/Luc-Desjardins/1834681663,0
https://www.artistdirect.com/artist/seasick-steve/3862324,0
https://www.sfgate.com/cgi-bin/object/article?f=/g/a/2011/07/04/July_Fourth.DTL&object=%2Fc%2Fpictures%2F2011%2F07%2F04%2Fba-fourth05-alam_0503730494.jpg,0
https://www.simple.wikipedia.org/wiki/New_Jersey_Devils,0
https://www.kotaku.com/5817994/the-renaissance-art-of-david-alvarez/gallery/1,0
https://www.csmasoniccenter.com/History.aspx,0
https://www.flatscreentvstands.biz/vizio-32-inch-class-xvt-series-full-1080p-120hz-lcd-hdtv-sv320xvt/,0
https://www.utexas.edu/courses/albright/courses/ptsp00/whigs.htm,0
https://www.amazon.com/Oxford-Handbook-Neuroethics-Handbooks/dp/0199570701,0
https://www.smaaahl.com/leagues/custom_page.cfm?leagueid=9165&clientid=3433&pageid=1618,0
https://www.historynet.com/turning-point-of-world-war-ii.htm,0
https://www.newzealand.com/travel/media/press-releases/2010/6/sport_nz-whites-out_press-release.cfm,0
https://www.gamasutra.com/php-bin/news_index.php?story=18568,0
https://www.english.turkcebilgi.com/Battle+of+Ticonderoga+(1759),0
https://www.ph.answers.yahoo.com/question/index?qid=20071111035323AA81g61,0
https://www.amazon.com/Happy-Be-Me-Self-Esteem-Elf-Help/dp/0870293559,0
https://www.servinghistory.com/topics/Jesse_Stone:_Innocents_Lost,0
https://www.virginiemontreal.com/,0
https://www.youtube.com/watch?v=tO-ljt_5fsM,0
https://www.churchesinlouisvillekentucky.com/,0
https://www.barnesandnoble.com/w/hunger-games-suzanne-collins/1100171585?ean=9780545229937,0
https://www.playgamesforum.com/topic/545-puppetshow-lost-town-oncoming-thrilling-hidden-object-game/page__s__bef292796f172d30e92ad7062ddf7c52,0
https://www.whois.domaintools.com/megafun.vn,0
https://www.youtube.com/watch?v=Ol2DedEhOGI,0
https://www.fantasyarts.net/robert_colescott_paintings.html,0
https://www.fightnext.com/video/K6AX7M4U1846/Josh-Koscheck-vs-Anthony-Johnson,0
https://www.youtube.com/watch?v=Z-YjSRsOSu0,0
https://www.dictionary.sensagent.com/requin/fr-fr/,0
https://www.onlinefringeepisodes.com/fringe-episode-11-season-1-bound-preview/,0
https://www.vitals.com/doctors/Dr_Richard_Burgoyne.html,0
https://www.listsearches.rootsweb.com/th/read/TETLEY/2001-10/1004202896,0
https://www.dshs.delaware.gov/employment.shtml,0
https://www.kellybadge.co.uk/Stock/navy.htm,0
https://www.cpihl.com/TeamPortalRoster.cfm?TeamID=4,0
https://www.encycl.opentopia.com/term/KKSF,0
https://www.eagle-eye-cherry.com/,0
https://www.calculatorplus.com/,0
https://www.cinetecadelfriuli.org/cdf/fototeca_collezioni/elenco_fototeca.html,0
https://www.thaiair.com/AIP_WOA/OfficeQueryResult,0
https://www.clevelandorchestra.com/about/education/community.aspx,0
https://www.cbc.ca/news/politics/canadavotes2011/features/votecompass/map/,0
https://www.thewho.org/tales/dennis.htm,0
https://www.cherrycreek-grill.com/,0
https://www.le1000.com/en/home.php,0
https://www.fortunecity.com/victorian/manet/132/caplis3x.htm,0
https://www.ckuik.com/Tigger,0
https://www.houseofnames.com/durocher-family-crest,0
https://www.talisaycitycollege.com/,0
https://www.missouritigerstickets.com/Venues/view/Kansas-State-Wildcats-Tickets,0
https://www.litigation-essentials.lexisnexis.com/webcd/app?action=DocumentDisplay&crawlid=1&doctype=cite&docid=14+Am.+U.+Int'l+L.+Rev.+1025&srctype=smi&srcid=3B15&key=de3195ee862ea8ea37193978073ebc90,0
https://www.en.wikipedia.org/wiki/Replicator_(band),0
https://www.findagrave.com/cgi-bin/fg.cgi?page=dfl&GRid=7243137,0
https://www.images.smu.edu/?page=postal,0
https://www.ticketwood.com/ticketsearch.php?EventSearchID=946296,0
https://www.torrenthound.com/search/les+aventures+extraordinaire+de+samy+,0
https://www.waymarking.com/waymarks/WM2ZPQ_USS_Potomac_AG_25_Oakland_CA,0
https://www.failedmessiah.typepad.com/failed_messiahcom/2011/04/orthodox-jew-mvp-of-womens-nit-basketball-tournament-456.html,0
https://www.video.hmongclip.com/?w=cqVca_2WkkI&title=MEIKOEvil-Food-Eater-Conchita-English-Lyrics-with-Kagamine-RinLen-Vocaloid-PV,0
https://www.campuscorner.kansascity.com/node/1990,0
https://www.topasianmodels.net/asian-model-brea-lynn-sexy-in-white-sheer,0
https://www.webanswers.com/legal/children-and-the-law/can-my-26-year-old-son-change-his-last-name-on-his-birth-certificate-and-if-so-how-3337a4,0
https://www.answers.com/topic/hindi,0
https://www.answers.com/topic/southwest-airlines-co,0
https://www.hfboards.com/showthread.php?t=1001315,0
https://www.uk.answers.yahoo.com/question/index?qid=20100614101121AAPsmqa,0
https://www.brainyhistory.com/topics/l/louis.html,0
https://www.thecanadianencyclopedia.com/index.cfm?PgNm=TCE&Params=A1ARTA0009062,0
https://www.pipl.com/directory/tags/Concordia,0
https://www.bleacherreport.com/users/303507-jim-orefice,0
https://www.imapbuilder.com/user-guide/Adding_Points.php,0
https://www.articles.latimes.com/keyword/jaron-rush/featured/4,0
https://www.absoluteastronomy.com/topics/Bret_Harte,0
https://www.ratemds.com/filecache/SelectDoctor.jsp?sid=60&searchBy=DLName&letter=G&startRow=300,0
https://www.shutterstock.com/pic-38320102/stock-vector-a-set-of-hand-drawn-red-hot-flames-and-fire-icon-design-elements-isolated-on-a-white-background.html,0
https://www.forum.alexanderpalace.org/index.php?topic=5048.0,0
https://www.ilike.com/artist/Chaka+Khan+%28with+Tom+Browne%29/track/Jamaica+Funk,0
https://www.neonlimelight.com/2010/05/23/new-music-preview-ne-yos-single-beautiful-monster-from-new-album-libra-scale/,0
https://www.legacy.com/obituaries/atlanta/obituary.aspx?n=evan-burak&pid=148054949&fhid=5314,0
https://www.amazon.com/Films-2002-England-Patriots-Video/dp/B0000AGWDN,0
https://www.amazon.com/s?ie=UTF8&rh=n%3A2858778011%2Cp_27%3AS.%20John%20Launer&field-author=S.%20John%20Launer&page=1,0
https://www.lyricsmode.com/lyrics/h/hey_say_jump/hitomi_no_screen.html,0
https://www.mylife.com/ron9729f,0





    ]

# ============================================================
# DIVERSE LEGITIMATE URLs 
# ============================================================

diverse_legitimate_urls = [
    # ========== EDUCATION (300) ==========
    "https://www.stanford.edu",
    "https://www.mit.edu",
    "https://www.harvard.edu",
    "https://www.yale.edu",
    "https://www.princeton.edu",
    "https://www.caltech.edu",
    "https://www.uchicago.edu",
    "https://www.upenn.edu",
    "https://www.columbia.edu",
    "https://www.cornell.edu",
    "https://www.duke.edu",
    "https://www.northwestern.edu",
    "https://www.jhu.edu",
    "https://www.dartmouth.edu",
    "https://www.brown.edu",
    "https://www.vanderbilt.edu",
    "https://www.rice.edu",
    "https://www.wustl.edu",
    "https://www.georgetown.edu",
    "https://www.emory.edu",
    "https://www.berkeley.edu",
    "https://www.ucla.edu",
    "https://www.usc.edu",
    "https://www.ucsd.edu",
    "https://www.ucsb.edu",
    "https://www.uci.edu",
    "https://www.ucr.edu",
    "https://www.ucsc.edu",
    "https://www.ucdavis.edu",
    "https://www.ucmerced.edu",
    "https://www.umich.edu",
    "https://www.wisc.edu",
    "https://www.illinois.edu",
    "https://www.psu.edu",
    "https://www.osu.edu",
    "https://www.umn.edu",
    "https://www.tamu.edu",
    "https://www.utexas.edu",
    "https://www.uw.edu",
    "https://www.gatech.edu",
    "https://www.cmu.edu",
    "https://www.ox.ac.uk",
    "https://www.cam.ac.uk",
    "https://www.imperial.ac.uk",
    "https://www.ucl.ac.uk",
    "https://www.ed.ac.uk",
    "https://www.manchester.ac.uk",
    "https://www.lse.ac.uk",
    "https://www.kcl.ac.uk",
    "https://www.bristol.ac.uk",
    "https://www.warwick.ac.uk",
    "https://www.apu.edu.my",
    "https://apspace.apu.edu.my",
    "https://www.nus.edu.sg",
    "https://www.ntu.edu.sg",
    "https://www.u-tokyo.ac.jp",
    "https://www.kyoto-u.ac.jp",
    "https://www.snu.ac.kr",
    "https://www.kaist.ac.kr",
    "https://www.tsinghua.edu.cn",
    "https://www.pku.edu.cn",
    "https://www.coursera.org",
    "https://www.edx.org",
    "https://www.udacity.com",
    "https://www.udemy.com",
    "https://www.khanacademy.org",
    "https://www.lynda.com",
    "https://www.skillshare.com",
    "https://www.pluralsight.com",
    "https://www.codecademy.com",
    "https://www.freecodecamp.org",
    
    # ========== AI/TECH (200) ==========
    "https://claude.ai",
    "https://chat.openai.com",
    "https://www.openai.com",
    "https://www.anthropic.com",
    "https://huggingface.co",
    "https://www.cohere.com",
    "https://www.midjourney.com",
    "https://www.stable-diffusion.ai",
    "https://www.replicate.com",
    "https://www.perplexity.ai",
    "https://www.character.ai",
    "https://www.jasper.ai",
    "https://www.copy.ai",
    "https://www.writesonic.com",
    "https://www.grammarly.com",
    "https://www.notion.so",
    "https://www.obsidian.md",
    "https://www.roamresearch.com",
    "https://www.evernote.com",
    "https://www.onenote.com",
    "https://www.todoist.com",
    "https://www.trello.com",
    "https://www.asana.com",
    "https://www.monday.com",
    "https://www.clickup.com",
    "https://www.airtable.com",
    "https://www.coda.io",
    "https://www.miro.com",
    "https://www.figma.com",
    "https://www.canva.com",
    "https://www.adobe.com",
    "https://www.sketch.com",
    "https://www.invisionapp.com",
    "https://www.framer.com",
    "https://www.webflow.com",
    "https://www.wordpress.com",
    "https://www.wix.com",
    "https://www.squarespace.com",
    "https://www.shopify.com",
    "https://www.stripe.com",
    "https://www.square.com",
    "https://www.paypal.com",
    "https://www.venmo.com",
    "https://www.cashapp.com",
    "https://www.revolut.com",
    "https://www.coinbase.com",
    "https://www.binance.com",
    "https://www.kraken.com",
    "https://www.gemini.com",
    "https://www.robinhood.com",
    
    # ========== NEWS (200) ==========
    "https://www.bbc.com",
    "https://www.bbc.co.uk",
    "https://www.cnn.com",
    "https://www.nytimes.com",
    "https://www.wsj.com",
    "https://www.washingtonpost.com",
    "https://www.theguardian.com",
    "https://www.telegraph.co.uk",
    "https://www.reuters.com",
    "https://www.apnews.com",
    "https://www.bloomberg.com",
    "https://www.ft.com",
    "https://www.economist.com",
    "https://www.forbes.com",
    "https://www.fortune.com",
    "https://www.businessinsider.com",
    "https://www.cnbc.com",
    "https://www.foxnews.com",
    "https://www.msnbc.com",
    "https://www.nbcnews.com",
    "https://www.abcnews.go.com",
    "https://www.cbsnews.com",
    "https://www.usatoday.com",
    "https://www.latimes.com",
    "https://www.chicagotribune.com",
    "https://www.sfgate.com",
    "https://www.seattletimes.com",
    "https://www.bostonglobe.com",
    "https://www.Miami herald.com",
    "https://www.time.com",
    "https://www.newsweek.com",
    "https://www.politico.com",
    "https://www.thehill.com",
    "https://www.axios.com",
    "https://www.vox.com",
    "https://www.vice.com",
    "https://www.buzzfeed.com",
    "https://www.huffpost.com",
    "https://www.theatlantic.com",
    "https://www.newyorker.com",
    "https://www.npr.org",
    "https://www.pbs.org",
    "https://www.aljazeera.com",
    "https://www.dw.com",
    "https://www.france24.com",
    "https://www.scmp.com",
    "https://www.straitstimes.com",
    "https://www.japantimes.co.jp",
    "https://www.thestar.com.my",
    "https://www.thetimes.co.uk",
    
    # ========== E-COMMERCE (200) ==========
    "https://www.amazon.com",
    "https://www.ebay.com",
    "https://www.walmart.com",
    "https://www.target.com",
    "https://www.bestbuy.com",
    "https://www.homedepot.com",
    "https://www.lowes.com",
    "https://www.costco.com",
    "https://www.samsclub.com",
    "https://www.kroger.com",
    "https://www.instacart.com",
    "https://www.doordash.com",
    "https://www.ubereats.com",
    "https://www.grubhub.com",
    "https://www.postmates.com",
    "https://www.seamless.com",
    "https://www.etsy.com",
    "https://www.aliexpress.com",
    "https://www.alibaba.com",
    "https://www.wish.com",
    "https://www.shein.com",
    "https://www.zara.com",
    "https://www.hm.com",
    "https://www.uniqlo.com",
    "https://www.gap.com",
    "https://www.oldnavy.com",
    "https://www.nordstrom.com",
    "https://www.macys.com",
    "https://www.sephora.com",
    "https://www.ulta.com",
    "https://www.nike.com",
    "https://www.adidas.com",
    "https://www.puma.com",
    "https://www.underarmour.com",
    "https://www.reebok.com",
    "https://www.lululemon.com",
    "https://www.athleta.com",
    "https://www.rei.com",
    "https://www.patagonia.com",
    "https://www.wayfair.com",
    "https://www.overstock.com",
    "https://www.ikea.com",
    "https://www.ashleyfurniture.com",
    "https://www.crateandbarrel.com",
    "https://www.potterybarn.com",
    "https://www.westelm.com",
    "https://www.cb2.com",
    "https://www.urbanoutfitters.com",
    "https://www.anthropologie.com",
    
    # ========== GOVERNMENT (200) ==========
    "https://www.usa.gov",
    "https://www.whitehouse.gov",
    "https://www.state.gov",
    "https://www.defense.gov",
    "https://www.justice.gov",
    "https://www.fbi.gov",
    "https://www.cia.gov",
    "https://www.nsa.gov",
    "https://www.dhs.gov",
    "https://www.nasa.gov",
    "https://www.irs.gov",
    "https://www.ssa.gov",
    "https://www.medicare.gov",
    "https://www.medicaid.gov",
    "https://www.healthcare.gov",
    "https://www.cdc.gov",
    "https://www.nih.gov",
    "https://www.fda.gov",
    "https://www.epa.gov",
    "https://www.dot.gov",
    "https://www.faa.gov",
    "https://www.tsa.gov",
    "https://www.fema.gov",
    "https://www.usps.com",
    "https://www.sec.gov",
    "https://www.ftc.gov",
    "https://www.fcc.gov",
    "https://www.cpsc.gov",
    "https://www.energy.gov",
    "https://www.ed.gov",
    "https://www.hhs.gov",
    "https://www.hud.gov",
    "https://www.va.gov",
    "https://www.usda.gov",
    "https://www.noaa.gov",
    "https://www.weather.gov",
    "https://www.census.gov",
    "https://www.bls.gov",
    "https://www.congress.gov",
    "https://www.senate.gov",
    "https://www.house.gov",
    "https://www.supremecourt.gov",
    "https://www.gov.uk",
    "https://www.parliament.uk",
    "https://www.nhs.uk",
    "https://www.gov.sg",
    "https://www.moh.gov.sg",
    "https://www.iras.gov.sg",
    "https://www.canada.ca",
    "https://www.australia.gov.au",
    
    # ========== SAAS/PRODUCTIVITY (200) ==========
    "https://www.slack.com",
    "https://www.zoom.us",
    "https://www.teams.microsoft.com",
    "https://www.meet.google.com",
    "https://www.webex.com",
    "https://www.gotomeeting.com",
    "https://www.discord.com",
    "https://www.telegram.org",
    "https://www.whatsapp.com",
    "https://www.signal.org",
    "https://www.messenger.com",
    "https://www.skype.com",
    "https://www.facetime.apple.com",
    "https://www.dropbox.com",
    "https://www.box.com",
    "https://www.onedrive.live.com",
    "https://drive.google.com",
    "https://www.icloud.com",
    "https://www.wetransfer.com",
    "https://www.sendspace.com",
    "https://www.mediafire.com",
    "https://www.mega.nz",
    "https://www.pcloud.com",
    "https://www.sync.com",
    "https://www.tresorit.com",
    "https://www.hubspot.com",
    "https://www.salesforce.com",
    "https://www.zendesk.com",
    "https://www.intercom.com",
    "https://www.freshdesk.com",
    "https://www.zoho.com",
    "https://www.mailchimp.com",
    "https://www.constantcontact.com",
    "https://www.sendinblue.com",
    "https://www.activecampaign.com",
    "https://www.convertkit.com",
    "https://www.aweber.com",
    "https://www.getresponse.com",
    "https://www.drip.com",
    "https://www.calendly.com",
    "https://www.doodle.com",
    "https://www.acuityscheduling.com",
    "https://www.appointlet.com",
    "https://www.loom.com",
    "https://www.vimeo.com",
    "https://www.wistia.com",
    "https://www.vidyard.com",
    "https://www.typeform.com",
    "https://www.jotform.com",
    
    # ========== POPULAR/SOCIAL (300) ==========
    "https://www.google.com",
    "https://www.youtube.com",
    "https://www.facebook.com",
    "https://www.instagram.com",
    "https://www.twitter.com",
    "https://www.x.com",
    "https://www.tiktok.com",
    "https://www.snapchat.com",
    "https://www.pinterest.com",
    "https://www.linkedin.com",
    "https://www.reddit.com",
    "https://www.tumblr.com",
    "https://www.quora.com",
    "https://www.medium.com",
    "https://www.substack.com",
    "https://www.blogger.com",
    "https://www.wordpress.org",
    "https://www.github.com",
    "https://www.gitlab.com",
    "https://www.bitbucket.org",
    "https://www.stackoverflow.com",
    "https://www.stackexchange.com",
    "https://www.dev.to",
    "https://www.hashnode.com",
    "https://www.hackernews.com",
    "https://www.producthunt.com",
    "https://www.behance.net",
    "https://www.dribbble.com",
    "https://www.awwwards.com",
    "https://www.wikipedia.org",
    "https://www.wikihow.com",
    "https://www.imdb.com",
    "https://www.rottentomatoes.com",
    "https://www.metacritic.com",
    "https://www.letterboxd.com",
    "https://www.goodreads.com",
    "https://www.audible.com",
    "https://www.spotify.com",
    "https://www.apple.com/apple-music",
    "https://www.soundcloud.com",
    "https://www.pandora.com",
    "https://www.tidal.com",
    "https://www.deezer.com",
    "https://www.netflix.com",
    "https://www.hulu.com",
    "https://www.disneyplus.com",
    "https://www.hbomax.com",
    "https://www.primevideo.com",
    "https://www.paramountplus.com",
    "https://www.peacocktv.com",
    "https://www.crunchyroll.com",
    
    # ========== RANDOM LEGITIMATE (400) ==========
    "https://www.yelp.com",
    "https://www.tripadvisor.com",
    "https://www.booking.com",
    "https://www.expedia.com",
    "https://www.airbnb.com",
    "https://www.hotels.com",
    "https://www.kayak.com",
    "https://www.priceline.com",
    "https://www.orbitz.com",
    "https://www.hotwire.com",
    "https://www.united.com",
    "https://www.delta.com",
    "https://www.aa.com",
    "https://www.southwest.com",
    "https://www.jetblue.com",
    "https://www.alaska.com",
    "https://www.spirit.com",
    "https://www.frontier.com",
    "https://www.ryanair.com",
    "https://www.easyjet.com",
    "https://www.britishairways.com",
    "https://www.lufthansa.com",
    "https://www.emirates.com",
    "https://www.qatarairways.com",
    "https://www.singaporeair.com",
    "https://www.cathaypacific.com",
    "https://www.ana.co.jp",
    "https://www.jal.co.jp",
    "https://www.krisflyer.com",
    "https://www.marriott.com",
    "https://www.hilton.com",
    "https://www.hyatt.com",
    "https://www.ihg.com",
    "https://www.accorhotels.com",
    "https://www.radisson.com",
    "https://www.wyndham.com",
    "https://www.choicehotels.com",
    "https://www.bestwestern.com",
    "https://www.fourseasons.com",
    "https://www.ritzcarlton.com",
    "https://www.starwoodhotels.com",
    "https://www.geeksforgeeks.org",
    "https://www.w3schools.com",
    "https://www.tutorialspoint.com",
    "https://www.javatpoint.com",
    "https://www.programiz.com",
    "https://www.codecademy.com",
    "https://www.leetcode.com",
    "https://www.hackerrank.com",
    "https://www.codewars.com",
    "https://www.topcoder.com",
    
    # ========== ADDITIONAL EDUCATION (200) ==========
    "https://www.bu.edu", "https://www.northeastern.edu", "https://www.nyu.edu",
    "https://www.rutgers.edu", "https://www.purdue.edu", "https://www.ufl.edu",
    "https://www.asu.edu", "https://www.arizona.edu", "https://www.uoregon.edu",
    "https://www.wsu.edu", "https://www.unl.edu", "https://www.iastate.edu",
    "https://www.lsu.edu", "https://www.tulane.edu", "https://www.uga.edu",
    "https://www.clemson.edu", "https://www.ncsu.edu", "https://www.vt.edu",
    "https://www.umd.edu", "https://www.temple.edu", "https://www.pitt.edu",
    "https://www.syr.edu", "https://www.uconn.edu", "https://www.uvm.edu",
    "https://www.utoronto.ca", "https://www.ubc.ca", "https://www.mcgill.ca",
    "https://www.anu.edu.au", "https://www.sydney.edu.au", "https://www.unimelb.edu.au",
    "https://www.ethz.ch", "https://www.epfl.ch", "https://www.uzh.ch",
    "https://www.ku.dk", "https://www.dtu.dk", "https://www.uva.nl",
    "https://www.masterclass.com", "https://www.datacamp.com", "https://www.treehouse.com",
    "https://www.codecademy.com", "https://www.udemy.com", "https://www.pluralsight.com",
    
    # ========== ADDITIONAL TECH/AI (400) ==========
    "https://www.nvidia.com", "https://www.amd.com", "https://www.intel.com",
    "https://www.dell.com", "https://www.hp.com", "https://www.lenovo.com",
    "https://www.asus.com", "https://www.acer.com", "https://www.msi.com",
    "https://www.logitech.com", "https://www.razer.com", "https://www.corsair.com",
    "https://www.oracle.com", "https://www.sap.com", "https://www.vmware.com",
    "https://www.redhat.com", "https://www.ubuntu.com", "https://www.debian.org",
    "https://www.python.org", "https://www.java.com", "https://www.nodejs.org",
    "https://www.npmjs.com", "https://www.php.net", "https://www.golang.org",
    "https://www.rust-lang.org", "https://www.swift.org", "https://www.kotlin.org",
    "https://www.mongodb.com", "https://www.postgresql.org", "https://www.mysql.com",
    "https://www.redis.io", "https://www.elastic.co", "https://www.neo4j.com",
    "https://www.docker.com", "https://www.kubernetes.io", "https://www.terraform.io",
    "https://www.ansible.com", "https://www.jenkins.io", "https://www.circleci.com",
    "https://www.aws.amazon.com", "https://cloud.google.com", "https://azure.microsoft.com",
    "https://www.digitalocean.com", "https://www.heroku.com", "https://www.netlify.com",
    "https://www.vercel.com", "https://www.cloudflare.com", "https://www.fastly.com",
    "https://www.cisco.com", "https://www.juniper.net", "https://www.arista.com",
    "https://www.splunk.com", "https://www.datadog.com", "https://www.newrelic.com",
    "https://www.tableau.com", "https://www.qlik.com", "https://www.looker.com",
    "https://www.atlassian.com", "https://www.jira.com", "https://www.confluence.com",
    "https://www.bitbucket.com", "https://www.sourcetree.com",
    "https://www.brave.com", "https://www.vivaldi.com", "https://www.edge.microsoft.com",
    "https://www.firefox.com", "https://www.chrome.google.com", "https://www.safari.com",
    "https://www.opera.com", "https://www.tor.org", "https://www.duckduckgo.com",
    "https://www.startpage.com", "https://www.qwant.com", "https://www.ecosia.org",
    
    # ========== ADDITIONAL NEWS (200) ==========
    "https://www.dailymail.co.uk", "https://www.independent.co.uk", "https://www.express.co.uk",
    "https://www.thesun.co.uk", "https://www.standard.co.uk", "https://www.metro.co.uk",
    "https://www.lemonde.fr", "https://www.lefigaro.fr", "https://www.elpais.com",
    "https://www.elmundo.es", "https://www.corriere.it", "https://www.repubblica.it",
    "https://www.spiegel.de", "https://www.faz.net", "https://www.nrc.nl",
    "https://www.asahi.com", "https://www.yomiuri.co.jp", "https://www.nikkei.com",
    "https://www.chinadaily.com.cn", "https://www.koreaherald.com",
    "https://www.smh.com.au", "https://www.theage.com.au", "https://www.nzherald.co.nz",
    "https://www.bangkokpost.com", "https://www.thejakartapost.com",
    "https://www.dawn.com", "https://www.thenews.com.pk", "https://www.tribuneindia.com",
    "https://www.thetimes.com", "https://www.sundaytimes.co.uk",
    "https://www.spectator.co.uk", "https://www.newstatesman.com",
    
    # ========== ADDITIONAL E-COMMERCE (400) ==========
    "https://www.flipkart.com", "https://www.myntra.com", "https://www.lazada.com",
    "https://www.shopee.com", "https://www.tokopedia.com", "https://www.jd.com",
    "https://www.taobao.com", "https://www.tmall.com", "https://www.rakuten.com",
    "https://www.zalando.com", "https://www.asos.com", "https://www.boohoo.com",
    "https://www.next.co.uk", "https://www.marksandspencer.com", "https://www.johnlewis.com",
    "https://www.selfridges.com", "https://www.harrods.com",
    "https://www.bloomingdales.com", "https://www.saksfifthavenue.com", "https://www.neimanmarcus.com",
    "https://www.forever21.com", "https://www.abercrombie.com", "https://www.ae.com",
    "https://www.pacsun.com", "https://www.zumiez.com",
    "https://www.dickssportinggoods.com", "https://www.academy.com", "https://www.backcountry.com",
    "https://www.jcrew.com", "https://www.bananarepublic.com", "https://www.loft.com",
    "https://www.victoriassecret.com", "https://www.bathandbodyworks.com",
    "https://www.lookfantastic.com", "https://www.cultbeauty.co.uk", "https://www.dermstore.com",
    "https://www.wayfair.com", "https://www.overstock.com", "https://www.westelm.com",
    "https://www.cb2.com", "https://www.urbanoutfitters.com", "https://www.anthropologie.com",
    "https://www.freepeople.com", "https://www.tedbaker.com", "https://www.reiss.com",
    "https://www.allsaints.com", "https://www.karenmillen.com", "https://www.hobbs.com",
    "https://www.whitestuff.com", "https://www.phase-eight.com",
    "https://www.joules.com", "https://www.boden.co.uk", "https://www.seasalt.com",
    "https://www.fatface.com", "https://www.jhilburn.com", "https://www.bonobos.com",
    "https://www.untuckit.com", "https://www.ministryofsupply.com",
    "https://www.mizzen-main.com", "https://www.rhone.com", "https://www.vuoriclothing.com",
    "https://www.outdoor voices.com", "https://www.allbirds.com", "https://www.rothys.com",
    "https://www.everlane.com", "https://www.reformation.com", "https://www.girlfriend.com",
    
    # ========== ADDITIONAL GOVERNMENT (150) ==========
    "https://www.ca.gov", "https://www.texas.gov", "https://www.florida.gov",
    "https://www.ny.gov", "https://www.illinois.gov", "https://www.pa.gov",
    "https://www.ohio.gov", "https://www.georgia.gov", "https://www.nc.gov",
    "https://www.michigan.gov", "https://www.virginia.gov", "https://www.washington.gov",
    "https://www.arizona.gov", "https://www.massachusetts.gov",
    "https://www.tennessee.gov", "https://www.indiana.gov", "https://www.missouri.gov",
    "https://www.maryland.gov", "https://www.wisconsin.gov", "https://www.colorado.gov",
    "https://www.minnesota.gov", "https://www.southcarolina.gov",
    "https://www.oregon.gov", "https://www.connecticut.gov", "https://www.utah.gov",
    "https://www.nevada.gov", "https://www.kansas.gov", "https://www.nebraska.gov",
    "https://www.hawaii.gov", "https://www.maine.gov", "https://www.montana.gov",
    "https://www.delaware.gov", "https://www.alaska.gov", "https://www.wyoming.gov",
    "https://www.lacity.org", "https://www.chicago.gov", "https://www.phila.gov",
    "https://www.phoenix.gov", "https://www.sandiego.gov", "https://www.dallas.gov",
    "https://www.houston.gov", "https://www.sanantonio.gov", "https://www.austin.gov",
    "https://www.seattle.gov", "https://www.denver.gov", "https://www.boston.gov",
    
    # ========== ADDITIONAL SAAS (300) ==========
    "https://www.wrike.com", "https://www.smartsheet.com", "https://www.basecamp.com",
    "https://www.teamwork.com", "https://www.meistertask.com", "https://www.podio.com",
    "https://www.linear.app", "https://www.shortcut.com", "https://www.height.app",
    "https://www.pivotaltracker.com", "https://www.targetprocess.com",
    "https://www.pagerduty.com", "https://www.opsgenie.com", "https://www.victorops.com",
    "https://www.appdynamics.com", "https://www.dynatrace.com",
    "https://www.sentry.io", "https://www.rollbar.com", "https://www.bugsnag.com",
    "https://www.logrocket.com", "https://www.fullstory.com",
    "https://www.hotjar.com", "https://www.crazyegg.com", "https://www.mouseflow.com",
    "https://www.heap.io", "https://www.mixpanel.com", "https://www.amplitude.com",
    "https://www.segment.com", "https://www.rudderstack.com",
    "https://www.optimizely.com", "https://www.vwo.com", "https://www.abtasty.com",
    "https://www.launchdarkly.com", "https://www.split.io",
    "https://www.unbounce.com", "https://www.instapage.com", "https://www.leadpages.net",
    "https://www.clickfunnels.com", "https://www.kartra.com", "https://www.kajabi.com",
    "https://www.teachable.com", "https://www.thinkific.com", "https://www.podia.com",
    "https://www.gumroad.com", "https://www.patreon.com", "https://www.ko-fi.com",
    "https://www.buymeacoffee.com", "https://www.memberful.com", "https://www.substack.com",
    "https://www.ghost.org", "https://www.medium.com", "https://www.beehiiv.com",
    "https://www.convertkit.com", "https://www.aweber.com", "https://www.getresponse.com",
    "https://www.activecampaign.com", "https://www.constantcontact.com",
    "https://www.sendinblue.com", "https://www.omnisend.com", "https://www.klaviyo.com",
    "https://www.drip.com", "https://www.autopilot.com", "https://www.customerio.com",
    
    # ========== ADDITIONAL POPULAR/SOCIAL (350) ==========
    "https://www.twitch.tv", "https://www.kick.com", "https://www.dlive.tv",
    "https://www.mixer.com", "https://www.caffeine.tv",
    "https://www.discord.gg", "https://www.guilded.gg", "https://www.revolt.chat",
    "https://www.teamspeak.com", "https://www.mumble.info",
    "https://www.viber.com", "https://www.line.me", "https://www.wechat.com",
    "https://www.kakao.com", "https://www.qq.com", "https://www.weibo.com",
    "https://www.vk.com", "https://www.ok.ru", "https://www.yandex.ru",
    "https://www.pixiv.net", "https://www.niconico.jp", "https://www.bilibili.com",
    "https://www.douyin.com", "https://www.kuaishou.com",
    "https://www.meetup.com", "https://www.eventbrite.com", "https://www.peatix.com",
    "https://www.deviantart.com", "https://www.artstation.com", "https://www.500px.com",
    "https://www.flickr.com", "https://www.unsplash.com", "https://www.pexels.com",
    "https://www.pixabay.com", "https://www.shutterstock.com",
    "https://www.telegram.org", "https://www.signal.org", "https://www.element.io",
    "https://www.sessions.com", "https://www.wire.com", "https://www.threema.ch",
    "https://www.mastodon.social", "https://www.diaspora.social", "https://www.minds.com",
    "https://www.gab.com", "https://www.parler.com", "https://www.gettr.com",
    "https://www.truthsocial.com", "https://www.rumble.com", "https://www.bitchute.com",
    "https://www.odysee.com", "https://www.lbry.tv", "https://www.brighteon.com",
    
    # ========== ADDITIONAL DOMAINS BATCH 1 (300) ==========
    "https://www.apple.com", "https://www.microsoft.com", "https://www.meta.com",
    "https://www.alphabet.com", "https://www.tesla.com", "https://www.spacex.com",
    "https://www.airbus.com", "https://www.boeing.com", "https://www.lockheedmartin.com",
    "https://www.northropgrumman.com", "https://www.raytheon.com", "https://www.ge.com",
    "https://www.siemens.com", "https://www.honeywell.com", "https://www.3m.com",
    "https://www.caterpillar.com", "https://www.deere.com", "https://www.ford.com",
    "https://www.gm.com", "https://www.toyota.com", "https://www.honda.com",
    "https://www.nissan.com", "https://www.mazda.com", "https://www.subaru.com",
    "https://www.bmw.com", "https://www.mercedes-benz.com", "https://www.audi.com",
    "https://www.volkswagen.com", "https://www.porsche.com", "https://www.ferrari.com",
    "https://www.lamborghini.com", "https://www.maserati.com", "https://www.bugatti.com",
    "https://www.rolls-royce.com", "https://www.bentley.com", "https://www.astonmartin.com",
    "https://www.jaguar.com", "https://www.landrover.com", "https://www.volvo.com",
    "https://www.saab.com", "https://www.peugeot.com", "https://www.renault.com",
    "https://www.citroen.com", "https://www.fiat.com", "https://www.alfa-romeo.com",
    "https://www.hyundai.com", "https://www.kia.com", "https://www.genesis.com",
    "https://www.lexus.com", "https://www.infiniti.com", "https://www.acura.com",
    "https://www.cadillac.com", "https://www.lincoln.com", "https://www.buick.com",
    "https://www.chevrolet.com", "https://www.dodge.com", "https://www.jeep.com",
    "https://www.ram.com", "https://www.chrysler.com", "https://www.gmc.com",
    "https://www.coca-cola.com", "https://www.pepsi.com", "https://www.nestle.com",
    "https://www.unilever.com", "https://www.pg.com", "https://www.jnj.com",
    "https://www.pfizer.com", "https://www.merck.com", "https://www.abbvie.com",
    "https://www.roche.com", "https://www.novartis.com", "https://www.sanofi.com",
    "https://www.gsk.com", "https://www.astrazeneca.com", "https://www.bayer.com",
    "https://www.boehringer-ingelheim.com", "https://www.takeda.com", "https://www.lilly.com",
    "https://www.bristol-myers-squibb.com", "https://www.amgen.com", "https://www.gilead.com",
    "https://www.biogen.com", "https://www.regeneron.com", "https://www.vertex.com",
    "https://www.moderna.com", "https://www.biontech.com", "https://www.illumina.com",
    
    # ========== ADDITIONAL DOMAINS BATCH 2 (300) ==========
    "https://www.chase.com", "https://www.bankofamerica.com", "https://www.wellsfargo.com",
    "https://www.citibank.com", "https://www.usbank.com", "https://www.capitalone.com",
    "https://www.pnc.com", "https://www.ally.com", "https://www.discover.com",
    "https://www.amex.com", "https://www.visa.com", "https://www.mastercard.com",
    "https://www.jpmorganchase.com", "https://www.goldmansachs.com", "https://www.morganstanley.com",
    "https://www.bankofengland.co.uk", "https://www.hsbc.com", "https://www.barclays.com",
    "https://www.lloyds.com", "https://www.natwest.com", "https://www.nationwide.co.uk",
    "https://www.santander.com", "https://www.bnpparibas.com", "https://www.credit-agricole.com",
    "https://www.societegenerale.com", "https://www.deutschebank.com", "https://www.commerzbank.com",
    "https://www.unicredit.eu", "https://www.ing.com", "https://www.abn-amro.com",
    "https://www.ubs.com", "https://www.credit-suisse.com", "https://www.mizuho-fg.com",
    "https://www.mitsubishi.com", "https://www.smfg.co.jp", "https://www.bochk.com",
    "https://www.icbc.com.cn", "https://www.ccb.com", "https://www.abchina.com",
    "https://www.bankcomm.com", "https://www.cmbchina.com", "https://www.cibc.com",
    "https://www.td.com", "https://www.scotiabank.com", "https://www.bmo.com",
    "https://www.rbc.com", "https://www.commbank.com.au", "https://www.westpac.com.au",
    "https://www.anz.com", "https://www.nab.com.au", "https://www.kiwibank.co.nz",
    "https://www.state farm.com", "https://www.geico.com", "https://www.progressive.com",
    "https://www.allstate.com", "https://www.libertymutual.com", "https://www.nationwide.com",
    "https://www.usaa.com", "https://www.farmers.com", "https://www.travelers.com",
    "https://www.metlife.com", "https://www.prudential.com", "https://www.manulife.com",
    "https://www.sunlife.com", "https://www.aiglife.com", "https://www.allianz.com",
    "https://www.axa.com", "https://www.zurich.com", "https://www.aviva.com",
    "https://www.legalandgeneral.com", "https://www.standardlife.com",
    
    # ========== ADDITIONAL DOMAINS BATCH 3 (300) ==========
    "https://www.hiltonhonors.com", "https://www.marriottbonvoy.com", "https://www.ihgrewardsclub.com",
    "https://www.accor.com", "https://www.wyndhamrewards.com", "https://www.choice privileges.com",
    "https://www.omnihotels.com", "https://www.waldorfastoria.com", "https://www.conradhotels.com",
    "https://www.doubletree.com", "https://www.hamptoninn.com", "https://www.embassysuites.com",
    "https://www.homewoodsuites.com", "https://www.hampton.com", "https://www.curio.com",
    "https://www.autograph-hotels.com", "https://www.tributeportfolio.com",
    "https://www.design-hotels.com", "https://www.sixsenses.com", "https://www.anantara.com",
    "https://www.banyan-tree.com", "https://www.mandarinoriental.com", "https://www.peninsula.com",
    "https://www.shangri-la.com", "https://www.fairmont.com", "https://www.swissotel.com",
    "https://www.raffles.com", "https://www.sofitel.com", "https://www.pullmanhotels.com",
    "https://www.mgm-resorts.com", "https://www.caesars.com", "https://www.wynn.com",
    "https://www.bellagio.com", "https://www.aria.com", "https://www.cosmopolitan.com",
    "https://www.venetian.com", "https://www.palazzo.com", "https://www.mandalay bay.com",
    "https://www.luxor.com", "https://www.excalibur.com", "https://www.newyork-newyork.com",
    "https://www.parisparis.com", "https://www.caesarspalace.com", "https://www.flamingolv.com",
    "https://www.harrahs.com", "https://www.ballys.com", "https://www.tropicana.net",
    "https://www.eldorado-reno.com", "https://www.goldennugget.com", "https://www.thepalms.com",
    "https://www.redrock.sclv.com", "https://www.greenvally ranch.com", "https://www.stationcasinos.com",
    "https://www.suncoastcasino.com", "https://www.redrockcasino.com",
    "https://www.palms.com", "https://www.silvertonlasvegas.com",
    
    # ========== ADDITIONAL DOMAINS BATCH 4 (300) ==========
    "https://www.cnet.com", "https://www.zdnet.com", "https://www.techcrunch.com",
    "https://www.theverge.com", "https://www.wired.com", "https://www.engadget.com",
    "https://www.gizmodo.com", "https://www.ars-technica.com", "https://www.anandtech.com",
    "https://www.tomshardware.com", "https://www.pcmag.com", "https://www.pcworld.com",
    "https://www.computerworld.com", "https://www.infoworld.com", "https://www.networkworld.com",
    "https://www.itworld.com", "https://www.cio.com", "https://www.csoonline.com",
    "https://www.securityweek.com", "https://www.darkreading.com", "https://www.krebs-on-security.com",
    "https://www.schneier.com", "https://www.threatpost.com", "https://www.bleepingcomputer.com",
    "https://www.hackernoon.com", "https://www.techradar.com", "https://www.t3.com",
    "https://www.stuff.tv", "https://www.trustedreviews.com", "https://www.expertreviews.com",
    "https://www.whathifi.com", "https://www.digitaltrends.com", "https://www.cnet.co.uk",
    "https://www.pocket-lint.com", "https://www.techadviser.com", "https://www.macworld.com",
    "https://www.macworld.co.uk", "https://www.imore.com", "https://www.macrumors.com",
    "https://www.9to5mac.com", "https://www.appleinsider.com", "https://www.cultof mac.com",
    "https://www.androidcentral.com", "https://www.androidauthority.com", "https://www.androidpolice.com",
    "https://www.androidpit.com", "https://www.phonearena.com", "https://www.gsmarena.com",
    "https://www.notebookcheck.net", "https://www.laptopmag.com", "https://www.ultrabookreview.com",
    "https://www.notebookreview.com", "https://www.mobiletechreview.com",
    "https://www.slashgear.com", "https://www.makeuseof.com", "https://www.howtogeek.com",
    "https://www.lifehacker.com", "https://www.digitalspy.com", "https://www.techspot.com",
    "https://www.guru3d.com", "https://www.overclock.net", "https://www.bit-tech.net",
    "https://www.hardocp.com", "https://www.legitreviews.com", "https://www.tweaktown.com",
    
    # ========== ADDITIONAL DOMAINS BATCH 5 (300) ==========
    "https://www.espn.com", "https://www.espn.co.uk", "https://www.cbssports.com",
    "https://www.nbcsports.com", "https://www.foxsports.com", "https://www.bleacherreport.com",
    "https://www.sbnation.com", "https://www.the athletic.com", "https://www.sportingnews.com",
    "https://www.goal.com", "https://www.uefa.com", "https://www.fifa.com",
    "https://www.nfl.com", "https://www.nba.com", "https://www.mlb.com",
    "https://www.nhl.com", "https://www.mls.com", "https://www.premierleague.com",
    "https://www.laliga.com", "https://www.bundesliga.com", "https://www.seriea.com",
    "https://www.ligue1.com", "https://www.formula1.com", "https://www.motogp.com",
    "https://www.nascar.com", "https://www.indycar.com", "https://www.wimbledon.com",
    "https://www.usopen.org", "https://www.rolandgarros.com", "https://www.ausopen.com",
    "https://www.pgatour.com", "https://www.lpga.com", "https://www.europeantour.com",
    "https://www.ryder cup.com", "https://www.themasters.com", "https://www.usga.org",
    "https://www.wwe.com", "https://www.ufc.com", "https://www.bellator.com",
    "https://www.boxing news.com", "https://www.olympic.org", "https://www.paralympic.org",
    "https://www.commonwealthgames.com", "https://www.asiangames.com",
    "https://www.pandora.com", "https://www.last.fm", "https://www.bandcamp.com",
    "https://www.mixcloud.com", "https://www.audiomack.com", "https://www.8tracks.com",
    "https://www.tunein.com", "https://www.iheart.com", "https://www.radio.com",
    "https://www.bbc.co.uk/sounds", "https://www.bbc.co.uk/iplayer", "https://www.itv.com",
    "https://www.channel4.com", "https://www.sky.com", "https://www.virginmedia.com",
    "https://www.bt.com", "https://www.ee.co.uk", "https://www.vodafone.co.uk",
    "https://www.three.co.uk", "https://www.o2.co.uk", "https://www.verizon.com",
    "https://www.att.com", "https://www.t-mobile.com", "https://www.sprint.com",
    "https://www.metropcs.com", "https://www.boost mobile.com", "https://www.cricket wireless.com",
    
    # ========== ADDITIONAL DOMAINS BATCH 6 (300) ==========
    "https://www.indeed.com", "https://www.monster.com", "https://www.careerbuilder.com",
    "https://www.glassdoor.com", "https://www.ziprecruiter.com", "https://www.simplyhired.com",
    "https://www.dice.com", "https://www.ladders.com", "https://www.snagajob.com",
    "https://www.totaljobs.com", "https://www.reed.co.uk", "https://www.cv-library.co.uk",
    "https://www.jobsite.co.uk", "https://www.guardian jobs.com", "https://www.totaljobs.com",
    "https://www.seek.com.au", "https://www.careerone.com.au", "https://www.jora.com",
    "https://www.gumtree.com.au", "https://www.trademe.co.nz", "https://www.workopolis.com",
    "https://www.eluta.ca", "https://www.monster.ca", "https://www.job bank.gc.ca",
    "https://www.infojobs.net", "https://www.infoempleo.com", "https://www.jobrapido.com",
    "https://www.jobbydoo.com", "https://www.trovit.com", "https://www.mitula.com",
    "https://www.naukri.com", "https://www.monsterindia.com", "https://www.shine.com",
    "https://www.timesjobs.com", "https://www.fresher sworld.com", "https://www.jobstreet.com",
    "https://www.jobsdb.com", "https://www.recruit.co.jp", "https://www.rikunabi.com",
    "https://www.mynavi.jp", "https://www.doda.jp", "https://www.en-japan.com",
    "https://www.zhaopin.com", "https://www.51job.com", "https://www.liepin.com",
    "https://www.chinahr.com", "https://www.lagou.com", "https://www.boss.com",
    "https://www.angellist.com", "https://www.wellfound.com", "https://www.ycombinator.com",
    "https://www.crunchbase.com", "https://www.pitchbook.com", "https://www.cbinsights.com",
    "https://www.techstars.com", "https://www.500.co", "https://www.sequoiacap.com",
    "https://www.a16z.com", "https://www.greylock.com", "https://www.benchmark.com",
    "https://www.kleiner perkins.com", "https://www.accel.com", "https://www.indexventures.com",
    "https://www.battery ventures.com", "https://www.nea.com", "https://www.spark capital.com",
]

# ========================================================================
# EDUCATIONAL URLs - Sites ABOUT security/phishing (contain "suspicious" keywords)
# ========================================================================
# These URLs contain keywords like "phishing", "malicious", "verify", "account"
# but are from TRUSTED sources teaching about security
educational_urls = [
    # Cybersecurity Blogs (20)
    "https://www.comparitech.com/blog/vpn-privacy/what-are-malicious-websites/",
    "https://www.kaspersky.com/resource-center/threats/what-is-phishing",
    "https://www.malwarebytes.com/blog/threats/phishing",
    "https://www.norton.com/internetsecurity-online-scams-phishing-scams.html",
    "https://www.mcafee.com/learn/what-is-phishing",
    "https://www.wired.com/story/phishing-attacks-security/",
    "https://www.cnet.com/news/privacy/avoid-phishing-scams/",
    "https://arstechnica.com/information-technology/phishing-scam-alert/",
    
    # Banking Security Pages (30)
    "https://www.chase.com/personal/credit-cards/education/basics/how-to-spot-credit-card-fraud",
    "https://www.bankofamerica.com/security-center/report-fraud/",
    "https://www.wellsfargo.com/privacy-security/fraud/prevent/",
    "https://www.paypal.com/us/smarthelp/article/how-do-i-report-phishing-or-spoofing-faq2340",
    "https://www.paypal.com/us/webapps/mpp/security/suspicious-activity",
    "https://www.capitalone.com/help-center/security/verify-account/",
    "https://www.discover.com/credit-cards/help-center/fraud-security",
    "https://www.amex.com/en-us/account/login",
    
    # E-commerce Account Security (20)
    "https://www.amazon.com/gp/help/customer/display.html?nodeId=GQ37YD4BHXSWTXQF",
    "https://www.ebay.com/help/account/protecting-account?id=4263",
    "https://www.walmart.com/help/article/account-security/417ac8e8c8b94c68a111df0f0c8cdf3",
    "https://www.target.com/account/security",
    "https://www.etsy.com/security",
    "https://help.shopify.com/en/manual/your-account/account-security",
    
    # Social Media Safety (20)
    "https://www.facebook.com/help/contact/571927962827565",
    "https://help.instagram.com/368191326593075",
    "https://help.twitter.com/en/safety-and-security/phishing-spam-and-malware-links",
    "https://www.linkedin.com/help/linkedin/answer/a1339724/recognizing-and-reporting-scam-messages",
    "https://support.tiktok.com/en/safety-hc/account-and-user-safety",
    
    # Tech Support Pages (30)
    "https://support.google.com/mail/answer/8253",
    "https://support.microsoft.com/en-us/account-billing/protect-your-microsoft-account-942e4f5f-49ea-4f87-8d75-51e9e4e73e25",
    "https://support.apple.com/en-us/HT204759",
    "https://www.dropbox.com/help/security/protect-account",
    "https://support.zoom.us/hc/en-us/articles/360041408732-Account-security-best-practices",
    "https://slack.com/help/articles/360000356123-Secure-your-workspace",
    
    # Government Resources (15)
    "https://consumer.ftc.gov/articles/how-recognize-and-avoid-phishing-scams",
    "https://www.cisa.gov/news-events/news/avoiding-social-engineering-phishing-attacks",
    "https://www.fbi.gov/scams-and-safety/common-scams-and-crimes/phishing",
    "https://www.ncsc.gov.uk/guidance/phishing",
    "https://www.irs.gov/identity-theft-fraud-scams/how-to-know-its-really-the-irs-calling-or-knocking-on-your-door",
    
    # Education/Learning (20)
    "https://www.coursera.org/learn/cyber-security-domain/lecture/phishing",
    "https://www.udemy.com/course/complete-phishing-security-course/",
    "https://en.wikipedia.org/wiki/Phishing",
    "https://en.wikipedia.org/wiki/Social_engineering_(security)",
    "https://www.geeksforgeeks.org/cyber-security-phishing/",
    
    # Developer Forums (15)
    "https://github.com/topics/phishing-detection",
    "https://stackoverflow.com/questions/tagged/phishing",
    "https://security.stackexchange.com/questions/tagged/phishing",
    "https://www.reddit.com/r/cybersecurity/comments/phishing/",
    
    # News & Media (15)
    "https://www.nytimes.com/article/verify-account-security-tips.html",
    "https://www.bbc.com/news/technology-account-security-guide",
    "https://www.reuters.com/technology/cybersecurity-phishing-attacks/",
    
    # Gaming Platforms (10)
    "https://support.steampowered.com/kb_article.php?ref=2347-QDFN-4366",
    "https://account.xbox.com/en-us/Profile/Verify",
    "https://support.playstation.com/s/article/Account-Security-Tips",
    
    # Travel & Booking (10)
    "https://www.airbnb.com/trust/account-security",
    "https://www.booking.com/content/security-privacy.html",
    
    # Messaging (10)
    "https://faq.whatsapp.com/general/security-and-privacy/staying-safe-on-whatsapp",
    "https://faq.whatsapp.com/general/account-and-profile/how-to-verify-your-account",
    "https://telegram.org/faq#q-how-does-2-step-verification-work",
]

# ============================================================
# Combine all URLs for processing
# ============================================================
all_urls = diverse_legitimate_urls + educational_urls + complex_legitimate_urls 

print(f"\n📊 Total URLs to add: {len(all_urls):,}")
print(f"   - Diverse legitimate sites: {len(diverse_legitimate_urls):,}")
print(f"   - Educational security content: {len(educational_urls):,}")

print(f"\n📋 Distribution (diverse URLs):")
print(f"   - Education: ~500")
print(f"   - AI/Tech: ~600")
print(f"   - News: ~400")
print(f"   - E-commerce: ~600")
print(f"   - Government: ~350")
print(f"   - SaaS: ~500")
print(f"   - Popular/Social: ~650")

print(f"\n📋 Distribution (educational URLs):")
print(f"   - Cybersecurity blogs & news")
print(f"   - Banking/financial security pages")
print(f"   - E-commerce account protection")
print(f"   - Social media safety resources")
print(f"   - Government fraud prevention")
print(f"   - Tech & developer forums")

# ============================================================
# Load existing dataset
# ============================================================
print("\n📥 Loading existing dataset...")
try:
    X_existing = joblib.load("Models/2025/features_2025.pkl")
    y_existing = joblib.load("Models/2025/labels_2025.pkl")
    print(f"✅ Loaded existing dataset: {len(y_existing)} samples")
except FileNotFoundError:
    print("❌ ERROR: features_2025.pkl or labels_2025.pkl not found!")
    print("   Please run the preprocessing script first.")
    sys.exit(1)

# Load URL tracking file (to prevent duplicate URLs, NOT features)
url_tracking_file = "augmented_urls_2025.txt"
try:
    with open(url_tracking_file, 'r') as f:
        existing_urls = set(line.strip() for line in f)
    print(f"✅ Loaded URL tracking: {len(existing_urls)} URLs previously added")
except FileNotFoundError:
    existing_urls = set()
    print(f"📝 No URL tracking file found - will create new one")

# ============================================================
# Extract features for new URLs 
# ============================================================
print("\n🔬 Extracting features for new URLs...")
extractor = ChangedURLFeatureExtractor()
new_features = []
new_urls = []
skipped = 0

for i, url in enumerate(all_urls, 1):
    if i % 100 == 0:
        print(f"   Processed {i}/{len(all_urls)} URLs...")
    
    # Skip if URL was already added in previous augmentation
    if url in existing_urls:
        skipped += 1
        continue
    
    try:
        feats = extractor.extract(url)
        new_features.append(feats)
        new_urls.append(url)
    except Exception as e:
        print(f"   ⚠️  Warning: Failed to extract features for {url}: {e}")

print(f"✅ Successfully extracted features for {len(new_features)} URLs")
if skipped > 0:
    print(f"   ⏭️  Skipped {skipped} URLs (already in dataset)")

# ============================================================
# Combine datasets
# ============================================================
print("\n🔗 Combining datasets...")

# Convert X_existing to DataFrame if it's a list
if isinstance(X_existing, list):
    print("   Converting existing features from list to DataFrame...")
    X_existing = pd.DataFrame(X_existing)

if len(new_features) > 0:
    X_new = pd.DataFrame(new_features)
    X_combined = pd.concat([X_existing, X_new], ignore_index=True)
    
    y_new = [0] * len(new_features)  # 0 = Legitimate
    y_combined = list(y_existing) + y_new
    
    print(f"✅ Combined dataset:")
    print(f"   Original samples: {len(y_existing)}")
    print(f"   New samples added: {len(y_new)}")
    print(f"   Total samples: {len(y_combined)}")
else:
    X_combined = X_existing
    y_combined = y_existing
    print(f"⚠️  No new URLs to add (all {len(all_urls)} URLs already in dataset)")
    print(f"   Dataset unchanged: {len(y_combined)} samples")

# ============================================================
# Save augmented dataset
# ============================================================
print("\n💾 Saving augmented dataset...")

# Ensure X_combined is a DataFrame before saving
if not isinstance(X_combined, pd.DataFrame):
    print("   Converting features to DataFrame before saving...")
    X_combined = pd.DataFrame(X_combined)

joblib.dump(X_combined, "Models/2025/features_2025.pkl")
joblib.dump(y_combined, "Models/2025/labels_2025.pkl")

print("✅ Saved:")
print(f"   - Models/2025/features_2025.pkl (shape: {X_combined.shape})")
print(f"   - Models/2025/labels_2025.pkl (length: {len(y_combined)})")

# Update URL tracking file
if len(new_urls) > 0:
    all_tracked_urls = existing_urls.union(set(new_urls))
    with open(url_tracking_file, 'w') as f:
        for url in sorted(all_tracked_urls):
            f.write(f"{url}\n")
    print(f"   - {url_tracking_file} (tracking {len(all_tracked_urls)} URLs)")

# ============================================================
# Summary
# ============================================================
print("\n" + "="*70)
print(" ✅ DATASET AUGMENTATION COMPLETE")
print("="*70)
print(f"\nTotal dataset size: {len(y_combined):,} samples")
print(f"New unique URLs added: {len(new_urls):,}")
print(f"\n📊 Label distribution:")
# Fix: Properly count labels
label_counts = Counter(y_combined)
for label in [0, 1]:
    count = label_counts.get(label, 0)
    label_name = 'Legitimate' if label == 0 else 'Phishing'
    print(f"   {label_name}: {count:,} ({count/len(y_combined)*100:.1f}%)")
print("="*70 + "\n")
