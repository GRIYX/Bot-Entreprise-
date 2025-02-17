import discord
from discord.ext import commands
from discord.ui import View, Button
import asyncio
import datetime
import json
import os
from dotenv import load_dotenv
# from keep_alive import keep_alive

# --------------------------
# Token
# --------------------------

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# --------------------------
# Instants
# --------------------------

intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ----------------------------------------------------------------
# Début de programme !
# ----------------------------------------------------------------

# --------------------------
# Variable
# --------------------------

# Dictionnaire pour stocker les demandes en attente
pending_requests = {}

# Configuration des entreprises et rôles
companies = {
    "LSPD": {"role": "Employé LSPD", "boss_roles": ["Patron LSPD", "Co-Patron LSPD"]},
    "BCSO": {"role": "Employé BCSO", "boss_roles": ["Patron BCSO", "Co-Patron BCSO"]},
    "Gruppe 6": {"role": "Employé Gruppe 6", "boss_roles": ["Patron Gruppe 6", "Co-Patron Gruppe 6"]},
    "EMS": {"role": "Employé EMS", "boss_roles": ["Patron EMS", "Co-Patron EMS"]},
    "Bennys": {"role": "Employé Bennys", "boss_roles": ["Patron Bennys", "Co-Patron Bennys"]},
    "Fermier": {"role": "Employé Fermier", "boss_roles": ["Patron Fermier", "Co-Patron Fermier"]},
    "Burger Shot": {"role": "Employé Burger Shot", "boss_roles": ["Patron Burger Shot", "Co-Patron Burger Shot"]},
    "Taco Fast-food": {"role": "Employé Taco Fast-food", "boss_roles": ["Patron Taco Fast-food", "Co-Patron Taco Fast-food"]},
    "Pearls": {"role": "Employé Pearls", "boss_roles": ["Patron Pearls", "Co-Patron Pearls"]},
    "Pizzeria": {"role": "Employé Pizzeria", "boss_roles": ["Patron Pizzeria", "Co-Patron Pizzeria"]},
    "Vigneron": {"role": "Employé Vigneron", "boss_roles": ["Patron Vigneron", "Co-Patron Vigneron"]},
    "Tabac": {"role": "Employé Tabac", "boss_roles": ["Patron Tabac", "Co-Patron Tabac"]},
    "Distillerie": {"role": "Employé Distillerie", "boss_roles": ["Patron Distillerie", "Co-Patron Distillerie"]},
    "Taxi": {"role": "Employé Taxi", "boss_roles": ["Patron Taxi", "Co-Patron Taxi"]},
    "Pawn-Shop": {"role": "Employé Pawn-Shop", "boss_roles": ["Patron Pawn-Shop", "Co-Patron Pawn-Shop"]},
    "Galaxy": {"role": "Employé Galaxy", "boss_roles": ["Patron Galaxy", "Co-Patron Galaxy"]},
    # Ajoute d'autres entreprises ici
}

# --------------------------
# Commande demande de role
# --------------------------


# Commande pour demander un rôle
@bot.command()
async def roles(ctx, company_name: str):
    company_name = company_name.capitalize()
    
    if company_name not in companies:
        await ctx.send(f"❌ L'entreprise `{company_name}` n'existe pas.")
        return
    
    role_name = companies[company_name]["role"]
    boss_roles = companies[company_name]["boss_roles"]
    
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role in ctx.author.roles:
        await ctx.send(f"✅ Tu as déjà le rôle `{role_name}`.")
        return
    
    boss_members = [member for member in ctx.guild.members if any(discord.utils.get(member.roles, name=role) for role in boss_roles)]
    if not boss_members:
        await ctx.send(f"❌ Aucun Patron ou Co-Patron disponible pour `{company_name}`.")
        return

    # Embed de validation
    embed = discord.Embed(title="Demande de rôle", description=f"{ctx.author.mention} demande le rôle `{role_name}`.", color=discord.Color.blue())
    embed.add_field(name="Entreprise", value=company_name, inline=True)
    embed.add_field(name="Demandeur", value=ctx.author.mention, inline=True)
    embed.set_footer(text="Un Patron ou Co-Patron doit valider cette demande.")

    # Boutons Accepter/Refuser
    view = RoleRequestView(ctx.author, role, boss_roles, ctx.channel)
    message = await ctx.send(embed=embed, view=view)
    
    # Ajouter à la liste des demandes en attente
    pending_requests[message.id] = view
    

# Gestionnaire des boutons de validation
class RoleRequestView(discord.ui.View):
    def __init__(self, requester, role, boss_roles, channel):
        super().__init__(timeout=None)
        self.requester = requester
        self.role = role
        self.boss_roles = boss_roles
        self.channel = channel

    @discord.ui.button(label="✅ Accepter", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any(discord.utils.get(interaction.user.roles, name=role) for role in self.boss_roles):
            await interaction.response.send_message("❌ Tu n'as pas la permission d'accepter cette demande.", ephemeral=True)
            return

        await self.requester.add_roles(self.role)
        await interaction.response.edit_message(content=f"✅ {self.requester.mention} a reçu le rôle `{self.role.name}`.", view=None)
        await self.channel.send(f"✅ {self.requester.mention}, ta demande pour `{self.role.name}` a été acceptée !")
        self.stop()

    @discord.ui.button(label="❌ Refuser", style=discord.ButtonStyle.red)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any(discord.utils.get(interaction.user.roles, name=role) for role in self.boss_roles):
            await interaction.response.send_message("❌ Tu n'as pas la permission de refuser cette demande.", ephemeral=True)
            return
        
        await interaction.response.edit_message(content=f"❌ La demande de {self.requester.mention} pour `{self.role.name}` a été refusée.", view=None)
        await self.channel.send(f"❌ {self.requester.mention}, ta demande pour `{self.role.name}` a été refusée.")
        self.stop()

# --------------------------
# Message Entreprise setup 
# --------------------------

@bot.command()
async def message(ctx):

    embed2 = discord.Embed(title="Demande de rôle", description=f"{ctx.author.mention} demande le rôle .", color=discord.Color.blue())
    embed2.add_field(name="Entreprise", value=ctx.author.mention, inline=True)
    embed2.add_field(name="Demandeur", value=ctx.author.mention, inline=True)
    embed2.add_field(name="Demandeur", value=ctx.author.mention, inline=True)
    embed2.add_field(name="Demandeur2", value=ctx.author.mention)
    embed2.add_field(name="Demandeur3", value=ctx.author.mention)
    embed2.set_footer(text="Un Patron ou Co-Patron doit valider cette demande.")

    await ctx.send(embed=embed2)



# --------------------------
# @on_ready 
# --------------------------

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user}")

# ----------------------------------------------------------------
# Fin de programme !
# ----------------------------------------------------------------


# keep_alive()
bot.run(token=token)