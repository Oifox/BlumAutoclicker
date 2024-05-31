from client import ClickerClient

client = ClickerClient()

while True:
    client.update_balance()
    client.play_game()
    client.start_farming()
