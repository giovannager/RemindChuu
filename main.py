# Name: Giovanna Gerada
# Date: May 31, 2022
# Purpose: creating a discord bot called RemindChuu to remind us to pay our rent at the end of each month

# import libraries
from operator import index
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import os
import json

from dotenv import load_dotenv
load_dotenv()

# define constants and variables
TOKEN = os.environ.get("TOKEN")

client = commands.Bot(command_prefix = '!')
client.remove_command("help")

dict_reminders = {"users" : [], "reminders" : []} # the list of reminders is a list of dicts corresponding whose index to the username 

# with open('all_data.json', 'w') as outfile:
#     json.dump(dict_reminders, outfile)
    
# keep a log of past messages
past_msgs = {"users" : [], "msgs" : []}

all_times = []

flag = False

# things to be run as the bot is first booted up
@client.event
async def on_ready():
    send_reminder.start()
    print("We have logged in as {0.user}".format(client))

# every 10 seconds it checks if there is a reminder for the current time and sends the reminder if there is
@tasks.loop(seconds = 10)
async def send_reminder():
    now = datetime.now().replace(second = 0, microsecond = 0)
    now_str = datetime.strftime(now, "%Y-%m-%d %H:%M:%S")
    if now in all_times:
        list(filter(lambda item: item != now, all_times))
        # find the reminders that match this time
        infile = open('all_data.json')
        data = json.load(infile)

        # checking for reminders matching the current time
        for i in range (len(data["reminders"])):
            if now_str in data["reminders"][i]["times"]:
                index_reminder = data["reminders"][i]["times"].index(now_str)

                channel = data["reminders"][i]["channel"][index_reminder]
                reminder = data["reminders"][i]["tasks"][index_reminder]

                # remove and send the reminder
                data["reminders"][i]["tasks"].pop(index_reminder)
                data["reminders"][i]["times"].pop(index_reminder)

                if data["reminders"][i]["command"][index_reminder] == "remindme":
                    data["reminders"][i]["channel"].pop(index_reminder)
                    data["reminders"][i]["command"].pop(index_reminder)

                    with open('all_data.json', 'w') as outfile:
                        json.dump(data, outfile, default = str)

                    await client.get_channel(channel).send("<@" + data["reminders"][i]["user"] + "> **You've asked me to remind you:**\n" + reminder)
                else:
                    data["reminders"][i]["channel"].pop(index_reminder)
                    data["reminders"][i]["command"].pop(index_reminder)

                    with open('all_data.json', 'w') as outfile:
                        json.dump(data, outfile, default = str)

                    await client.get_channel(channel).send("@everyone **You've asked me to remind you:**\n" + reminder)

