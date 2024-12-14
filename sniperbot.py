
import discord
from discord.ext import commands
import datetime
import threading
import os
import re
import discord
from discord.ext import commands
import datetime
import threading
import os
import re
from io import StringIO
from contextlib import redirect_stdout
import requests  # For kanye quotes
import json
import asyncio
import random

from schoology import Student, SCHOOL_URLS
from uwuify import uwuify
from rtdb import ref, increment
from face_api import FaceAPI


class Log:

  __slots__ = 'is_valid', 'content', 'author', 'attachments', 'embeds', 'color', 'created_at', 'deleted_at'

  # Initialize context structure
  def __init__(self, message, color=0x202225):

    self.is_valid = message is not None

    if self.is_valid:

      # Save variables
      self.content = message.content
      self.author = message.author
      self.attachments = message.attachments
      self.embeds = message.embeds
      self.color = color
      self.created_at = message.created_at

    self.deleted_at = datetime.datetime.now()


class SchoologyView(discord.ui.View):

  def __init__(self, students, author, *, confidences=None):
    super().__init__()
    self.i = 0
    self.students = students
    self.author = author
    self.confidences = confidences
    self.frst_button = discord.ui.Button(emoji='<:first:940169691425566741>')
    self.prev_button = discord.ui.Button(emoji='<:left:940157746723061810>')
    self.next_button = discord.ui.Button(emoji='<:right:940157728083570748>')
    self.last_button = discord.ui.Button(emoji='<:last:940169703177977866>')
    self.frst_button.callback = self.frst_callback
    self.prev_button.callback = self.prev_callback
    self.next_button.callback = self.next_callback
    self.last_button.callback = self.last_callback
    self.add_item(self.frst_button)
    self.add_item(self.prev_button)
    self.add_item(self.next_button)
    # self.add_item(self.last_button)
    self.disable_buttons()
    self.embed = discord.Embed(color=0x202225)
    self.update_embed()

  async def on_timeout(self):
    self.frst_button.disabled = self.prev_button.disabled = True
    self.next_button.disabled = self.last_button.disabled = True
    try: await self.message.edit(view=self)
    except discord.errors.NotFound: print("SchoologyView message was already deleted")

  def update_embed(self):
    student = self.students[self.i]
    self.embed.title = f'{student.name}'
    student_info = []

    if student.id is not None:
      id_type = 'Student' if student.id.isdigit() else 'Teacher'
      mailto_url = f'https://mailto.kamiak.org/{student.id}'
      student_info.append(f'{id_type} ID: [{student.id}]({mailto_url})')

    school_name = student.school[-1]
    school_url = SCHOOL_URLS.get(school_name, "https://www.mukilteoschools.org/")
    student_info.append(f'School: [{school_name}]({school_url})')
    
    if self.confidences is not None:
      student_info.append(f'Confidence: `{self.confidences[self.i]:.3f}%`')

    self.embed.description = '\n'.join(student_info)
    self.embed.set_image(url=student.image[-1])
    self.embed.set_footer(text=f'{self.i+1} / {len(self.students)}')

  async def update(self, interaction):
    self.update_embed()
    await interaction.response.edit_message(embed=self.embed, view=self)

  def disable_buttons(self):
    self.frst_button.disabled = self.prev_button.disabled = not 0 <= self.i-1
    self.next_button.disabled = self.last_button.disabled = not self.i+1 < len(self.students)
  
  async def change_index(self, interaction, i):
    # if interaction.user != self.author: return
    self.i = i
    self.disable_buttons()
    await self.update(interaction)

  async def prev_callback(self, interaction):
    await self.change_index(interaction, self.i-1)

  async def next_callback(self, interaction):
    await self.change_index(interaction, self.i+1)

  async def frst_callback(self, interaction):
    await self.change_index(interaction, 0)
  
  async def last_callback(self, interaction):
    await self.change_index(interaction, len(self.students)-1)


class MudaeView(discord.ui.View):

  def __init__(self, student:Student):
    super().__init__()
    self.student = student
    self.button = discord.ui.Button(emoji='<:heart1:1024122660726259743>')
    self.button.callback = self.on_claim
    self.add_item(self.button)
    # Create embed
    self.embed = discord.Embed(color=0xff9c2c)
    self.embed.title = f'{student.name}'
    self.embed.description = \
      (f'{"Student" if student.id.isdigit() else "Teacher"} ID: [{student.id}](https://mailto.kamiak.org/{student.id})' if student.id is not None else '')+'\n'\
      f'School: [{student.school[-1]}]({SchoologyView.SCHOOL_URLS.get(student.school[-1], "https://www.mukilteoschools.org/")})'+'\n'\
      f'Click the button to claim!'
    self.embed.set_image(url=student.image[-1])

  async def on_timeout(self):
    self.button.disabled = True
    try: await self.message.edit(view=self)
    except discord.errors.NotFound: print("MudaeView message was already deleted")

  async def on_claim(self, interaction:discord.Interaction):
    self.button.disabled = True
    self.embed.color = 0x670d08
    self.embed.description = self.embed.description.replace('\nClick the button to claim!', '')
    self.embed.set_footer(text=f'Belongs to {interaction.user.display_name}', icon_url=interaction.user.display_avatar.url)
    await interaction.response.edit_message(embed=self.embed, view=self)


