# Avrae → MCP Skill Translation Checklist

Use this checklist to translate Avrae command coverage into MCP skills.

## How to use this checklist
- Mark each item when the command/subcommand is represented in an MCP skill.
- For each completed item, capture:
  - the MCP skill/tool name,
  - argument schema mapping,
  - examples and edge cases,
  - response normalization strategy.

---

## CharGenerator
- [ ] `!randchar [level]`
- [ ] `![randname|name] [race] [option]`
- [ ] `!rollstats`

## Core
- [ ] `![about|stats|info]`
- [ ] `!changelog`
  - [ ] `!changelog [follow|subscribe]`
- [ ] `!ddb`
- [ ] `!invite`
- [ ] `!ping`

## Customization
- [ ] `!alias <kwargs>`
  - [ ] `!alias autofix`
  - [ ] `!alias [delete|remove] <name>`
  - [ ] `!alias [deleteall|removeall]`
  - [ ] `!alias list [page=1]`
  - [ ] `!alias rename <old_name> <new_name>`
  - [ ] `!alias serve <name>`
  - [ ] `!alias [subscribe|sub] <url>`
  - [ ] `!alias [unsubscribe|unsub] <name>`
- [ ] `!cvar [name] [value]`
  - [ ] `!cvar [deleteall|removeall]`
  - [ ] `!cvar list`
  - [ ] `!cvar [remove|delete] <name>`
- [ ] `![globalvar|gvar] [name]`
  - [ ] `!globalvar create [value]`
  - [ ] `!globalvar edit <name> [value]`
  - [ ] `!globalvar editor <name> [user]`
  - [ ] `!globalvar list`
  - [ ] `!globalvar [remove|delete] <name>`
- [ ] `!multiline <cmds>`
- [ ] `!prefix [prefix]`
- [ ] `![servalias|serveralias] <kwargs>`
  - [ ] `!servalias autofix`
  - [ ] `!servalias [delete|remove] <name>`
  - [ ] `!servalias list [page=1]`
  - [ ] `!servalias rename <old_name> <new_name>`
  - [ ] `!servalias [subscribe|sub] <url>`
  - [ ] `!servalias [unsubscribe|unsub] <name>`
- [ ] `![server_settings|servsettings]`
- [ ] `![servervar|svar] [name] [value]`
  - [ ] `!servervar list`
  - [ ] `!servervar [remove|delete] <name>`
- [ ] `![servsnippet|serversnippet] <kwargs>`
  - [ ] `!servsnippet autofix`
  - [ ] `!servsnippet [delete|remove] <name>`
  - [ ] `!servsnippet list [page=1]`
  - [ ] `!servsnippet rename <old_name> <new_name>`
  - [ ] `!servsnippet [subscribe|sub] <url>`
  - [ ] `!servsnippet [unsubscribe|unsub] <name>`
- [ ] `!snippet <kwargs>`
  - [ ] `!snippet autofix`
  - [ ] `!snippet [delete|remove] <name>`
  - [ ] `!snippet [deleteall|removeall]`
  - [ ] `!snippet list [page=1]`
  - [ ] `!snippet rename <old_name> <new_name>`
  - [ ] `!snippet serve <name>`
  - [ ] `!snippet [subscribe|sub] <url>`
  - [ ] `!snippet [unsubscribe|unsub] <name>`
- [ ] `!tembed <teststr>`
- [ ] `!test <teststr>`
- [ ] `![uservar|uvar] [name] [value]`
  - [ ] `!uservar [deleteall|removeall]`
  - [ ] `!uservar list`
  - [ ] `!uservar [remove|delete] <name>`

## Dice
- [ ] `![iterroll|rrr] <iterations> <dice> [dc] [args]`
- [ ] `![monattack|ma|monster_attack] <monster_name> [atk_name] [args]`
  - [ ] `!monattack list <monster_name>`
- [ ] `![moncast|mcast|monster_cast] <monster_name> <spell_name> [args]`
- [ ] `![moncheck|mc|monster_check] <monster_name> <check> [args]`
- [ ] `![monsave|ms|monster_save] <monster_name> <save_stat> [args]`
- [ ] `![multiroll|rr] <iterations> <dice>`
- [ ] `![roll|r] [dice=1d20]`

## GameLog
- [ ] `!campaign [campaign_link]`
  - [ ] `!campaign list`
  - [ ] `!campaign remove <name>`

## GameTrack
- [ ] `!cast <spell_name> [args]`
- [ ] `![customcounter|cc] [name] [modifier]`
  - [ ] `!customcounter create <name> [args]`
  - [ ] `!customcounter [delete|remove] <name>`
  - [ ] `!customcounter edit <name> [args]`
  - [ ] `!customcounter reset [args...]`
  - [ ] `!customcounter [summary|list] [page=1]`
- [ ] `![game|g]`
  - [ ] `!game [coinpurse|coins|coin] [args]`
    - [ ] `!game coinpurse [convert|consolidate]`
  - [ ] `!game [deathsave|ds] [args]`
    - [ ] `!game deathsave [fail|f]`
    - [ ] `!game deathsave reset`
    - [ ] `!game deathsave [success|s|save]`
  - [ ] `!game [hp|HP] [hp]`
    - [ ] `!game hp max`
    - [ ] `!game hp mod <hp>`
    - [ ] `!game hp set <hp>`
  - [ ] `!game [longrest|lr] [args...]`
  - [ ] `!game [shortrest|sr] [args...]`
  - [ ] `!game [spellbook|sb]` (deprecated)
  - [ ] `!game [spellslot|ss] [level] [value] [args...]`
  - [ ] `!game [status|summary]`
  - [ ] `!game thp [thp]`
