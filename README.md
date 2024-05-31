# BlumAutoclicker
Autoclicker for @BlumCryptoBot mini-game

## Script can:
- Start farming
* Launch the game and take maximum profit from it (game result is randomized)
+ Collect daily bonus

## Using example:
> [!NOTE]
> In Telegram Desktop you need to enable WebView debugging modes

> ***Settings -> Advanced -> Experimental settings -> Enable WebView inspecting***

1. Go to the bot **https://t.me/BlumCryptoBot**
2. Click "Launch Bloom"
3. On the surface of the application that opens, right click and from the menu shown select **Inspect element**
4. Next, as in the [**Screenshot**](1.png), go to Network tab and wait until refresh appears in the list of requests
   > It may take time until the current token expires
   
   > If you don't have requests click in the bot’s web application  3 dots and refresh.
6. The request response will contain what we need. Copy content to token.json file
7. ```pip install -r requirements.txt```
8. Run script: ```python3 script main.py```

> [!CAUTION]
> Use script at your own risk!
