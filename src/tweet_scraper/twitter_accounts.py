from tweet_scraper import load_cookies_from_file

accounts = {
    "frank033045322": {
        "password": "frank_cashcow_n001",
        "email": "cashcow.frank001@gmail.com",
        "email_password": "frank.cashcow.001",
        "cookies": "cookies_frank033045322.json"
    },
    "zoe178479968816": {
        "password": "zoe_cashcow_n002",
        "email": "cashcow.zoe002@gmail.com",
        "email_password": "zoe_cashcow_n002",
        "cookies": "cookies_zoe178479968816.json"
    },
    "angus1364984": {
        "password": "angus_cashcow_n003",
        "email": "cashcow.angus003@yahoo.com",
        "email_password": "angus_cashcow_n003",
        "cookies": "cookies_angus1364984.json",
    },
    "Porky5641173659" : {
        "password": "porky_cashcow_n004",
        "email": "cashcow.porky004@mail.com",
        "email_password": "porky_cashcow_n004",
        "cookies": "cookies_Porky5641173659.json"
    },
    "Fanta484278": {
        "password": "fanta_cashcow_n005",
        "email": "cashcow.fanta005@mail.com",
        "email_password": "fanta_cashcow_n005",
        "cookies": "cookies_Fanta484278.json",
    },
    "coco33952489968": {
        "password": "coco_cashcow_n006",
        "email": "cashcow.coco006@mail.com ",
        "email_password": "coco_cashcow_n006",
        "cookies": "cookies_coco33952489968.json",
    },
    "Ralph7041654884": {
        "password": "ralph_cashcow_n007",
        "email": "cashcow.ralph007@mail.com",
        "email_password": "ralph_cashcow_n007",
        "cookies": "cookies_ralph7041654884.json",
    },
    "Piggy477428": {
        "password": "piggy_cashcow_n008",
        "email": "cashcow.piggy008@mail.com",
        "email_password": "piggy_cashcow_n008",
        "cookies": "cookies_piggy477428.json",
    },
    "cookie377906": {
        "password": "cookie_cashcow_n009",
        "email": "cashcow.cookie009@mail.com",
        "email_password": "cookie_cashcow_n009",
        "cookies": "cookies_cookie377906.json",
    },
    "chicken86780932": {
        "password": "chicken_cashcow_n010",
        "email": "cashcow.chicken010@mail.com",
        "email_password": "chicken_cashcow_n010",
        "cookies": "cookies_chicken86780932.json",
    },
    "chewy1965931": {
        "password": "chewy_cashcow_n011",
        "email": "cashcow.chewy011@mail.com",
        "email_password": "chewy_cashcow_n011",
        "cookies": "cookies_chewy1965931.json",
    },
    "buddy9928413566": {
        "password": "buddy_cashcow_n012",
        "email": "cashcow.buddy012@mail.com",
        "email_password": "buddy_cashcow_n012",
        "cookies": "cookies_chewy1965931.json",
    },
    "fishy382464": {
        "password": "fishy_cashcow_n013",
        "email": "cashcow.fishy013@mail.com",
        "email_password": "fishy_cashcow_n013",
        "cookies": "cookies_fishy382464.json",
    },
    "harold857825489": {
        "password": "harold_cashcow_n014",
        "email": "cashcow.harold014@mail.com",
        "email_password": "harold_cashcow_n014",
        "cookies": "cookies_harold857825489.json",
    },
    "frederick005832": {
        "password": "frederick_cashcow_n015",
        "email": "cashcow.frederick015@mail.com",
        "email_password": "frederick_cashcow_n015",
        "cookies": "cookies_frederick005832.json",
    },
    "jason2203892377": {
        "password": "jason_cashcow_n016",
        "email": "cashcow.jason016@mail.com",
        "email_password": "jason_cashcow_n016",
        "cookies": "cookies_jason2203892377.json",
    },
    "meerkat796544": {
        "password": "meerkat_cashcow_n017",
        "email": "cashcow.meerkat017@mail.com",
        "email_password": "meerkat_cashcow_n017",
        "cookies": "cookies_meerkat796544.json",
    },
    "stanley2084522": {
        "password": "stanley_cashcow_n018",
        "email": "cashcow.stanley018@mail.com",
        "email_password": "stanley_cashcow_n018",
        "cookies": "cookies_stanley2084522.json",
    },
    "franklin343528": {
        "password": "franklin_cashcow_n019",
        "email": "cashcow.franklin019@mail.com",
        "email_password": "franklin_cashcow_n019",
        "cookies": "cookies_franklin343528.json",
    },
    "Melman680043064": {
        "password": "melman_cashcow_n020",
        "email": "cashcow.melman020@mail.com",
        "email_password": "melman_cashcow_n020",
        "cookies": "cookies_melman680043064.json",
    },
    "gloria1745491": {
        "password": "gloria_cashcow_n021",
        "email": "cashcow.gloria021@mail.com",
        "email_password": "gloria_cashcow_n021",
        "cookies": "cookies_gloria1745491.json",
    },
    "julian739285": {
        "password": "julian_cashcow_n022",
        "email": "cashcow.julian022@mail.com",
        "email_password": "julian_cashcow_n022",
        "cookies": "cookies_julian739285.json",
    },
    "skipper30132732": {
        "password": "skipper_cashcow_n023",
        "email": "cashcow.skipper023@mail.com",
        "email_password": "skipper_cashcow_n023",
        "cookies": "cookies_skipper30132732.json",
    },
    "jenny8527077512": {
        "password": "jenny_cashcow_n024",
        "email": "cashcow.jenny024@mail.com",
        "email_password": "jenny_cashcow_n024",
        "cookies": "cookies_jenny_8527077512.json",
    },
    "Sheep1829982": {
        "password": "sheep_cashcow_n025",
        "email": "cashcow.sheep025@mail.com",
        "email_password": "sheep_cashcow_n025",
        "cookies": "cookies_sheep1829982.json",
    },
    "Ella": {
        "password": "ella_cashcow_n026",
        "email": "cashcow.ella026@mail.com",
        "email_password": "ella_cashcow_n026",
    },
    "Gatorade2213124": {
        "password": "gatorade_cashcow_n027",
        "email": "cashcow.gatorade027@mail.com",
        "email_password": "gatorade_cashcow_n027",
        "cookies": "cookies_gatorade2213124.json",
    },
    "Spongebob181031": {
        "password": "spongebob_cashcow_n028",
        "email": "cashcow.spongebob028@mail.com",
        "email_password": "spongebob_cashcow_n028",
        "cookies": "cookies_spongebob181031.json",
    },
    "Samuel190496734": {
        "password": "samuel_cashcow_n029",
        "email": "cashcow.samuel029@mail.com",
        "email_password": "samuel_cashcow_n029",
        "cookies": "cookies_samuel190496734.json",
    },
    "Boog428560": {
        "password": "boog_cashcow_n030",
        "email": "cashcow.boog030@mail.com",
        "email_password": "boog_cashcow_n030",
        "cookies": "cookies_boog428560.json",
    },
    "henry4306315130": {
        "password": "henry_cashcow_n031",
        "email": "cashcow.henry031@mail.com",
        "email_password": "henry_cashcow_n031",
        "cookies": "cookies_henry430315130.json",
    },
    "Jelly1129151": {
        "password": "jelly_cashcow_n032",
        "email": "cashcow.jelly032@mail.com",
        "email_password": "jelly_cashcow_n032",
        "cookies": "cookies_jelly1129151.json",
    },
    "Jackie67307686": {
        "password": "jacky_cashcow_n033",
        "email": "cashcow.jackie033@mail.com",
        "email_password": "jackie_cashcow_n033",
        "cookies": "cookies_jackie67307686.json",
    },
    "rambo287203": {
        "password": "rambo_cashcow_n034",
        "email": "cashcow.rambo034@mail.com",
        "email_password": "rambo_cashcow_n034",
        "cookies": "cookies_rambo287203.json",
    },
    "fanks598427": {
        "password": "fanks_cashcow_n035",
        "email": "cashcow.fanks035@mail.com",
        "email_password": "fanks_cashcow_n035",
        "cookies": "cookies_fanks598427.json",
    },
    "larry2267992545": {
        "password": "larry_cashcow_n036",
        "email": "cashcow.larry036@mail.com",
        "email_password": "larry_cashcow_n036",
        "cookies": "cookies_larry2267992545.json",
    },
    "Mort1996165": {
        "password": "mort_cashcow_n037",
        "email": "cashcow.mort037@mail.com",
        "email_password": "mort_cashcow_n037",
        "cookies": "cookies_mort_1996165.json",
    },
    "lemur108871": {
        "password": "lemur_cashcow_n038",
        "email": "cashcow.lemur038@mail.com",
        "email_password": "lemur_cashcow_n038",
        "cookies": "cookies_lemur108871.json",
    },
    "maximus788573": {
        "password": "maximus_cashcow_n039",
        "email": "cashcow.maximus039@mail.com",
        "email_password": "maximus_cashcow_n039",
        "cookies": "cookies_maximus788573.json",
    },
    "carl87942256912": {
        "password": "carl_cashcow_n040",
        "email": "cashcow.carl040@mail.com",
        "email_password": "carl_cashcow_n040",
        "cookies": "cookies_carl87942256912.json",
    },
    "milton781063211": {
        "password": "milton_cashcow_n041",
        "email": "cashcow.milton04211@mail.com",
        "email_password": "milton_cashcow_n041",
        "cookies": "cookies_milton781063211.json",
    },
    "table1459510": {
        "password": "table_cashcow_n042",
        "email": "cashcow.table042@mail.com",
        "email_password": "table_cashcow_n042",
        "cookies": "cookies_table1459510.json",
    },
    "panda4276137752": {
        "password": "panda_cashcow_n043",
        "email": "cashcow.panda043@mail.com",
        "email_password": "panda_cashcow_n043",
        "cookies": "cookies_panda4276137752.json",
    },
    "bamboo151128": {
        "password": "bamboo_cashcow_n044",
        "email": "cashcow.bamboo044@mail.com",
        "email_password": "bamboo_cashcow_n044",
        "cookies": "cookies_bamboo151128.json",
    },
    "fried6446992238": {
        "password": "fried_cashcow_n045",
        "email": "cashcow.fried045@mail.com",
        "email_password": "fried_cashcow_n045",
        "cookies": "cookies_fried6446992238.json",
    },
    "temote95437": {

    },
    "teash616366": {

    },
    "weash231554": {

    },
    "cartot148371": {

    },
    "parmon139352": {

    },
    "mangrove199423": {
        
    },
    "tank796006": {

    },
    "nemo618813": {

    },
    "marcus915624702": {

    },
    "frankalyn171547": {

    },
    "ted34877378": {

    },
    "tampa785539": {

    },
    "fishy354099": {

    },
    "marlin553626": {

    },


}

