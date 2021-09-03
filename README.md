# Deploying to Heroku

1. Make sure the requirements.txt has the reference to kora module

2. In Heroku, go to the app settings and add the two Config Vars below:
    * CHROMEDRIVER_PATH --> /app/.chromedriver/bin/chromedriver
    * GOOGLE_CHROME_BIN --> /app/.apt/usr/bin/google-chrome

3. Still on the app settings tab, on Buildpacks section, add the two buildpacks below:
    * https://github.com/heroku/heroku-buildpack-google-chrome
    * https://github.com/heroku/heroku-buildpack-chromedriver

Once the app is deployed again, Heroku will add the two new buildpacks to the dyno and Kora will be able to access the chrome webdriver.