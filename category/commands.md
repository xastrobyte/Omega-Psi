# Commands
## Help
  * `help | h | ? [command]` - Gives you help on all commands or a specific command in the bot.

  * `info | ?? [member]` - Gives you info on a member or the server as saved by the bot.

  * `inviteBot | invite [permissions...]` - Gives you a link so you can invite the bot to your own server.
    * Accepted Parameters For permissions...
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

  * `sendBug | bug | error | feedback <messageType> <message>` - Allows you to send any feedback, bugs, or errors directly to all developers of Omega Psi.
    * Accepted Parameters For messageType
      * `bug` - The type of message is a bug in Omega Psi.
      * `error` - Something is going wrong but you don't know what.
      * `feedback` - You want to provide feedback, suggest features, or anything else that doesn't fit into a message type.
      * `moderator` - If you are the Server Owner and you do not have Server Moderator commands showing up in the help menu, use this.

  * `markdown | getMarkdown | md | getMd None` - Creates and sends the markdown file for the commands.

## Code
  * `brainfuck | brainf | bf <code> [parameters]` - Runs brainfuck code. Kinda confusing stuff at first glance.

## Game
  * `hangman | playHangman [difficulty]` - Let's you play hangman!
    * Accepted Parameters For difficulty
      * `easy | simple | e` - Play an easy game of hangman.
      * `medium | m` - Play a medium game of hangman.
      * `hard | difficult | h` - Play a hard game of hangman.
      * `quit | q | exit` - Allows you to quit the hangman game.

  * `scramble [difficulty]` - Allows you to guess an unscrambled word.
    * Accepted Parameters For difficulty
      * `normal | n | easy | e` - Only each word is scrambled.
      * `expert | hard | difficult` - The entire phrase is scrambled.
      * `quit | q | exit` - Allows you to quit the scramble game.

## Gif
  * `gif | giphy | g [keywords]` - Sends a random gif from Giphy.

  * `theOffice | office | o None` - Sends a random gif related to The Office.

  * `parksAndRec | parks | pnr None` - Sends a random gif related to Parks and Rec.

  * `brooklyn99 | b99 | 99 None` - Sends a random gif related to Brooklyn Nine-Nine.

## Insult
  * `insult | i [insultLevel]` - Sends you an insult.
    * Accepted Parameters For insultLevel
      * `touchy | t` - Soft insults for a soft person.
      * `remorseful | remorse | r` - Harder insults. Might offend you.
      * `noRemorse | noremorse | nr` - Hardcore insults. And I mean it.

  * `addInsult | addI | add <insultLevel> <insult>` - Allows you to add your own insult.
    * Accepted Parameters For insultLevel
      * `touchy | t` - Soft insults for a soft person.
      * `remorseful | remorse | r` - Harder insults. Might offend you.
      * `noRemorse | noremorse | nr` - Hardcore insults. And I mean it.

  * `listInsults | list | l [insultLevel]` - Lists the insults that can be sent.
    * Accepted Parameters For insultLevel
      * `touchy | t` - Soft insults for a soft person.
      * `remorseful | remorse | r` - Harder insults. Might offend you.
      * `noRemorse | noremorse | nr` - Hardcore insults. And I mean it.

## Math
  * `factor | f <expression>` - Factors a mathematical expression.

  * `fibonacci | fib <number>` - Gets the fibonacci number of a number.

  * `derivative | derivate | dv <expression>` - Gets the derivative of an expression.

  * `simplify | simp | evaluate | eval <expression>` - Simplifies a mathematical expression.

  * `factorial | ! <number>` - Gets the factorial of a number.

  * `solve | system <equation(s)>` - Solves an equation or a system of equations.

  * `expand | exp | e <expression>` - Expands a mathematical expression.

  * `integral | integrate <expression>` - Gets the integral of an expression.

  * `substitute | subs <expression> <variables>` - Substitutes variables in an equation.

## Rank
  * `rank | r None` - Shows you your current level and experience in this server.

## Weather
  * `weather | getWeather <location>` - Gets the weather for a specified location.

## Server Moderator
  * `addMember | addM | am <member(s)...>` - Allows you to add a member, or members, to the server file manually.

  * `removeMember | removeM | rm <member(s)...>` - Allows you to remove a member, or members, from the server file manually.

  * `addModerator | addMod <member(s)...>` - Allows you to add a moderator, or moderators, to the server (only for Omega Psi).

  * `removeModerator | removeMod | remMod <member(s)...>` - Allows you to remove a moderator, or moderators, from the server (only for Omega Psi).

  * `activate | enable <command>` - Allows you to activate a command, or commands, in the server.

  * `deactivate | disable <command> [reason]` - Allows you to deactivate a command in the server.

  * `toggleRanking | toggleLeveling | toggleRank | toggleLevel | togRank | togLevel None` - Allows you to toggle the ranking system in the server.

  * `toggleJoinMessage | toggleJoinMsg | togJoinMessage | togJoinMsg None` - Allows you to toggle the join message in the server.

  * `setJoinMessageChannel | setJoinMsgChannel | setJoinMsgChan <channel>` - Allows you to set the channel that the Join Messages are sent in.

  * `setLevel | setLvl <level> <member...>` - Allows you to set the level of a member, or members, in the server.

  * `addPrefix | addPre <prefix>` - Allows you to add a prefix for this server.

  * `removePrefix | removePre | remPre <prefix>` - Allows you to remove a prefix from this server.

  * `setServerName | setSvrName <name>` - Allows you to set the Server's name.

  * `createInvite | createServerInvite | getInvite | getServerInvite [infinite]` - Allows you to create an invite to this server.
    * Accepted Parameters For infinite
      * `True | true | T | t | Yes | yes | Y | y` - Set the server invite to never expire.
      * `False | false | F | f | No | no | N | n` - Set the server invite to expire.

  * `addRole <name> [colour]` - Adds a role to the server.

  * `removeRole <name>` - Removes a role from the server.

  * `kickMember | kickMbr <member(s)...>` - Kicks a member, or members, from the server.

  * `banMember | banMbr <member(s)...>` - Bans a member, or members, from the server.

  * `addMemberRole | addMbrRole | giveRole <member> <role(s)...>` - Gives a member the mentioned role(s).

  * `removeMemberRole | removeMbrRole | takeRole <member> <role(s)...>` - Removes the mentioned role(s) from a member.

  * `setMemberRoles | setMbrRoles | setRoles <member> <role(s)...>` - Sets the roles for a member.

## Bot Moderator
  * `addBotModerator | addBotMod | abm <member(s)...>` - Allows you to add a bot moderator to the bot.

  * `removeBotModerator | removeBotMod | remBotMod | rbm <member(s)...>` - Allows you to remove a bot moderator from the bot.

  * `activateGlobally | enableGlobally <command(s)>` - Allows you to activate a command, or commands, globally.

  * `deactivateGlobally | disableGlobally <command> [reason]` - Allows you to deactivate a command globally.

  * `botInfo | bi None` - Allows you to get the info about the bot.

  * `servers | botServers None` - Allows you to get a list of servers the bot is in.

  * `setStatus | status <activity> <text>` - Allows you to change the presence of the bot.
    * Accepted Parameters For activity
      * `playing | Playing` - The playing activity type.
      * `streaming | Streaming` - The streaming activity type.
      * `listening | Listening` - The listening activity type.
      * `watching | Watching` - The watching activity type.

  * `stop | quit | kill None` - Kills the bot.
