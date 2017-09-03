### Trivious-bot

Experiment with selenium and [triviusgame.com](triviusgame.com).

#### Install
- Clone repository
- Run ``` pip install -r -requirements.txt ```

#### Run bot
```python
from bot import Bot  

bot = Bot(
    "<quiz url>",  # https://triviusgame.com/game/geography/geography-general
    "<email addres>",
    "<password>"
)

bot.start()
```