@client.event
async def on_message(message):
    # define extra variables when there are messages
    username = str(message.author.id)
    user_message = str(message.content)
    channel = message.channel.id
    server = str(message.guild.id)
    print(f"{username}: {user_message} ({server}: {channel})")

    # add items to log
    if username not in past_msgs["users"]:
        new_dict = {"user_msg" : [user_message], "channel" : [channel], "server" : [server]}
        past_msgs["users"].append(username)
        past_msgs["msgs"].append(new_dict)
    else:
        index_user = past_msgs["users"].index(username)
        past_msgs["msgs"][index_user]["user_msg"].append(user_message)
        past_msgs["msgs"][index_user]["channel"].append(channel)
        past_msgs["msgs"][index_user]["server"].append(server)

    # number of counted logs
    index_user = past_msgs["users"].index(username)
    num_logs = len(past_msgs["msgs"][index_user]["user_msg"])

    # make sure the bot does not respond to its own messages
    if message.author == client.user:
        return None

    # create personal reminders to ping the user
    if user_message.startswith("!remindme"):
        # check if the user already has reminders
        # gonna need to check if its in the json file instead - read the json file
        infile = open('all_data.json')
        data = json.load(infile)

        if username in data["users"]:
            # continue to add the reminder
            reminder = user_message.split("!remindme ", 1)[1]
            
            index = data["users"].index(username)

            data["reminders"][index]["tasks"].append(reminder)
            data["reminders"][index]["channel"].append(channel)
            data["reminders"][index]["command"].append("remindme")

            with open('all_data.json', 'w') as outfile:
                json.dump(data, outfile, default = str)

            await message.channel.send("What time would you like to set this reminder to? (yyyy/mm/dd at hh:mm AM/PM)")

        else:
            # first add the username and make a new dict in reminders, then add the reminder
            new_dict = {"user" : username, "tasks" : [], "times" : [], "channel" : [], "command" : []}
            data["users"].append(username)
            data["reminders"].append(new_dict)

            reminder = user_message.split("!remindme ", 1)[1]

            index = data["users"].index(username)

            data["reminders"][index]["tasks"].append(reminder)
            data["reminders"][index]["channel"].append(channel)
            data["reminders"][index]["command"].append("remindme")

            with open('all_data.json', 'w') as outfile:
                json.dump(data, outfile, default = str)

            await message.channel.send("What time would you like to set this reminder to? (yyyy/mm/dd at hh:mm AM/PM)")


    if "!remindme" in past_msgs["msgs"][index_user]["user_msg"][num_logs - 2]:
        if user_message != past_msgs["msgs"][index_user]["user_msg"][num_logs - 2]:
            await message.channel.send(get_time(user_message, username))

    if "!remindsvr" in past_msgs["msgs"][index_user]["user_msg"][num_logs - 2]:
        if user_message != past_msgs["msgs"][index_user]["user_msg"][num_logs - 2]:
            await message.channel.send(get_time(user_message, server))


    # create server reminders to be pinned with @everyone
    if user_message.startswith("!remindsvr"):
        reminder = user_message.split("!remindsvr", 1)[1]
        # gonna need to check if its in the json file instead - read the json file
        infile = open('all_data.json')
        data = json.load(infile)

        if server in data["users"]:
            # continue to add the reminder
            reminder = user_message.split("!remindsvr ", 1)[1]

            index = data["users"].index(server)

            data["reminders"][index]["tasks"].append(reminder)
            data["reminders"][index]["channel"].append(channel)
            data["reminders"][index]["command"].append("remindsvr")

            with open('all_data.json', 'w') as outfile:
                json.dump(data, outfile, default = str)

            await message.channel.send("What time would you like to set this server reminder to? (yyyy/mm/dd at hh:mm AM/PM)")
        else:
            # add the server to the dictionary first and then add the reminder            
            new_dict = {"user" : server, "tasks" : [], "times" : [], "channel" : [], "command" : []}
            data["users"].append(server)
            data["reminders"].append(new_dict)

            reminder = user_message.split("!remindsvr ", 1)[1]

            index = data["users"].index(server)

            data["reminders"][index]["tasks"].append(reminder)
            data["reminders"][index]["channel"].append(channel)
            data["reminders"][index]["command"].append("remindsvr")

            with open('all_data.json', 'w') as outfile:
                json.dump(data, outfile, default = str)

            await message.channel.send("What time would you like to set this sever reminder to? (yyyy/mm/dd at hh:mm AM/PM)")

    # remove personal reminders
    if user_message.startswith("!removemy"):
        if user_message.split("!removemy", 1)[1] != "":
            rm_num = user_message.split("!removemy ", 1)[1]
            
            # check if the input is valid
            if is_int(rm_num):
                rm_num = int(rm_num)

                infile = open('all_data.json')
                data = json.load(infile)

                if username in data["users"]:
                    index = data["users"].index(username)
                    if data["reminders"][index]["tasks"] != []:
                        if 1 <= rm_num and rm_num < len(data["reminders"][index]["tasks"]) + 1:
                            #remove the item
                            data["reminders"][index]["tasks"].pop(rm_num - 1)
                            data["reminders"][index]["times"].pop(rm_num - 1)
                            data["reminders"][index]["channel"].pop(rm_num - 1)
                            data["reminders"][index]["command"].pop(rm_num - 1)

                            with open('all_data.json', 'w') as outfile:
                                json.dump(data, outfile, default = str)

                            await message.channel.send("Reminder " + str(rm_num) + " has been removed!")
                        else:
                            await message.channel.send("Please choose a valid number from the list of reminders. To see all reminders type '!myreminders'.")
                    else:
                        await message.channel.send("You haven't set up any reminders yet. Please make some reminders before you attempt to clear them.")
                else:
                    await message.channel.send("You haven't set up any reminders yet. Please make some reminders before you attempt to clear them.")
            else:
                await message.channel.send("Please choose a valid number from the list of reminders. To see all reminders type '!myreminders'.")
        else:
            await message.channel.send("Please choose a valid number from the list of reminders. To see all reminders type '!myreminders'.")

    # remove server reminders
    if user_message.startswith("!removesvr"):
        if user_message.split("!removesvr", 1)[1] != "":
            rm_num = user_message.split("!removesvr ", 1)[1]
            
            # check if the input is valid
            if is_int(rm_num):
                rm_num = int(rm_num)

                infile = open('all_data.json')
                data = json.load(infile)

                if username in data["users"]:
                    index = data["users"].index(server)
                    if data["reminders"][index]["tasks"] != []:
                        if 1 <= rm_num and rm_num < len(data["reminders"][index]["tasks"]) + 1:
                            #remove the item
                            data["reminders"][index]["tasks"].pop(rm_num - 1)
                            data["reminders"][index]["times"].pop(rm_num - 1)
                            data["reminders"][index]["channel"].pop(rm_num - 1)
                            data["reminders"][index]["command"].pop(rm_num - 1)

                            with open('all_data.json', 'w') as outfile:
                                json.dump(data, outfile, default = str)

                            await message.channel.send("Reminder " + str(rm_num) + " has been removed!")
                        else:
                            await message.channel.send("Please choose a valid number from the list of reminders. To see all reminders type '!svrreminders'.")
                    else:
                        await message.channel.send("You haven't set up any server reminders yet. Please make some reminders before you attempt to clear them.")
                else:
                    await message.channel.send("You haven't set up any server reminders yet. Please make some reminders before you attempt to clear them.")
            else:
                await message.channel.send("Please choose a valid number from the list of server reminders. To see all reminders type '!svrreminders'.")
        else:
            await message.channel.send("Please choose a valid number from the list of server reminders. To see all reminders type '!svrreminders'.")


    # clear all personal reminders
    if user_message == "!clearmy":
        infile = open('all_data.json')
        data = json.load(infile)

        if username not in data["users"]:
            past_msgs["msgs"][index_user]["user_msg"][num_logs - 1] = ""
            await message.channel.send("You haven't set up any reminders yet. Please make some reminders before you attempt to clear them.")
            
        index = data["users"].index(username)
        if data["reminders"][index]["tasks"] == []:
            past_msgs["msgs"][index_user]["user_msg"][num_logs - 1] = ""
            await message.channel.send("You haven't set up any reminders yet. Please make some reminders before you attempt to clear them.")

        else:
            await message.channel.send("Are you sure you would like to clear all of your reminders? (y/n)")
    
    # implementing a confirmation message
    if past_msgs["msgs"][index_user]["user_msg"][num_logs - 2] == "!clearmy":
        infile = open('all_data.json')
        data = json.load(infile)
        if user_message.lower() == "y" or user_message.lower() == "yes":
            index = data["users"].index(username)
            data["reminders"][index]["tasks"] = []
            data["reminders"][index]["times"] = []
            data["reminders"][index]["channel"] = []
            data["reminders"][index]["command"] = []

            with open('all_data.json', 'w') as outfile:
                json.dump(data, outfile, default = str)

            await message.channel.send("Okay! All of your reminders have been cleared!")

        else:
            await message.channel.send("Okay! Your reminders have not been cleared and I'll be sure to keep them safe!")

     
    # clear all server reminders
    if user_message == "!clearsvr":
        infile = open('all_data.json')
        data = json.load(infile)

        if server not in data["users"]:
            past_msgs["msgs"][index_user]["user_msg"][num_logs - 1] = ""
            await message.channel.send("You haven't set up any server reminders yet. Please make some server reminders before you attempt to clear them.")
            
        index = data["users"].index(server)
        if data["reminders"][index]["tasks"] == []:
            past_msgs["msgs"][index_user]["user_msg"][num_logs - 1] = ""
            await message.channel.send("You haven't set up any server reminders yet. Please make some server reminders before you attempt to clear them.")

        else:
            await message.channel.send("Are you sure you would like to clear all of the server reminders? (y/n)")
    
    # implementing a confirmation message
    if past_msgs["msgs"][index_user]["user_msg"][num_logs - 2] == "!clearsvr":
        infile = open('all_data.json')
        data = json.load(infile)
        if user_message.lower() == "y" or user_message.lower() == "yes":
            index = data["users"].index(server)
            data["reminders"][index]["tasks"] = []
            data["reminders"][index]["times"] = []
            data["reminders"][index]["channel"] = []
            data["reminders"][index]["command"] = []

            with open('all_data.json', 'w') as outfile:
                json.dump(data, outfile, default = str)

            await message.channel.send("Okay! All of the server reminders have been cleared!")

        else:
            await message.channel.send("Okay! The server reminders have not been cleared and I'll be sure to keep them safe!")

    await client.process_commands(message)