async def execute_and_capture(message: discord.Message) -> str:
  """Execute and capture stdout. Returns stdout or the exception."""
  code = message.content.removeprefix('```python').removesuffix('```')
  try:
    out = StringIO()
    exec('async def __FUNCTION(message):\n  '+code.replace('\n', '\n  '), globals())
    with redirect_stdout(out): await __FUNCTION(message)  # type: ignore
    return out.getvalue()
  except Exception as e:
    return e


async def get_snipe_embed(ctx: Log) -> discord.Embed:
  """Returns embed for the snipe"""

  # Return same embed if message is an embed **sent by this bot**
  if ctx.author == bot.user and len(ctx.embeds) > 0:
    embed = ctx.embeds[0]
    ctx.embeds = ctx.embeds[1:]
    return embed

  # Create embed and return
  embed = discord.Embed(description=ctx.content, color=ctx.color) # 0xbb0a1e
  try: embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
  except: embed.set_author(name='Unknown User', icon_url=r'https://cdn.discordapp.com/embed/avatars/0.png')
  embed.timestamp = ctx.created_at
  return embed


class TemporaryFile(discord.File):
  """Temporary attachment file that deletes its referenced file on destruction"""

  IMAGE_EXTENSIONS = '.png', '.jpg', '.jpeg', '.gif'

  def __init__(self, attachment: discord.Attachment):
    self.attachment = attachment
    self.name = attachment.filename
    self.path = f'tmp/{self.name}'
    super().__init__(self.path)
  
  @staticmethod
  async def save(attachment: discord.Attachment):
    await attachment.save('tmp/'+attachment.filename)
    return TemporaryFile(attachment)

  def __del__(self):
    os.remove(self.path)
  
  def is_image(self):
    return any(self.name.endswith(ext) for ext in TemporaryFile.IMAGE_EXTENSIONS)
 

async def send_deleted_embeds(channel: discord.TextChannel, ctx: Log):
  for embed in ctx.embeds: await channel.send(embed=embed)


async def snipe(channel: discord.channel, send=None):
  """Snipes a deleted discord message"""
  
  if send is None: send = channel.send

  if channel.id not in history:
    await send("There's nothing to snipe!")
    return

  # Find deleted message
  ctx = history[channel.id].pop()
  if not history[channel.id]: del history[channel.id]  # Clean channel history

  # If message is invalid tell the user and terminate process
  if not ctx.is_valid:
    await send('Message is unavailable (bot is being updated).')
    return

  try:

    embed = await get_snipe_embed(ctx)

    # Send normally if it does not have any attachments
    if not ctx.attachments:
      await send(embed=embed)
      await send_deleted_embeds(channel, ctx)
      return
    
    file = await TemporaryFile.save(ctx.attachments[0])
    
    # Send file with embed if file is an image
    if file.is_image():
      embed.set_image(url='attachment://'+file.name)
      await send(embed=embed, file=file)
      await send_deleted_embeds(channel, ctx)
      return
    
    # Send file and embed separately
    await send(embed=embed)
    await send_deleted_embeds(channel, ctx)
    await channel.send(file=file)


  except discord.errors.Forbidden:

    # Put message back in cache if it was sniped while bot was muted or something
    if channel.id not in history: history[channel.id] = []
    history[channel.id].insert(0, ctx)  # Front-based stack


async def dox_image(image_url: str, author: discord.User, send):
  """Finds someone's school picture, school, and student id from an image url"""
  try:
    async with FaceAPI() as fa:
      results = await fa.search_face(image_url)
    students = [student_dict[result[0]] for result in results]
    confidences = [result[1] for result in results]

    view = SchoologyView(students, author, confidences=confidences)
    view.message = await send(embed=view.embed, view=view)
    ref.child(f'waifus/{students[0].url[::-1].split("/", 2)[1][::-1]}/doxxes').transaction(increment)
  except:
    await send('No faces (or multiple faces) were detected in the image')

