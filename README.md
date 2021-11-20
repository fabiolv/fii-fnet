# FII-FNET API
This project is part of my personal studies on Python and APIs and it's a WIP.
There's a lot of refactoring and improvements needed that will be done as time permits.

This API uses BM&F Bovespa's FNET API to get data reported by the FIIs administrators.
Since the monthly and the dividends reports are standardized HTML documents, the API queries the reports and returns the raw HTML content from FNET. This data is to be parsed by another service.


### Deploying to Heroku

*** 2021-11-20 - Not needed anymore as the kora/selenium dependency has been removed ***
1. Make sure the requirements.txt has the reference to kora module

2. In Heroku, go to the app settings and add the two Config Vars below:
    * CHROMEDRIVER_PATH --> /app/.chromedriver/bin/chromedriver
    * GOOGLE_CHROME_BIN --> /app/.apt/usr/bin/google-chrome

3. Still on the app settings tab, on Buildpacks section, add the two buildpacks below:
    * https://github.com/heroku/heroku-buildpack-google-chrome
    * https://github.com/heroku/heroku-buildpack-chromedriver

Once the app is deployed again, Heroku will add the two new buildpacks to the dyno and Kora will be able to access the chrome webdriver.