# displaying an embed of all personal reminders
@client.command(pass_context = True, name = "myreminders", aliases = ["myrem"])
async def myreminders(ctx):
    username = str(ctx.message.author).split("#")[0]
    user = str(ctx.message.author.id)

    infile = open('all_data.json')
    data = json.load(infile)

    embed = discord.Embed(
        title = username + "'s reminders",
        description = print_dictlist(data, user),
        colour = 0xf3957b
   )

    if user not in data["users"]:
        embed.add_field(name="You currently have no reminders...", value="You can add reminders using !remindme", inline=True)
        await ctx.send(embed=embed)

    index = data["users"].index(user)
    if data["reminders"][index]["tasks"] == []:
        embed.add_field(name="You currently have no reminders...", value="You can add reminders using !remindme", inline=True)

    await ctx.send(embed=embed)

# displaying an embed of all server reminders
@client.command(pass_context = True, name = "svrreminders", aliases = ["svreminders", "svrrem", "svrem"])
async def svrreminders(ctx):
    server = str(ctx.message.guild.id)
    server_name = str(ctx.message.guild.name)

    infile = open('all_data.json')
    data = json.load(infile)

    embed = discord.Embed(
        title = "Server reminders for " + server_name,
        description = print_dictlist(data, server),
        colour = 0xf3957b
    )

    if server not in data["users"]:
        embed.add_field(name="The server currently has no reminders for everyone...", value="You can add reminders for everyone using !remindsvr", inline=True)
        await ctx.send(embed=embed)

    index = data["users"].index(server)
    if data["reminders"][index]["tasks"] == []:
        embed.add_field(name="The server currently has no reminders for everyone...", value="You can add reminders for everyone using !remindsvr", inline=True)

    await ctx.send(embed=embed)

    