async def dox(text: str, author: discord.User, send):
  """Finds someone's school picture, school, and student id"""
  query = text.strip().lower().split(' ')[2:]
  students = [
    student
    for student, _ in sorted(
      [
        (student, matches)
        for student in data
        for matches in [sum(
          sum(
            (1000000 if param == student.id else 1)*(1000 if len(param) == len(name) else 1)*(5*(len(query)-param_i))
            for name in student.name.lower().split(' ')
            if param in name or param == student.id
          )
          for param_i, param in enumerate(query)
        )]
        if matches > 0
      ],
      key=(lambda x: x[1]),
      reverse=True
    )
  ]
  if len(students) == 0:
    await send("That person doesn't exist!")
  else:
    view = SchoologyView(students, author)
    view.message = await send(embed=view.embed, view=view)
    ref.child(f'waifus/{students[0].url[::-1].split("/", 2)[1][::-1]}/doxxes').transaction(increment)


class SniperBot(commands.Bot):
  def __init__(self):
    intents = discord.Intents.default()
    intents.members = True
    intents.messages = True
    intents.message_content = True
    super().__init__('', intents=intents, status=discord.Status.do_not_disturb, activity=discord.Activity(name='snipe, pls dox', type=2))
    self.synced = False
  
  async def on_ready(self):
    if not self.synced:
      await self.tree.sync()
      self.synced = True
    print(f'[sniper] :: Logged in as {bot.user}')


TOKEN = os.environ['TOKEN']
CLEAR_LIMIT = datetime.timedelta(minutes=30)
CLEAR_DELAY = datetime.timedelta(minutes=5)
SNIPE_DELAY = datetime.timedelta(seconds=60)

bot = SniperBot()

history = {}
admins = [557233155866886184, 650900479663931413]
student_dict = {student_id: Student(student) for student_id, student in json.load(open('data.json', 'r')).items()}
data = list(student_dict.values())  # Schoology data
data_school = {}  # Students per school
for student in data:
  if student.school[-1] not in data_school: data_school[student.school[-1]] = []
  data_school[student.school[-1]].append(student)
if not os.path.exists('tmp'): os.mkdir('tmp')


@bot.hybrid_command(name='snipe', description='Bring back the most recently deleted message')
async def snipe_command(ctx: commands.Context):
  await snipe(ctx.channel, ctx.send)

@bot.hybrid_command(name='dox', description="Find someone's school picture, school, and student id")
async def dox_command(ctx: commands.Context, *, name: str):
  await dox(f'pls dox {name}', ctx.author, ctx.send)


@bot.event
async def on_message(message): 
  # Stop execution if sender is this bot
  # if message.author == bot.user: return

  # Execute message if it is send by admin and is enclosed with "```"s
  if message.author.id in admins and message.content.startswith('```python') and message.content.endswith('```'):
    result = await execute_and_capture(message)
    await message.channel.send(result)
    return

  # Find first word in string: re.sub(r"^\W+", "", mystring)
  # Find first 10 words in message
  match re.findall(r'\w+', message.content.lower()):


    # "Snipe" function
    case ['snipe', *_] | ['pls' | 'plz', 'snipe']:

      # if message.author == bot.user: await message.delete()
      
      await snipe(message.channel)

    
    # Dox by image url
    case ['pls' | 'plz', 'dox' | 'doxx' | 'snipe', *_] if 'https://' in message.content or 'http://' in message.content:

      matches = re.findall(r'((http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-]))', message.content)
      await dox_image(matches[0][0], message.author, message.channel.send)

    # Dox by image upload
    case ['pls' | 'plz', 'dox' | 'doxx' | 'snipe'] if message.attachments:

      await dox_image(message.attachments[0].url, message.author, message.channel.send)

    # Dox by name query
    case ['pls' | 'plz', 'dox' | 'doxx' | 'snipe', _, *_]:

      # if message.guild is not None and message.guild.id == 836698659071590452:
      #   await message.channel.send('Please use `/search <person>` instead next time, thanks!')

      await dox(message.content, message.author, message.channel.send)
    
    
    # User wants to roll
    case ['pls' | 'plz', category, *school] if category in ['roll', 'r', 'kamiak', 'k', 'mariner', 'm']:

      # Return if user is using command in dms
      if isinstance(message.channel, discord.DMChannel):
        await message.channel.send('This command can only be used from a server!')
        return

      # Roll student
      match category:
        case 'roll' | 'r':
          school = school.join(' ')
          if school == '':
            choices = data
          else:
            choices = data_school.get(school.title(), data_school.get(school.upper(), None))
            if choices == None:
              await message.channel.send('School couldn\'t be found. The full command is `pls roll <school>` without the High/Middle School at the end.')
              return
        case 'kamiak' | 'k': choices = data_school['Kamiak']
        case 'mariner' | 'm': choices = data_school['Mariner']

      student = random.choice(choices)

      # Send embed
      view = MudaeView(student)
      view.message = await message.channel.send(embed=view.embed, view=view)

      
    # User wants to uwu text
    case ['pls' | 'plz', command, _, *_] if command in ['uwu', 'uwuify']:
      await message.channel.send(uwuify(message.content[message.content.index(command)+len(command)+1:]))


    # User wants to be reminded
    case ['pls' | 'plz', 'remind', *_]:
      try:
        time, text = message.content[message.content.index('remind')+7:].split(' ', 1)
        number = float(time[:-1])
        seconds = number*{'s': 1, 'm': 60, 'h': 3600, 'd': 86400, 'w': 604800, 'y': 31557600}[time[-1].lower()]
      except:
        await message.channel.send("Sorry, I couldn't understand")
        return
      await message.channel.send(f"Reminding in {seconds} seconds...")
      await asyncio.sleep(seconds)
      await message.channel.send(f'<@{message.author.id}> {text}')


    # Kanye is in words
    case [*words] if 'kanye' in words:

      response = requests.get(r'https://api.kanye.rest/')
      while not response.ok: response = requests.get(r'https://api.kanye.rest/')

      quote = response.json()['quote']
      if quote[-1].isalpha(): quote += '.'

      embed = discord.Embed(description=quote, color=0x202225)
      embed.set_footer(text='- Kanye West')

      await message.channel.send(embed=embed)

    
    # 'pls waifu' command
    case ['pls' | 'plz', tag] if tag in ['w', 'uniform', 'maid', 'waifu', 'oppai']:
      if tag == 'w': tag == 'waifu'

      url = r'https://api.waifu.im/search?included_tags='+tag
      response = requests.get(url)
      while not response.ok: response = requests.get(url)
      image_data = response.json()['images'][0]

      image_url = image_data['url']
      source_url = image_data['source']
      height = image_data['height']
      width = image_data['width']

      embed = discord.Embed(color=0x202225)
      embed.title = f'Image Result'
      embed.description = f'[Source]({source_url}) · {width}x{height}'
      embed.set_image(url=image_url)
      embed.set_footer(text='powered by waifu.im')

      await message.channel.send(embed=embed) 


