import discord, json, random
from discord.commands import Option

CONFIG = dict()

bot = discord.Bot()

# The character selector window
class CharacterSelector(discord.ui.View):
    def __init__(self, user: discord.User, characters: list[str], amount: int, max_tries: int):
        super().__init__(timeout=None)
        self.user = user
        self.characters = characters
        self.amount = amount
        self.remaining_tries = max_tries
        self.names = random.sample(characters, self.amount)
        
        for i, name in enumerate(self.names):
            self.add_item(RerollCharacterButton(name, i))
        self.add_item(LockButton())
    
    def list_characters(self) -> str:
        output = f"**Character Rolls for {self.user.mention}:**\n"
        for i, name in enumerate(self.names):
            output += f"**{i + 1}:** {name}\n"
        output += f"Select a character below to reroll them in your lineup. Remaining rolls: ***{self.remaining_tries}***"
        return output

class RerollCharacterButton(discord.ui.Button):
    def __init__(self, name: str, pos: int):
        super().__init__(
            label=name,
            style=discord.ButtonStyle.primary,
        )
        self.pos = pos
    
    async def callback(self, interaction: discord.Interaction):
        # Runs when the button is clicked
        if self.view.remaining_tries <= 0 or interaction.user != self.view.user:
            return
        self.view.remaining_tries -= 1
        # Randomly choose a character that is not currently selected
        choose_pool = [x for x in self.view.characters if x not in self.view.names]
        new_name = random.choice(choose_pool)
        self.view.names[self.pos] = new_name
        self.label = new_name

        # Checking if out of tries and locking:
        if self.view.remaining_tries <= 0:
            for button in self.view.children:
                button.disabled = True
        await interaction.response.edit_message(content=self.view.list_characters(), view=self.view)

class LockButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Lock",
            style=discord.ButtonStyle.danger
        )
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.view.user:
            return
        self.view.remaining_tries = 0
        for button in self.view.children:
            button.disabled = True
        await interaction.response.edit_message(content=self.view.list_characters(), view=self.view)

@bot.slash_command()
async def get_characters(ctx):
    view = CharacterSelector(ctx.author, CONFIG["characters"], CONFIG["characters_given"], CONFIG["max_rerolls"])
    await ctx.respond(view.list_characters(), view=view)

# Disabled because as far as I can tell this isn't possible

# @bot.slash_command()
# async def make_list_for_group(ctx, role: discord.Role):
#     # Only run by administrators
#     author = ctx.author
#     if not (isinstance(author, discord.Member) and author.guild_permissions.administrator):
#         return
#     first_send = True
#     for member in role.members:
#         print(member)
#         view = CharacterSelector(member, CONFIG["characters"], CONFIG["characters_given"], CONFIG["max_rerolls"])
#         if first_send:
#             first_send = False
#             await ctx.respond(view.list_characters(), view=view)
#         else:
#             await ctx.followup.send(view.list_characters(), view=view)

@bot.event
async def on_ready():
    print("Ready!")

def init() -> None:
    try:
        with open("config.json") as conf:
            config = json.load(conf)
    except FileNotFoundError:
        print(f"Unable to locate config file")
        exit(1)
    except json.decoder.JSONDecodeError as e:
        print(f"Error parsing json file: {e}")
        exit(1)

    # Config validation
    assert (
        "token" in config
        and "characters_given" in config
        and "max_rerolls" in config
        and "characters" in config
    ), "Missing expected fields in config. Please make sure default_config.json was copied and edited to config.json correctly."
    assert isinstance(config["characters_given"], int) and isinstance(
        config["max_rerolls"], int
    ), "characters_given and max_rerolls must both be numbers"
    assert config["characters_given"] > 0 and config["characters_given"] < 25, "characters_given must be positive and less than 25 due to discord limitations"
    assert config["max_rerolls"] >= 0, "max_rerolls must not be negative"
    assert isinstance(config["characters"], list), "characters must be a list of names"
    assert len(config["characters"]) >= config["characters_given"], "Must be at least as many characters to choose from as go into teams"
    for name in config["characters"]:
        assert isinstance(name, str), "Every item in characters must be a string"
    
    global CONFIG
    CONFIG = config

    try:
        bot.run(config["token"])
    except discord.LoginFailure as e:
        print(f"Error logging into discord: {e}")
        exit(1)


if __name__ == "__main__":
    init()