# displaying an embed to display a list of commands
@client.command(pass_context = True, name = "help")
async def help(ctx):
    embed = discord.Embed(
        title = "List of Available Commands!",
        description = "",
        colour = 0xf3957b
    )

    embed.add_field(name='Personal Commands', value='`!remindme <reminder>` - set a personal reminder\n`!myreminders`, or `!myrem` - view list of personal reminders\n`!removemy <number>`, or `!remmy <number>` - remove a personal reminder\n`!clearmy` - clear all personal reminders', inline=False)
    embed.add_field(name='Server Commands', value='`!remindsvr <reminder>` - set a server reminder\n`!svrreminders`, or `!svrrem` - view list of server reminders\n`!removesvr <number>`, or `!remsvr <number>` - remove a server reminder\n`!clearsvr` - clear all server reminders', inline=False)
    embed.add_field(name='Misc Commands', value="`!help` - print a list of available commands", inline=False)

    await ctx.send(embed=embed)



# HELPER FUNCTIONS
# print all the values of a list within a reminder dictionary on separate lines
def print_dictlist(dict, user):
    if user not in dict["users"]:
        new_dict = {"user" : user, "tasks" : [], "times" : [], "channel" : [], "command" : []}
        dict["users"].append(user)
        dict["reminders"].append(new_dict)

        with open('all_data.json', 'w') as outfile:
            json.dump(dict, outfile, default = str)

    list_str = ""
    index = dict["users"].index(user)

    for i in range(len(dict["reminders"][index]["tasks"])):
        date = datetime.strptime(dict["reminders"][index]["times"][i], "%Y-%m-%d %H:%M:%S")
        list_str = list_str + str(i + 1) + ". " +  dict["reminders"][index]["tasks"][i] + " - " + date.strftime("%Y/%m/%d at %I:%M %p") + "\n"
    return list_str

# Obtain the time for remindme and remindsvr and complete creating reminders by adding the time
def get_time(user_message, name):
    infile = open('all_data.json')
    data = json.load(infile)

    try: 
        datetime_obj = datetime.strptime(user_message, "%Y/%m/%d at %I:%M %p")

    except:
        # make sure we're not adding reminders with invalid times
        index = data["users"].index(name)
        data["reminders"][index]["tasks"].pop()
        data["reminders"][index]["channel"].pop()
        data["reminders"][index]["command"].pop()

        with open('all_data.json', 'w') as outfile:
            json.dump(data, outfile, default = str)

        return ("There was an error due to **invalid formatting** or an **invalid date**.\n\nPlease try creating the reminder again.\nMake sure you type a **valid date** in the **correct format** next time (ex. 2025/08/19 at 5:30 PM).")
    else:
        # make sure the date is valid and in the future
        if datetime_obj <= datetime.now():
            index = data["users"].index(name)
            data["reminders"][index]["tasks"].pop()
            data["reminders"][index]["channel"].pop()
            data["reminders"][index]["command"].pop()

            with open('all_data.json', 'w') as outfile:
                json.dump(data, outfile, default = str)

            return ("There was an error as the date you enter must be in the **future**.\n\nPlease try creating the reminder again.\nMake sure you type a valid date that is in the **future** next time (ex. 2025/08/19 at 5:30 PM).")
        else:
            index = data["users"].index(name)
            data["reminders"][index]["times"].append(datetime_obj)
            all_times.append(datetime_obj)

            with open('all_data.json', 'w') as outfile:
                json.dump(data, outfile, default = str)

            return ("Okay! I've set the reminder for you!")


# check if the input is a valid integer
def is_int(number):
    try:
        int(number)
        return True
    except:
        return False



# run the bot
client.run(TOKEN) # the token was stored in an .env file
