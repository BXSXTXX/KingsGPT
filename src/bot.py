import os
import openai
import discord
from random import randrange
from src.aclient import client
from discord import app_commands
from src import log, art, personas, responses
logger = log.setup_logger(__name__)
def run_discord_bot():
    @client.event
    async def on_ready():
        await client.send_start_prompt()
        await client.tree.sync()
        logger.info(f'Bastixx Script mit dem Bot {client.user} synchonisiert!')
    @client.tree.command(name="chat", description="Schreibe mit ChatGPT hier auf Königsmine!")
    async def chat(interaction: discord.Interaction, *, message: str):
        if client.is_replying_all == "True":
            await interaction.response.defer(ephemeral=False)
            await interaction.followup.send(
                "> **WARNUNG: Du bist im ´repyALL´ modus. Wenn du Slashcommands nutzen möchtest, wechsle zum normalen Modus mit  `/replyall`!**")
            logger.warning("\x1b[31mFehler: Slashcommands sind deaktiviert. \x1b[0m")
            return
        if interaction.user == client.user:
            return
        username = str(interaction.user)
        channel = str(interaction.channel)
        logger.info(
            f"\x1b[31m{username}\x1b[0m : /chat [{message}] in ({channel})")
        await client.send_message(interaction, message)
    @client.tree.command(name="private", description="Aktiviere den Privaten modus!")
    async def private(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        if not client.isPrivate:
            client.isPrivate = not client.isPrivate
            logger.warning("\x1b[31mPrivater Modus aktiviert.\x1b[0m")
            await interaction.followup.send(
                "> **INFO: Ab jetzt werden Nachrichten nicht mehr öffentlich gesendet. Wenn du öffentliche Antworten aktivieren möchtest, schreibe `/public`**")
        else:
            logger.info("Fehler: Privater modus ist schon aktiv!")
            await interaction.followup.send(
                "> **WARNUNG: Der Private Modus ist schon aktiv. Wenn du ihn deaktivieren möchtest, schreibe `/public`!**")

    @client.tree.command(name="public", description="Aktiviere öffentliche Antworten")
    async def public(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        if client.isPrivate:
            client.isPrivate = not client.isPrivate
            await interaction.followup.send(
                "> **INFO: Next, the response will be sent to the channel directly. If you want to switch back to private mode, use `/private`**")
            logger.warning("\x1b[31mSwitch to public mode\x1b[0m")
        else:
            await interaction.followup.send(
                "> **WARN: You already on public mode. If you want to switch to private mode, use `/private`**")
            logger.info("You already on public mode!")


    @client.tree.command(name="replyall", description="Toggle replyAll access")
    async def replyall(interaction: discord.Interaction):
        client.replying_all_discord_channel_id = str(interaction.channel_id)
        await interaction.response.defer(ephemeral=False)
        if client.is_replying_all == "True":
            client.is_replying_all = "False"
            await interaction.followup.send(
                "> **INFO: Next, the bot will response to the Slash Command. If you want to switch back to replyAll mode, use `/replyAll` again**")
            logger.warning("\x1b[31mSwitch to normal mode\x1b[0m")
        elif client.is_replying_all == "False":
            client.is_replying_all = "True"
            await interaction.followup.send(
                "> **INFO: Next, the bot will disable Slash Command and responding to all message in this channel only. If you want to switch back to normal mode, use `/replyAll` again**")
            logger.warning("\x1b[31mSwitch to replyAll mode\x1b[0m")


    @client.tree.command(name="chat-model", description="Switch different chat model")
    @app_commands.choices(choices=[
        app_commands.Choice(name="Official GPT-3.5", value="OFFICIAL"),
        app_commands.Choice(name="Ofiicial GPT-4.0", value="OFFICIAL-GPT4"),
        app_commands.Choice(name="Website ChatGPT-3.5", value="UNOFFICIAL"),
        app_commands.Choice(name="Website ChatGPT-4.0", value="UNOFFICIAL-GPT4"),
        app_commands.Choice(name="Bard", value="Bard"),
    ])

    async def chat_model(interaction: discord.Interaction, choices: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=False)
        original_chat_model = client.chat_model
        original_openAI_gpt_engine = client.openAI_gpt_engine

        try:
            if choices.value == "OFFICIAL":
                client.openAI_gpt_engine = "gpt-3.5-turbo"
                client.chat_model = "OFFICIAL"
            elif choices.value == "OFFICIAL-GPT4":
                client.openAI_gpt_engine = "gpt-4"
                client.chat_model = "OFFICIAL"
            elif choices.value == "UNOFFICIAL":
                client.openAI_gpt_engine = "gpt-3.5-turbo"
                client.chat_model = "UNOFFICIAL"
            elif choices.value == "UNOFFICIAL-GPT4":
                client.openAI_gpt_engine = "gpt-4"
                client.chat_model = "UNOFFICIAL"
            elif choices.value == "Bard":
                client.chat_model = "Bard"
            else:
                raise ValueError("Hoppla: Ungültige auswahl!")

            client.chatbot = client.get_chatbot_model()
            await interaction.followup.send(f"> **INFO: Das Modell {client.chat_model} wurde aktiviert..**\n")
            logger.warning(f"\x1b[31mGEwechselt zu: {client.chat_model}\x1b[0m")

        except Exception as e:
            client.chat_model = original_chat_model
            client.openAI_gpt_engine = original_openAI_gpt_engine
            client.chatbot = client.get_chatbot_model()
            await interaction.followup.send(f"> **Hoppla: etwas ist schiefgelaufen bei dem versuch zum Chatmodell {choices.value} zu wechseln. Warscheinlich ist dieses Chatmodell nicht aktiv!**\n")
            logger.exception(f"Fehler beim Wechseln zum {choices.value} Chatmodel: {e}")


    @client.tree.command(name="reset", description="Setze den Chatverlauf für KönigsGPT zurück!")
    async def reset(interaction: discord.Interaction):
        if client.chat_model == "OFFICIAL":
            client.chatbot.reset()
        elif client.chat_model == "UNOFFICIAL":
            client.chatbot.reset_chat()
        elif client.chat_model == "Bard":
            client.chatbot = client.get_chatbot_model()
        await interaction.response.defer(ephemeral=False)
        await interaction.followup.send("> **INFO: KönigsmineGPT hat alles vergessen.**")
        personas.current_persona = "standard"
        logger.warning(
            "\x1b[31mChatverlauf reset erfolgreich\x1b[0m")

    @client.tree.command(name="hilfe", description="Zeigt die Hilfe für KönigsmineGPT")
    async def help(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        await interaction.followup.send(""":star: **KönigsGPT Standartkommands** \n
        - `/chat [Nachricht]` Schreibe mit KönigsmineGPT!
        - `/draw [beschreibung]` Generiere ein Bild mit Dalle2!
        - `/switchpersona [jailbreak]` Wähle aus optionalen Jailbreaks
                `random`: Wählt einen random Jailbreak aus.
                `chatgpt`: Standard ChatGPT modus
                `dan`: Dan Mode 11.0
                `sda`: Superior DAN
                `confidant`: Evil Confidant
                `based`: BasedGPT v2
                `oppo`: OPPO 
                `dev`: Developer Mode v2 

        - `/private` Aktiviere private Antworten.
        - `/public` Aktiviere öffentliche Antworten.
        - `/replyall` Aktiviere/Deaktiviere Antworten auf alle Nachrichten in diesem Chat.
        - `/reset` Entfernt den Chatverlauf für KönigsGPT!
        - `/chat-model` Ändere zu einen anderen Chatmodell.
                `OFFICIAL`: GPT-3.5 model
                `UNOFFICIAL`: Webseiten ChatGPT
                `Bard`: Google Bard model

By KnuddelTeddy & ChatGPT <3""")

        logger.info(
            "\x1b[31mSomeone needs help!\x1b[0m")

    @client.tree.command(name="draw", description="Generiert ein bild mit Dalle2!")
    async def draw(interaction: discord.Interaction, *, prompt: str):
        if interaction.user == client.user:
            return

        username = str(interaction.user)
        channel = str(interaction.channel)
        logger.info(
            f"\x1b[31m{username}\x1b[0m : Dalle2: [{prompt}] in ({channel})")

        await interaction.response.defer(thinking=True, ephemeral=client.isPrivate)
        try:
            path = await art.draw(prompt)

            file = discord.File(path, filename="image.png")
            title = f'> **{prompt}** - <@{str(interaction.user.mention)}' + '> \n\n'
            embed = discord.Embed(title=title)
            embed.set_image(url="attachment://image.png")

            await interaction.followup.send(file=file, embed=embed)

        except openai.InvalidRequestError:
            await interaction.followup.send(
                "> **Hoppla: Unangemessene Anfrage! :c**")
            logger.info(
            f"\x1b[31m{username}\x1b[0m hat eine UNANGEMESSENE Anfrage gesendet!")

        except Exception as e:
            await interaction.followup.send(
                "> **Hoppla: Irgendetwas ist schiefgelaufen. 😿**")
            logger.exception(f"Fehler beim erstellen eines Biles: {e}")


    @client.tree.command(name="switchpersona", description="Wechselt zwischen optionalen Jailbreaks")
    @app_commands.choices(persona=[
        app_commands.Choice(name="Random", value="random"),
        app_commands.Choice(name="Standard", value="standard"),
        app_commands.Choice(name="Do Anything Now 11.0", value="dan"),
        app_commands.Choice(name="Superior Do Anything", value="sda"),
        app_commands.Choice(name="Evil Confidant", value="confidant"),
        app_commands.Choice(name="BasedGPT v2", value="based"),
        app_commands.Choice(name="OPPO", value="oppo"),
        app_commands.Choice(name="Developer Mode v2", value="dev"),
        app_commands.Choice(name="DUDE V3", value="dude_v3"),
        app_commands.Choice(name="AIM", value="aim"),
        app_commands.Choice(name="UCAR", value="ucar"),
        app_commands.Choice(name="Jailbreak", value="jailbreak")
    ])
    async def switchpersona(interaction: discord.Interaction, persona: app_commands.Choice[str]):
        if interaction.user == client.user:
            return

        await interaction.response.defer(thinking=True)
        username = str(interaction.user)
        channel = str(interaction.channel)
        logger.info(
            f"\x1b[31m{username}\x1b[0m : 'Jailbreak: [{persona.value}]' ({channel})")

        persona = persona.value

        if persona == personas.current_persona:
            await interaction.followup.send(f"> **WARNUNG: `{persona}` ist bereits aktiv!**")

        elif persona == "standard":
            if client.chat_model == "OFFICIAL":
                client.chatbot.reset()
            elif client.chat_model == "UNOFFICIAL":
                client.chatbot.reset_chat()
            elif client.chat_model == "Bard":
                client.chat_model = client.get_chatbot_model()

            personas.current_persona = "standard"
            await interaction.followup.send(
                f"> **INFO: Gewechselt zu: `{persona}`**")

        elif persona == "random":
            choices = list(personas.PERSONAS.keys())
            choice = randrange(0, 6)
            chosen_persona = choices[choice]
            personas.current_persona = chosen_persona
            await responses.switch_persona(chosen_persona, client)
            await interaction.followup.send(
                f"> **INFO: Random gewechselt zu:`{chosen_persona}`**")


        elif persona in personas.PERSONAS:
            try:
                await responses.switch_persona(persona, client)
                personas.current_persona = persona
                await interaction.followup.send(
                f"> **INFO: Gewechselt zu:`{persona}` <3**")
            except Exception as e:
                await interaction.followup.send(
                    "> **Hoppla: Irgendetwas ist schiefgelaufen. Versuch es später erneut! :c**")
                logger.exception(f"Fehler beim wechseln des Jailbreaks:: {e}")

        else:
            await interaction.followup.send(
                f"> **Hoppla: kein verfügbarer Jailbreak namens: `{persona}` 😿**")
            logger.info(
                f'{username} hat einen nicht zur verfügung stehenden Jailbreak angefordert: `{persona}`')

    @client.event
    async def on_message(message):
        if client.is_replying_all == "True":
            if message.author == client.user:
                return
            if client.replying_all_discord_channel_id:
                if message.channel.id == int(client.replying_all_discord_channel_id):
                    username = str(message.author)
                    user_message = str(message.content)
                    channel = str(message.channel)
                    logger.info(f"\x1b[31m{username}\x1b[0m : '{user_message}' ({channel})")
                    await client.send_message(message, user_message)
            else:
                logger.exception("replying_all_discord_channel_id nicht gefunden.")

    TOKEN = os.getenv("DISCORD_BOT_TOKEN")

    client.run(TOKEN)