#   # Analyze text and possibly respnod
#   case _:
#     try:
#       tone_responses = {
#         'impolite': {
#           'confidence': 0.9,
#           'responses': [
#           "Didn't ask",
#           'Omg pls stfu',
#           'uwu',
#           'L',
#           ]
#         },
#         'frustrated': {
#           'confidence': 0.89,
#           'responses': [
#             'Cool your jets',
#             'Stop harshing the vibe',
#             'Daddy chill',
#             'Calm thy tits',
#             'Mald',
#           ]
#         },
#         'sad': {
#           'confidence': 0.88,
#           'responses': [
#             'Cope',
#             'Cry about it',
#             'Fry about it',
#           ]
#         }
#       }
#       analytics = analyze(message.content)
#       tone = analytics['classifications'][0]
#       if tone['class_name'] in tone_responses and tone['confidence'] > tone_responses[tone['class_name']]['confidence'] and random.random() < 0.2:
#         await message.channel.send(random.choice(tone_responses[tone['class_name']]['responses']))
#       print(analytics['classifications'][:3])
#     except:
#       pass



async def on_raw_message_action(payload):

  # Message is in cache
  if payload.cached_message is not None:

    message = payload.cached_message

    if message.author == bot.user and len(message.components) > 0: return  # Don't save if message has buttons

    # if message.author.id == 674785149556097054: return  # Aiden

    kwargs = {}
    if message.author.id == 761148487483785226: kwargs['color'] = 0xcc8899

    # Bot can now snipe its own messages
    # # Stop execution if sender is this bot
    # if message.author == bot.user: return

    # Message has already been deleted recently (in channel)
    if message.channel.id in history and \
    history[message.channel.id][0].is_valid and \
    datetime.datetime.now()-history[message.channel.id][0].deleted_at < SNIPE_DELAY:

      # Put deleted message in queue
      history[message.channel.id].append(Log(message, **kwargs))

    # Sender has not deleted another message recently
    else:

      # Log message normally
      history[message.channel.id] = [Log(message, **kwargs)]


@bot.event
async def on_raw_message_delete(payload):
  await on_raw_message_action(payload)


@bot.event
async def on_raw_message_edit(payload):
  await on_raw_message_action(payload)


def mem_clear():

  # Recurse
  thread = threading.Timer(CLEAR_DELAY.seconds, mem_clear)
  thread.daemon = True
  thread.start()

  # Get current time
  now = datetime.datetime.now()

  # Remove old logs from history
  for channel_id, log in history.copy().items():

    # Remove old logs until log is accepted  X--(history is sorted)--X
    if now-log[0].deleted_at > CLEAR_LIMIT:

      del history[channel_id]

    #if now-log[0].deleted_at < CLEAR_LIMIT: break
    #del history[channel_id]

  # Remove files from temp to free storage
  for filename in os.listdir('tmp'):
      os.remove('tmp/'+filename)


# Start clearing memory (recursive thread)
mem_clear()

# Start bot on Discord
bot.run(TOKEN)
message.txt
21 KB