- [ ] `![spellbook|sb] [args...]`
  - [ ] `!spellbook add <spell_name> [args]`
  - [ ] `!spellbook remove <spell_name>`
  - [ ] `!spellbook [remove_all|removeall]`

## Homebrew
- [ ] `!bestiary [name]`
  - [ ] `!bestiary delete <name>`
  - [ ] `!bestiary import <url>`
  - [ ] `!bestiary list`
  - [ ] `!bestiary server`
    - [ ] `!bestiary server list`
    - [ ] `!bestiary server [remove|delete] <bestiary_name>`
  - [ ] `!bestiary update`
- [ ] `!pack [name]`
  - [ ] `!pack editor <user>`
  - [ ] `!pack list`
  - [ ] `!pack server`
    - [ ] `!pack server list`
    - [ ] `!pack server [remove|delete] <pack_name>`
  - [ ] `!pack [subscribe|sub] <url>`
  - [ ] `!pack [unsubscribe|unsub] <name>`
- [ ] `!tome [name]`
  - [ ] `!tome editor <user>`
  - [ ] `!tome list`
  - [ ] `!tome server`
    - [ ] `!tome server list`
    - [ ] `!tome server [remove|delete] <tome_name>`
  - [ ] `!tome [subscribe|sub] <url>`
  - [ ] `!tome [unsubscribe|unsub] <name>`

## InitTracker
- [ ] `![init|i|I]`
  - [ ] `!init add <modifier> <name> [args]`
  - [ ] `!init [attack|a|action] [atk_name] [args]`
    - [ ] `!init attack list [args...]`
  - [ ] `!init begin [args]`
  - [ ] `!init cast <spell_name> [args]`
  - [ ] `!init [check|c] <check> [args]`
  - [ ] `!init effect <target_name> <effect_name> [args]`
  - [ ] `!init end [args]`
  - [ ] `!init [hp|HP] <name> [hp]`
    - [ ] `!init hp max <name> [hp]`
    - [ ] `!init hp mod <name> <hp>`
    - [ ] `!init hp set <name> <hp>`
  - [ ] `!init [join|cadd|dcadd] [args]`
  - [ ] `!init [list|summary] [args...]`
  - [ ] `!init madd <monster_name> [args]`
  - [ ] `!init [move|goto] [target]`
  - [ ] `!init [next|n]`
  - [ ] `!init nlp`
    - [ ] `!init nlp list`
    - [ ] `!init nlp stopall`
  - [ ] `!init note <name> [note]`
    - [ ] `!init note [remove|delete] <name>`
  - [ ] `!init [offturnattack|aoo|offturnaction|oa] <combatant_name> [atk_name] [args]`
  - [ ] `!init [offturncast|rc|reactcast] <combatant_name> <spell_name> [args]`
  - [ ] `!init [offturncheck|oc] <combatant_name> <check> [args]`
  - [ ] `!init [offturnsave|os] <combatant_name> <save> [args]`
  - [ ] `!init [opt|opts] <name> [args]`
  - [ ] `!init [prev|previous|rewind]`
  - [ ] `!init re <name> [effect]`
  - [ ] `!init remove <name>`
  - [ ] `!init [reroll|shuffle] [args]`
  - [ ] `!init [save|s] <save> [args]`
  - [ ] `!init [skipround|round|skiprounds] [numrounds=1]`
  - [ ] `!init status [name] [args...]`
  - [ ] `!init thp <name> <thp>`

## Lookup
- [ ] `!background <name>`
- [ ] `!class <name> [level]`
- [ ] `!classfeat <name>`
- [ ] `![condition|status] [name]`
- [ ] `!feat <name>`
- [ ] `!item <name>`
- [ ] `!monimage <name>`
- [ ] `!monster <name>`
- [ ] `![race|species] <name>`
- [ ] `![racefeat|speciesfeat] <name>`
- [ ] `![rule|reference] [name]`
- [ ] `!spell <name>`
- [ ] `!subclass <name>`
- [ ] `!token [name] [args]`

## PBPUtils
- [ ] `!br`
- [ ] `!echo <msg>`
- [ ] `!embed <args>`
- [ ] `!techo <seconds> <msg>`

## SheetManager
- [ ] `![action|a|attack] [atk_name] [args]`
  - [ ] `!action [add|create] <name> [args]`
  - [ ] `!action [delete|remove] <name>`
  - [ ] `!action import <data>`
  - [ ] `!action list [args...]`
- [ ] `![character|char] [name]`
  - [ ] `!character channel [name]`
    - [ ] `!character channel [reset|unset]`
  - [ ] `!character delete <name>`
  - [ ] `!character list`
  - [ ] `!character resetall`
  - [ ] `!character server [name]`
    - [ ] `!character server [reset|unset]`
- [ ] `![check|c] <check> [args]`
- [ ] `!csettings [args...]`
- [ ] `!desc`
  - [ ] `!desc [remove|delete]`
  - [ ] `!desc [update|edit] <desc>`
- [ ] `!import <url> [version] [args]`
- [ ] `!portrait`
  - [ ] `!portrait [remove|delete]`
  - [ ] `!portrait [update|edit] <url>`
- [ ] `![save|s] <skill> [args]`
  - [ ] `!save death [args]`
- [ ] `!sheet`
- [ ] `!transferchar <user>`
- [ ] `!update [args]`

## Tutorials
- [ ] `!help [command]`
- [ ] `!tutorial [name]`
  - [ ] `!tutorial end`
  - [ ] `!tutorial list`
  - [ ] `!tutorial skip`

---

## Optional tracking fields per command
Use this template per translated command if you want structured status notes:

```md
- [ ] `!command [args]`
  - MCP skill/tool:
  - Input schema:
  - Output schema:
  - Example prompt(s):
  - Validation notes:
  - Open issues:
```
