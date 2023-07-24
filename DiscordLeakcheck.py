import discord
import random
from leakcheck import LeakCheckAPI

intents = discord.Intents.all()
client = discord.Client(command_prefix='!', intents=intents)

api = LeakCheckAPI()
api.set_key("YOUR_LEAKCHECK_API_HERE")

# Define a list of possible colors
colors = [discord.Color.red(), discord.Color.green(), discord.Color.blue(), discord.Color.orange(), discord.Color.purple()]

async def display_results(channel, result, lookup_type):
    if 'error' in result:
        error_message = result['error']
        if error_message == 'Missing params (key, check, type)':
            error_message = 'Missing required parameters.'
        elif error_message == 'Invalid type':
            error_message = 'Invalid lookup type.'
        elif error_message == 'API Key is wrong':
            error_message = 'API key is invalid.'
        elif error_message == 'API Key is blocked':
            error_message = 'API key is blocked.'
        elif error_message == 'No license on this key':
            error_message = 'No license or upgrade required.'
        elif error_message == 'Your query contains invalid characters':
            error_message = 'You have submitted a query containing prohibited characters.'
        elif error_message == 'Enter at least 3 characters to search':
            error_message = 'Minimum number of characters is 3.'
        elif error_message == 'Invalid email':
            error_message = 'You have passed the email type with an invalid email address.'
        elif error_message == 'Invalid domain':
            error_message = 'You have passed the domain type with an invalid domain.'
        elif error_message == 'Invalid query':
            error_message = 'The search query you sent is invalid.'
        elif error_message == 'IP linking is required':
            error_message = 'You have to link an IP address.'
        elif error_message == 'Limit reached':
            error_message = 'You have exceeded your plan limits.'
        elif error_message == 'Not found':
            error_message = 'There are no results found.'
        elif error_message == 'Too many requests, you have been ratelimited':
            error_message = 'You have exceeded a request threshold and been banned for 10 sec.'
        else:
            error_message = 'An unknown error occurred.'

        await channel.send(error_message)
        return

    # Generate a random color from the list
    color = random.choice(colors)

    embed = discord.Embed(title="Leaked Data", color=color)
    total_chars = 0
    for idx, item in enumerate(result, start=1):
        line = item['line'].split(':')
        leaked_times = line[1] if len(line) > 1 else "Not Found"
        data = line[0]
        sources = ", ".join(item['sources']) if 'sources' in item else "Not Found"
        last_breach = item['last_breach'] if 'last_breach' in item else "Not Found"

        entry_label = f"{lookup_type.capitalize()} Entry {idx}"
        field_value = f"Username: {data}\nPassword: {leaked_times}\nSources: {sources or 'Not Found'}\nLast Breach: {last_breach or 'Not Found'}"

        # Check if adding the field would exceed the embed size limit
        if total_chars + len(field_value) + len(entry_label) > 6000:
            await channel.send(embed=embed)
            embed.clear_fields()
            total_chars = 0

        embed.add_field(name=entry_label, value=field_value, inline=False)
        total_chars += len(entry_label) + len(field_value)

    await channel.send(embed=embed)

@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!ping"):
        await message.channel.send("Pong!")

    if message.content.startswith("!login"):
        data = message.content.split("!login ")[1].strip()
        result = api.lookup(data, "login")
        await display_results(message.channel, result, "login")

    if message.content.startswith("!email"):
        data = message.content.split("!email ")[1].strip()
        result = api.lookup(data, "email")
        await display_results(message.channel, result, "email")

    if message.content.startswith("!mass"):
        keyword = message.content.split("!mass ")[1].strip()
        result = api.lookup(keyword, "mass")
        await display_results(message.channel, result, "mass_email")

client.run("YOURDISCORDBOTTOKEN")
