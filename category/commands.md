# Commands
  * [Help](#Help)
  * [Code](#Code)
  * [Game](#Game)
  * [Image](#Image)
  * [Insult](#Insult)
  * [Internet](#Internet)
  * [Math](#Math)
  * [Meme](#Meme)
  * [Miscellaneous](#Miscellaneous)
  * [NSFW](#NSFW)
  * [Rank](#Rank)
  * [Server Moderator](#Server-Moderator)
  * [Bot Moderator](#Bot-Moderator)
## Help
  *Shows you the help menu.*

  * `help | h | ? [command | category]` - Gives you help on all commands or a specific command in the bot.

  * `markdown | getMarkdown | md | getMd ` - **`Bot Mod`** Creates and sends the markdown file for the commands.

## Code
  *Commands that have to do with coding!*

  * `brainfuck | brainf | bf <code> [parameters]` - Runs brainfuck code. Kinda confusing stuff at first glance.

  * `convert | conversion | baseConversion | baseConverter [startBase] <endBase> <number>` - Converts a number from one base to another base.

  * `base64 | b64 <conversion> <text>` - Encodes or decodes text to base64.
    * Accepted Parameters for `conversion`
      * `encode | enc | e` - Encode text into base64.
      * `decode | dec | d` - Decode text from base64.

## Game
  *You can play games with these.*

  * `connectFour | connect4 | cf [difficulty]` - Play connect four with Omega Psi.
    * Accepted Parameters for `difficulty`
      * `quit | q | exit` - Allows you to quit the Connect 4 game.

  * `hangman | playHangman [difficulty]` - Let's you play hangman!
    * Accepted Parameters for `difficulty`
      * `easy | simple | e` - Play an easy game of Hangman.
      * `medium | m` - Play a medium game of Hangman.
      * `hard | difficult | h` - Play a hard game of Hangman.
      * `quit | q | exit` - Allows you to quit the hangman game.

  * `rockPaperScissors | rps <action>` - Allows you to play Rock Paper Scissors with me.
    * Accepted Parameters for `action`
      * `rock | r` - Do a rock action.
      * `paper | p` - Do a paper action.
      * `scissors | s` - Do a scissor action.

  * `scramble [difficulty]` - Allows you to guess an unscrambled word.
    * Accepted Parameters for `difficulty`
      * `normal | n | easy | e` - Only each word is scrambled.
      * `expert | hard | difficult` - The entire phrase is scrambled.
      * `quit | q | exit` - Allows you to quit the scramble game.

  * `ticTacToe | ttt [difficulty]` - Lets you play a Tic-Tac-Toe game against Omega Psi.
    * Accepted Parameters for `difficulty`
      * `easy | simple | e` - Play an easy game of Tic-Tac-Toe.
      * `medium | m` - Play a medium game of Tic-Tac-Toe.
      * `hard | difficult | h` - Play a hard game of Tic-Tac-Toe.
      * `quit | q | exit` - Quit your game of Tic-Tac-Toe.

  * `stats | gameStats ` - Gives you stats on the games you've won/lost.

  * `blackOps3 | blackops3 | bo3 <platform> <username>` - Gives you stats on a specific player in Black Ops 3
    * Accepted Parameters for `platform`
      * `xbox | Xbox` - Get Black Ops 3 stats for Xbox.
      * `playstation | psn | PSN` - Get Black Ops 3 stats for Playstation Network (PSN).

  * `blackOps4 | blackops4 | bo4 <platform> <username>` - Gives you stats on a specific player in Black Ops 4
    * Accepted Parameters for `platform`
      * `xbox | Xbox` - Get Black Ops 4 stats for Xbox.
      * `playstation | psn | PSN` - Get Black Ops 4 stats for Playstation Network (PSN).
      * `battleNet` - Get Black Ops 4 stats for Battle.net.

  * `fortnite <platform> <username>` - Gives you stats on a specific player in Fortnite.
    * Accepted Parameters for `platform`
      * `playstation | psn | ps` - Get Fortnite stats for Playstation 4.
      * `xbox | Xbox` - Get Fortnite stats for Xbox.
      * `pc | PC` - Get Fortnite stats for PC.

  * `fortniteItemShop ` - Gives you the current items in the Fortnite Item Shop.

  * `league | leagueOfLegends | LoL <username>` - Gives you stats on a specific Summoner in League of Legends.

## Image
  *Anything having to do with images is here.*

  * `gif | giphy | g [keywords]` - Sends a random gif from Giphy.

  * `dog | doggy | dogMe ` - Sends a random picture of a random dog from the internet.

  * `cat | kitty | catMe ` - Sends a random picture of a random cat from the internet.

  * `avatar | avatarMe ` - Sends a random cute avatar.

  * `robohash | robo [content]` - Sends a robohash avatar based off the text you enter.
    * Accepted Parameters for `content`
      * `random | surprise | surpriseMe` - Allows you to have a completely random robohash to be sent.

  * `timchen | tim | chen | t ` - Sends a random picture of Timchen (a Repl.it moderator) using an API made by [mat#6207](https://repl.it/@mat1)

  * `nasa | NASA | nasaImage | NASAImage | nasaImg | NASAImg [term]` - Gives you a random NASA image given a search term or no search term.

## Insult
  *If you feel in the mood to be insulted, here ya are.*

  * `insult | i [insultLevel]` - Sends you an insult.
    * Accepted Parameters for `insultLevel`
      * `touchy | t` - Soft insults for a soft person.
      * `remorseful | remorse | r` - Harder insults. Might offend you.
      * `noRemorse | noremorse | nr` - Hardcore insults. And I mean it.

  * `addInsult | addI <insultLevel> <insult> [tags]` - Allows you to add your own insult.
    * Accepted Parameters for `insultLevel`
      * `touchy | t` - Soft insults for a soft person.
      * `remorseful | remorse | r` - Harder insults. Might offend you.
      * `noRemorse | noremorse | nr` - Hardcore insults. And I mean it.
    * Accepted Parameters for `tags`
      * `NSFW | nsfw | 18+` - Make the insult an NSFW insult.

  * `listInsults | list | l [insultLevel]` - Lists the insults that can be sent.
    * Accepted Parameters for `insultLevel`
      * `touchy | t` - Soft insults for a soft person.
      * `remorseful | remorse | r` - Harder insults. Might offend you.
      * `noRemorse | noremorse | nr` - Hardcore insults. And I mean it.

  * `approveInsult | approve <value>` - **`Bot Mod`** Approves an insult in the list of pending insults.

  * `denyInsult | deny <value> <reason>` - **`Bot Mod`** Denies an insult in the list of pending insults.

  * `addInsultTag | addTag <value> <tag>` - **`Bot Mod`** Adds a tag to an insult if it is not already there.
    * Accepted Parameters for `tag`
      * `NSFW | nsfw` - An NSFW tag for an insult.

  * `listPendingInsults | pendingInsults ` - **`Bot Mod`** Lists the pending insults.

## Internet
  *All commands that deal with the internet are here.*

  * `movie | mv <query>` - Gives you information about a Movie on IMDb.

  * `tvShow | tv | show <query>` - Gives you information about a TV Show on IMDb.

  * `translate <to> [from] <text>` - Gives you the translation of given text to and from a language.

  * `urban | urbanDictionary | urbanDict <term>` - **`NSFW`** Gives you the top 5 urban dictionary entries for a term.

  * `weather | forecast | getWeather <location>` - Gets the weather for a specified location.

  * `wikipedia | wiki <term>` - Gets a wikipedia entry you type in.

  * `shortenUrl | shorten | shortUrl | url <url>` - Shortens a URL given.

## Math
  *Need help with math? These commands got your back.*

  * `simplify | simp | evaluate | eval <expression>` - Simplifies a mathematical expression.

  * `expand | exp | e <expression>` - Expands a mathematical expression.

  * `factor | f <expression>` - Factors a mathematical expression.

  * `factorial | ! <number>` - Gets the factorial of a number.

  * `solve | system <equation(s)>` - Solves an equation or a system of equations.

  * `substitute | subs <expression> <variables>` - Substitutes variables in an equation.

  * `derivative | derivate | dv <expression>` - Gets the derivative of an expression.

  * `integral | integrate <expression>` - Gets the integral of an expression.

  * `fibonacci | fib <number>` - Gets the fibonacci number of a number.

  * `solveKinematics | solveKine | kine | kinematics [X=] [Xo=] [Xf=] [V=] [Vo=] [Vf=] [a=] [t=]` - Solves for Basic Linear Kinematic Physics. Can be used for Horizontal or Vertical motion. To clarify a variable, make sure you set the variable (Vf=5 a=9.6 etc.)

## Meme
  *Memes, memes, and more memes.*

  * `meme ` - Sends a random meme from Reddit.

  * `areYouAwake <text>` - Sends a generated meme based off of [this](https://i.imgflip.com/2gqv88.jpg) image.

  * `expandingBrain | expBrain <firstText> [secondText] [thirdText] [fourthText] [fifthText] [sixthText] [seventhText] [eighthText] [ninthText] [tenthText] [eleventhText]` - Sends a generated meme based off [this](https://i.imgur.com/JPdmXOY.png) image.

  * `burnLetter <letterText> <spongebobText>` - Sends a generated meme based off of [this](https://tinyurl.com/burnLetter) image.

  * `butILikeThis | thisIsBetter <redCarText> <whiteCarText>` - Sends a generated meme based off of [this](https://i.imgur.com/GzRvZUx.png) image.

  * `carSkidding | carSkid <carText> <straightText> <exitText>` - Sends a generated meme based off of [this](https://tinyurl.com/carSkidding) image.

  * `cardSlam <cardText> <bodyText> <tableText>` - Sends a generated meme based off of [this](https://i.imgur.com/GBMCNYM.jpg) image.

  * `classroomStares <bubbleText>` - Sends a generated meme based off of [this](https://i.imgur.com/3QVQ2V5.jpg) image.

  * `didYouMean [searchText] <didYouMeanText>` - Sends a generated meme based off of [this](https://i.imgur.com/8GpQQun.png) image.

  * `icarlyStopSign | icarlyStop <spencerText> [stopText] <gibbyText>` - Sends a generated meme based off of [this](https://i.imgur.com/MSaTVD2.jpg) image.

  * `mastersBlessing <masterText> <swordText> <apprenticeText>` - Sends a generated meme based off of [this](https://tinyurl.com/mastersBlessing) image.

  * `armHandshake <handsText> <firstArm> <secondArm> [thirdArm] [fourthArm]` - Sends a generated meme based off of [this](https://tinyurl.com/twoArmHandshake) image.

  * `pigeon | isThisAPigeon <pigeonText> <personText> <questionText>` - Sends a generated meme based off of [this](https://i.kym-cdn.com/photos/images/original/001/374/087/be2.png) image.

  * `playstation [triangleText] [squareText] <xText> <circleText>` - Sends a generated meme based off of [this](https://i.imgur.com/ic6R1lS.png) image.

  * `puppetMeme <handText> <puppetText>` - Sends a generated meme based off of [this](https://tinyurl.com/puppetMeme) image.

  * `runAway <chaserText> <runnerText>` - Sends a generated meme based off of [this](https://tinyurl.com/y9zqyq92) image.

  * `saveOne <personText> <leftBehindText> <savedText>` - Sends a generated meme based off of [this](https://tinyurl.com/saveOneMeme) image.

  * `sayItAgain | dexterMeme <topText> <bottomText>` - Sends a generated meme based off of [this](https://i.imgflip.com/16iyn1.jpg?a428353) image.

  * `spontaneousAnger | angerMeme <angerText> <questionText>` - Sends a generated meme based off of [this](https://i.imgur.com/o1NzXyW.jpg) image.

  * `surprisedDwight <dwightText> <angelaText>` - Sends a generated meme based off of [this](https://tinyurl.com/surprisedDwight) image.

  * `surprisedPikachu <firstLine> <secondLine> <thirdLine> [fourthLine] [fifthLine]` - Sends a generated meme based off of [this](https://imgflip.com/s/meme/Surprised-Pikachu.jpg) image.

  * `trojanHorse <hidersText> <horseText> <castleText> <welcomersText>` - Sends a generated meme based off of [this](https://i.imgur.com/pNR2At1.jpg) image.

  * `whoKilledHannibal <ericAndreText> <gunText> <hannibalText> <questionText>` - Sends a generated meme based off of [this](https://i.imgflip.com/28s2gu.jpg) image.

## Miscellaneous
  *Other commands that don't really fit into a category yet.*

  * `advice ` - Gives you a random piece of advice.

  * `choose | choice <choice(s)...>` - Gives you a random choice from a specified list.

  * `chuckNorris | chuck | norris ` - Gives you a random Chuck Norris joke.

  * `color [colorType] <color>` - Gives you the information about a color given either the Hex, RGB, HSL, or CMYK.
    * Accepted Parameters for `colorType`
      * `hex | HEX` - Get color information using a hex code.
      * `rgb | RGB` - Get color information using an RGB tuple.
      * `hsl | HSL` - Get color information using HSL.
      * `cmyk | CMYK` - Get color information using CMYK.

  * `numberFact | number ` - Gives you a fact about a number.

  * `random | rand | randint <start> <end>` - Gives you a random number between the specified range.

  * `tronaldDumpMeme | tronaldMeme | trumpMeme ` - Gives you a random meme from Donald Trump.

  * `tronaldDumpQuote | tronaldQuote | trumpQuote ` - Gives you a random quote from Donald Trump.

  * `ping ` - Pings the bot.

  * `nickname | nick [nickname]` - Changes your nickname.

  * `info | ?? [member]` - Gives you info on a member or the server as saved by the bot.

  * `inviteBot | invite [permissions...]` - Gives you a link so you can invite the bot to your own server.
    * Accepted Parameters for `permissions...`
      * `administrator | admin` - Gives the bot administrator privileges.
      * `viewAuditLog | auditLog | audit` - Gives the bot access to the audit log.
      * `manageServer | mngSvr` - Gives the bot permission to manage the server.
      * `manageRoles | mngRoles` - Gives the bot permission to manage the roles.
      * `manageChannels | mngChnls` - Gives the bot permission to manage the channels.
      * `kickMembers | kickMbrs` - Gives the bot permission to kick members.
      * `banMembers | banMbrs` - Gives the bot permission to ban members.
      * `createInstantInvite | instantInvite | invite` - Gives the bot permission to create an instant invite for the server.
      * `changeNickname | chngNick` - Gives the bot permission to change their nickname.
      * `manageNicknames | mngNick` - Gives the bot permission to manage other people's nicknames.
      * `manageEmojis | mngEmojis` - Gives the bot permission to manage the server's emojis.
      * `manageWebhooks | mngWbhks` - Gives the bot permission to manage the server's webhooks.
      * `viewChannels | viewChnls` - Gives the bot permission to view the channels.
      * `sendMessages | message | msg` - Gives the bot permission to send messages.
      * `sendTtsMessages | ttsMessages` - Gives the bot permission to send TTS (text-to-speech) messages.
      * `manageMessages | mngMsgs` - Gives the bot permission to manage messages.
      * `embedLinks | links` - Gives the bot permission to embed links.
      * `attachFiles | files` - Gives the bot permission to attach files.
      * `readMessageHistory | messageHistory | msgHist` - Gives the bot permission to read the message history.
      * `mentionEveryone` - Gives the bot permission to mention everyone.
      * `useExternalEmojis | externalEmojis | emojis` - Gives the bot permission to use other server's emojis.
      * `addReactions | reactions` - Gives the bot permission to react to messages.
      * `connect` - Gives the bot permission to connect to a voice channel.
      * `speak` - Gives the bot permission to speak in a voice channel.
      * `muteMembers | mute` - Gives the bot permission to mute members in a voice channel.
      * `deafenMembers | deafen` - Gives the bot permission to deafen members in a voice channel.
      * `useMembers` - Gives the bot permission to move members to a different voice channel.
      * `useVoiceActivity | useVoice | voice` - Gives the bot permission to use voice activity in a voice channel.
      * `prioritySpeaker` - Gives the bot permission to the priority speaker.

  * `vote ` - Allows you to get a link to vote for Omega Psi on discordbots.org

  * `github ` - Sends you the Github link for the source code.

  * `replit | repl.it | repl ` - Sends you the Repl.it link for the bot.

  * `uptime ` - Sends a link to see the uptime of Omega Psi.

  * `sendBug | bug | error | feedback <messageType> <message>` - Allows you to send any feedback, bugs, or errors directly to all developers of Omega Psi.
    * Accepted Parameters for `messageType`
      * `bug` - The type of message is a bug in Omega Psi.
      * `error` - Something is going wrong but you don't know what.
      * `feedback` - You want to provide feedback, suggest features, or anything else that doesn't fit into a message type.
      * `moderator` - If you are the Server Owner and you do not have Server Moderator commands showing up in the help menu, use this.

## NSFW
  *An NSFW category for 18+*

  **You should be 18+ to run the commands in this category!**

  **_This category is NSFW._**

  * `boobs | boob ` - **`NSFW`** Sends a random picture of boobs.

  * `booty | ass ` - **`NSFW`** Sends a random picture of some booty.

## Rank
  *The ranking system is strong with this category.*

  **_This category contains commands that can only be run in a Server._**

  * `levelUp [interaction]` - Shows you how many profane words, reactions, or normal messages you need to send to level up.
    * Accepted Parameters for `interaction`
      * `profanity | profane` - Check how many profane words you need to level up.
      * `reactions | reacts` - Check how many reactions you need to level up.
      * `normal | basic` - Check how many regular messages you need to send to level up.

  * `rank | r ` - Shows you your current level and experience in this server.

## Server Moderator
  *Moderate your server with this.*

  **In order to use these commands, you must have the Manage Server permissions.**

  **_This category contains commands that can only be run in a Server._**

  * `addMember | addM | am <member(s)...>` - **`Server Mod`** Allows you to add a member, or members, to the server file manually.

  * `removeMember | removeM | rm <member(s)...>` - **`Server Mod`** Allows you to remove a member, or members, from the server file manually.

  * `activate | enable <command>` - **`Server Mod`** Allows you to activate a command, or commands, in the server.

  * `deactivate | disable <command> [reason]` - **`Server Mod`** Allows you to deactivate a command in the server.

  * `toggleRanking | toggleLeveling | toggleRank | toggleLevel | togRank | togLevel ` - **`Server Mod`** Allows you to toggle the ranking system in the server.

  * `toggleJoinMessage | toggleJoinMsg | togJoinMessage | togJoinMsg ` - **`Server Mod`** Allows you to toggle the join message in the server.

  * `setJoinMessageChannel | setJoinMsgChannel | setJoinMsgChan <channel>` - **`Server Mod`** Allows you to set the channel that the Join Messages are sent in.

  * `setLevel | setLvl <level> <member...>` - **`Server Mod`** Allows you to set the level of a member, or members, in the server.

  * `addPrefix | addPre <prefix>` - **`Server Mod`** Allows you to add a prefix for this server.

  * `removePrefix | removePre | remPre <prefix>` - **`Server Mod`** Allows you to remove a prefix from this server.

  * `setColor | setEmbedColor | embedColor <category> <color>` - **`Server Mod`** Allows you to set the embed color of a specific category in this server.
    * Accepted Parameters for `category`
      * `code` - Allows you to set the color of the Code category.
      * `game` - Allows you to set the color of the Game category.
      * `image` - Allows you to set the color of the Image category.
      * `insult` - Allows you to set the color of the Insult category.
      * `internet` - Allows you to set the color of the Internet category.
      * `math` - Allows you to set the color of the Math category.
      * `misc` - Allows you to set the color of the Misc category.
      * `nsfw` - Allows you to set the color of the NSFW category.
      * `rank` - Allows you to set the color of the Rank category.

  * `setServerName | setSvrName <name>` - **`Server Mod`** Allows you to set the Server's name.

  * `createInvite | createServerInvite | getInvite | getServerInvite [infinite]` - **`Server Mod`** Allows you to create an invite to this server.
    * Accepted Parameters for `infinite`
      * `True | true | T | t | Yes | yes | Y | y` - Set the server invite to never expire.
      * `False | false | F | f | No | no | N | n` - Set the server invite to expire.

  * `addRole <name> [colour]` - **`Server Mod`** Adds a role to the server.

  * `removeRole <name>` - **`Server Mod`** Removes a role from the server.

  * `kickMember | kickMbr <member(s)...>` - **`Server Mod`** Kicks a member, or members, from the server.

  * `banMember | banMbr <member(s)...>` - **`Server Mod`** Bans a member, or members, from the server.

  * `addMemberRole | addMbrRole | giveRole <member> <role(s)...>` - **`Server Mod`** Gives a member the mentioned role(s).

  * `removeMemberRole | removeMbrRole | takeRole <member> <role(s)...>` - **`Server Mod`** Removes the mentioned role(s) from a member.

  * `setMemberRoles | setMbrRoles | setRoles <member> <role(s)...>` - **`Server Mod`** Sets the roles for a member.

## Bot Moderator
  *Very private stuff.*

  **You must be a Bot Moderator to run these commands.**

  * `addBotModerator | addBotMod | abm <member(s)...>` - **`Bot Mod`** Allows you to add a bot moderator to the bot.

  * `removeBotModerator | removeBotMod | remBotMod | rbm <member(s)...>` - **`Bot Mod`** Allows you to remove a bot moderator from the bot.

  * `activateGlobally | enableGlobally <command(s)>` - **`Bot Mod`** Allows you to activate a command, or commands, globally.

  * `deactivateGlobally | disableGlobally <command> [reason]` - **`Bot Mod`** Allows you to deactivate a command globally.

  * `botInfo | bi ` - **`Bot Mod`** Allows you to get the info about the bot.

  * `servers | botServers [markdown]` - **`Bot Mod`** Allows you to get a list of servers the bot is in.

  * `setStatus | status <activity> <text>` - **`Bot Mod`** Allows you to change the presence of the bot.
    * Accepted Parameters for `activity`
      * `playing | Playing` - The playing activity type.
      * `streaming | Streaming` - The streaming activity type.
      * `listening | Listening | listening to | Listening to` - The listening activity type.
      * `watching | Watching` - The watching activity type.

  * `todo [action] [item]` - **`Bot Mod`** Adds, removes, or lists things in the TODO list.
    * Accepted Parameters for `action`
      * `add | a` - Adds something to the TODO list.
      * `remove | r` - Removes something from the TODO list.

  * `stop | quit | kill [process]` - **`Bot Mod`** Kills the bot.

  * `debug ` - **`Bot Mod`** Debugs the bot.
