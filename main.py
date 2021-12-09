import discord, json, random
from discord.commands import Option

CONFIG = dict()

bot = discord.Bot()

# The character selector window
class CharacterSelector(discord.ui.View):
    def __init__(
        self,
        user: discord.User,
        characters: list[dict[str, str]],
        amount: int,
        max_tries: int,
    ):
        super().__init__(timeout=None)
        self.user = user
        self.characters = characters
        self.amount = amount
        self.remaining_tries = max_tries
        self.names = random.sample(characters, self.amount)

        # Only bother adding buttons if starting with rerolls
        if self.remaining_tries > 0:
            for i, name in enumerate(self.names):
                self.add_item(RerollCharacterButton(name, i))
            self.add_item(LockButton())
        else:
            self.timeout = 0.0

    def gen_text(self) -> str:
        output = f"**Character Rolls for {self.user.mention}:**\n"
        output += f"Select a character below to reroll them in your lineup. Remaining rolls: ***{self.remaining_tries}***"
        return output

    def gen_embeds(self) -> list[discord.Embed]:
        embeds = list()
        for i, character in enumerate(self.names):
            embeds.append(
                discord.Embed(title=f"**{i + 1}:** {character['text']}").set_image(
                    url=character["image"]
                )
            )

        return embeds


class RerollCharacterButton(discord.ui.Button):
    def __init__(self, name: str, pos: int):
        super().__init__(
            label=name["text"],
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
        self.label = new_name["text"]

        # Checking if out of tries and locking:
        if self.view.remaining_tries <= 0:
            for button in self.view.children:
                button.disabled = True
        await interaction.response.edit_message(
            content=self.view.gen_text(), view=self.view, embeds=self.view.gen_embeds()
        )
        if self.disabled:
            self.view.stop()


class LockButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Lock", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.view.user and not (
            isinstance(interaction.user, discord.Member)
            and interaction.user.guild_permissions.administrator
        ):
            return
        self.view.remaining_tries = 0
        for button in self.view.children:
            button.disabled = True
        await interaction.response.edit_message(
            content=self.view.gen_text(), view=self.view, embeds=self.view.gen_embeds()
        )
        self.view.stop()


@bot.slash_command()
async def get_characters(ctx):
    view = CharacterSelector(
        ctx.author,
        CONFIG["characters"],
        CONFIG["characters_given"],
        CONFIG["max_rerolls"],
    )
    await ctx.respond(
        view.gen_text(),
        view=view,
        allowed_mentions=discord.AllowedMentions(replied_user=True),
        embeds=view.gen_embeds(),
    )


@bot.user_command(name="Post user list")
async def get_user_characters(ctx, user):
    # Check if admin
    if (
        isinstance(ctx.author, discord.Member)
        and ctx.author.guild_permissions.administrator
    ):
        view = CharacterSelector(
            user,
            CONFIG["characters"],
            CONFIG["characters_given"],
            CONFIG["max_rerolls"],
        )
        await ctx.respond(
            view.gen_text(),
            view=view,
            allowed_mentions=discord.AllowedMentions(users=True),
            embeds=view.gen_embeds(),
        )
    else:
        await ctx.respond("Only administrators can use this", ephemeral=True)


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
    assert (
        config["characters_given"] > 0 and config["characters_given"] < 25
    ), "characters_given must be positive and less than 25 due to discord limitations"
    assert config["max_rerolls"] >= 0, "max_rerolls must not be negative"
    assert isinstance(config["characters"], list), "characters must be a list of names"
    assert len(config["characters"]) > config["characters_given"] or (
        len(config["characters"]) == config["characters_given"]
        and config["max_rerolls"] == 0
    ), "Must be at least as many characters to choose from as go into teams"
    # for name in config["characters"]:
    #    assert isinstance(name, str), "Every item in characters must be a string"

    global CONFIG
    CONFIG = config

    try:
        bot.run(config["token"])
    except discord.LoginFailure as e:
        print(f"Error logging into discord: {e}")
        exit(1)


if __name__ == "__main__":
    init()
