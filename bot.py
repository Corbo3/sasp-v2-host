import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from datetime import datetime
import sqlite3
from keep_alive import keep_alive
load_dotenv()
TOKEN = os.getenv("TOKEN")
# --------------------------
# Config / IDs
# --------------------------
BOT_PREFIX = "+"
REPORT_CHANNEL_ID = 1417869757255913614   # Salon pour reports
LOGS_CONSOLE_ID = 1417567250596106261    # Salon logs console
LOGS_DC_ID = 1417567268946317323         # Salon logs actions bot

# --------------------------
# Bot setup
# --------------------------
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)


# --------------------------
# Logs helpers
# --------------------------
async def logs_console(message):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] {message}")
    channel = bot.get_channel(LOGS_CONSOLE_ID)
    if channel:
        await channel.send(f"[{now}] {message}")

async def logs_dc(message):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] {message}")
    channel = bot.get_channel(LOGS_DC_ID)
    if channel:
        await channel.send(f"[{now}] {message}")


# --------------------------
# Events
# --------------------------
@bot.event
async def on_ready():
    # Initialiser le dictionnaire temporaire
    bot.temp_data = {}

    try:
        synced = await bot.tree.sync()
        print(f"📌 Slash commands synchronisées : {len(synced)}")
    except Exception as e:
        print(f"Erreur sync : {e}")

    print(f"✅ Connecté en tant que {bot.user}")
    await logs_console(f"✅ Connecté en tant que {bot.user}")


# --------------------------
# Commande Recrutement
# --------------------------
@bot.command()
async def recrutement(ctx):
    await logs_dc(f"Commande +recrutement utilisée par {ctx.author} (ID: {ctx.author.id})")
    
    embed = discord.Embed(
        title="📢 Recrutement au SASP 📢",
        description=(
            "**Prérequis :**\n"
            "- Ne pas avoir de casier judiciaire\n"
            "- Posséder le permis de conduire\n\n"
            "**Étape 1 :** Remplir le formulaire présent dans le salon <#923645591551107098>\n\n"
            "**Étape 2 :** Vous recevrez un message indiquant si vous êtes admis ou refusé.\n\n"
            "**Étape 3 :** Si vous êtes admis, vous aurez accès à la catégorie recrutement et aux recruteurs.\n\n"
            "**Étape 4 :** Si vous êtes accepté, vous passerez la formation et deviendrez officiellement membre du SASP !\n\n"
            "**Note :** Pour toute question, contactez un recruteur."
        ),
        color=0xc2000a
    )
    embed.set_footer(text="SASP | Protéger et Servir")
    await ctx.send(embed=embed)


# --------------------------
# Report Modal
# --------------------------

DB_PATH = "arme.db"  # Chemin vers la base de données SQLite

# =========================
#   MODALS
# =========================
class SearchModal(discord.ui.Modal, title="🔎 Rechercher une arme"):
    nom = discord.ui.TextInput(label="Nom", required=False)
    prenom = discord.ui.TextInput(label="Prénom", required=False)
    modele = discord.ui.TextInput(label="Modèle", required=False)
    numero_serie = discord.ui.TextInput(label="Numéro de série", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        filters = {
            "nom": str(self.nom).strip(),
            "prenom": str(self.prenom).strip(),
            "modele": str(self.modele).strip(),
            "numero_serie": str(self.numero_serie).strip()
        }

        query = "SELECT nom, prenom, modele, numero_serie FROM armes WHERE 1=1"
        params = []
        if filters["nom"]:
            query += " AND nom LIKE ?"
            params.append(f"%{filters['nom']}%")
        if filters["prenom"]:
            query += " AND prenom LIKE ?"
            params.append(f"%{filters['prenom']}%")
        if filters["modele"]:
            query += " AND modele LIKE ?"
            params.append(f"%{filters['modele']}%")
        if filters["numero_serie"]:
            query += " AND numero_serie LIKE ?"
            params.append(f"%{filters['numero_serie']}%")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        embed = discord.Embed(title="🔎 Résultats de recherche", color=discord.Color.blurple())
        filtres_txt = [f"**{k.capitalize()}**: {v}" for k, v in filters.items() if v]
        embed.add_field(name="Filtres appliqués", value="\n".join(filtres_txt) if filtres_txt else "Aucun filtre", inline=False)

        if rows:
            for row in rows:
                nom, prenom, modele, numero_serie = row
                embed.add_field(
                    name=f"{prenom} {nom}",
                    value=f"**Modèle :** {modele}\n**N° de série :** {numero_serie}",
                    inline=False
                )
                logs_dc(f"Recherche arme : {prenom} {nom} - {modele} ({numero_serie}) par {interaction.user} (ID: {interaction.user.id})")
        else:
            embed.add_field(name="Résultats", value="❌ Aucun résultat trouvé", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)


class AddWeaponModal(discord.ui.Modal, title="➕ Ajouter une arme"):
    nom = discord.ui.TextInput(label="Nom", required=True)
    prenom = discord.ui.TextInput(label="Prénom", required=True)
    modele = discord.ui.TextInput(label="Modèle", required=True)
    numero_serie = discord.ui.TextInput(label="Numéro de série", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO armes (nom, prenom, modele, numero_serie) VALUES (?, ?, ?, ?)",
                (str(self.nom), str(self.prenom), str(self.modele), str(self.numero_serie))
            )
            conn.commit()
            conn.close()
            embed = discord.Embed(
                title="✅ Arme ajoutée",
                description=f"**{self.prenom} {self.nom}** - {self.modele} ({self.numero_serie})",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            logs_dc(f"Arme ajoutée : {self.prenom} {self.nom} - {self.modele} ({self.numero_serie}) par {interaction.user} (ID: {interaction.user.id})")
        except sqlite3.IntegrityError:
            await interaction.response.send_message("❌ Cette arme existe déjà (numéro de série en double).", ephemeral=True)


class RemoveWeaponModal(discord.ui.Modal, title="❌ Retirer une arme"):
    numero_serie = discord.ui.TextInput(label="Numéro de série", placeholder="Numéro unique de l'arme à supprimer", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM armes WHERE numero_serie = ?", (str(self.numero_serie),))
        changes = cursor.rowcount
        conn.commit()
        conn.close()

        if changes > 0:
            embed = discord.Embed(
                title="✅ Arme supprimée",
                description=f"Arme avec N° de série **{self.numero_serie}** supprimée.",
                color=discord.Color.red()
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            logs_dc(f"Arme avec N° de série {self.numero_serie} supprimée par {interaction.user} (ID: {interaction.user.id})")
        else:
            await interaction.response.send_message("❌ Aucune arme trouvée avec ce numéro de série.", ephemeral=True)


# =========================
#   VIEW AVEC BOUTONS
# =========================
class WeaponView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔎 Rechercher", style=discord.ButtonStyle.primary)
    async def search_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SearchModal())

    @discord.ui.button(label="➕ Ajouter", style=discord.ButtonStyle.success)
    async def add_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AddWeaponModal())

    @discord.ui.button(label="❌ Supprimer", style=discord.ButtonStyle.danger)
    async def remove_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RemoveWeaponModal())


# =========================
#   COMMANDE PRINCIPALE
# =========================
@bot.tree.command(name="armes", description="Gérer les armes (rechercher, ajouter, supprimer)")
async def armes(interaction: discord.Interaction):
    view = WeaponView()
    embed = discord.Embed(
        title="Gestion des armes",
        description="Utilisez les boutons ci-dessous pour rechercher, ajouter ou supprimer des armes dans la base de données.",
        color=discord.Color.blue()
    )
    embed.set_footer(text="SASP | Protéger et Servir")
    embed.add_field(name="🔎 Rechercher", value="Rechercher une arme par nom, prénom, modèle ou numéro de série. (Aucun champ est obligatoire)", inline=False)
    embed.add_field(name="➕ Ajouter", value="Ajouter une nouvelle arme à la base de données.", inline=False)
    embed.add_field(name="❌ Supprimer", value="Supprimer une arme existante par son numéro de série.", inline=False)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    








DB_PATH_CIVIL = "civil.db"




# =========================
#   MODALS CIVILS
# =========================
class SearchCivilModal(discord.ui.Modal, title="🔎 Rechercher un civil"):
    nom = discord.ui.TextInput(label="Nom", required=False)
    prenom = discord.ui.TextInput(label="Prénom", required=False)
    telephone = discord.ui.TextInput(label="Téléphone", required=False)
    adresse = discord.ui.TextInput(label="Adresse", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        filters = {
            "nom": str(self.nom).strip(),
            "prenom": str(self.prenom).strip(),
            "telephone": str(self.telephone).strip(),
            "adresse": str(self.adresse).strip()
        }

        query = "SELECT nom, prenom, telephone, adresse FROM civils WHERE 1=1"
        params = []
        if filters["nom"]:
            query += " AND nom LIKE ?"
            params.append(f"%{filters['nom']}%")
        if filters["prenom"]:
            query += " AND prenom LIKE ?"
            params.append(f"%{filters['prenom']}%")
        if filters["telephone"]:
            query += " AND telephone LIKE ?"
            params.append(f"%{filters['telephone']}%")
        if filters["adresse"]:
            query += " AND adresse LIKE ?"
            params.append(f"%{filters['adresse']}%")

        conn = sqlite3.connect(DB_PATH_CIVIL)
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        embed = discord.Embed(
            title="👤 Résultats de recherche - Civils",
            description="Voici les civils correspondant à ta recherche :",
            color=discord.Color.green()
        )
        embed.set_footer(text="Base de données civils | Recherche effectuée")

        filtres_txt = [f"**{k.capitalize()}**: {v}" for k, v in filters.items() if v]
        embed.add_field(
            name="📋 Filtres appliqués",
            value="\n".join(filtres_txt) if filtres_txt else "Aucun filtre",
            inline=False
        )

        if rows:
            for row in rows:
                nom, prenom, telephone, adresse = row
                embed.add_field(
                    name=f"👤 {prenom} {nom}",
                    value=f"📞 **Téléphone :** {telephone}\n🏠 **Adresse :** {adresse}",
                    inline=False
                )
        else:
            embed.add_field(name="Résultats", value="❌ Aucun civil trouvé", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)


class AddCivilModal(discord.ui.Modal, title="➕ Ajouter un civil"):
    nom = discord.ui.TextInput(label="Nom", required=True)
    prenom = discord.ui.TextInput(label="Prénom", required=True)
    telephone = discord.ui.TextInput(label="Téléphone", required=True)
    adresse = discord.ui.TextInput(label="Adresse", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            conn = sqlite3.connect(DB_PATH_CIVIL)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO civils (nom, prenom, telephone, adresse) VALUES (?, ?, ?, ?)",
                (str(self.nom), str(self.prenom), str(self.telephone), str(self.adresse))
            )
            conn.commit()
            conn.close()

            embed = discord.Embed(
                title="✅ Civil ajouté",
                color=discord.Color.green()
            )
            embed.add_field(name="👤 Identité", value=f"{self.prenom} {self.nom}", inline=False)
            embed.add_field(name="📞 Téléphone", value=self.telephone, inline=True)
            embed.add_field(name="🏠 Adresse", value=self.adresse, inline=True)
            embed.set_footer(text="Base de données civils | Ajout réussi")

            await interaction.response.send_message(embed=embed, ephemeral=True)
            logs_dc(f"Civil ajouté : {self.prenom} {self.nom} - {self.telephone} - {self.adresse} par {interaction.user} (ID: {interaction.user.id})")

        except sqlite3.IntegrityError:
            await interaction.response.send_message("❌ Ce civil existe déjà (numéro de téléphone en double ?).", ephemeral=True)


class RemoveCivilModal(discord.ui.Modal, title="❌ Supprimer un civil"):
    telephone = discord.ui.TextInput(label="Numéro de téléphone", placeholder="Téléphone unique du civil", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        conn = sqlite3.connect(DB_PATH_CIVIL)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM civils WHERE telephone = ?", (str(self.telephone),))
        changes = cursor.rowcount
        conn.commit()
        conn.close()

        if changes > 0:
            embed = discord.Embed(
                title="🗑️ Civil supprimé",
                description=f"Le civil avec le numéro **{self.telephone}** a été retiré de la base.",
                color=discord.Color.red()
            )
            embed.set_footer(text="Base de données civils | Suppression réussie")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            logs_dc(f"Civil avec téléphone {self.telephone} supprimé par {interaction.user} (ID: {interaction.user.id})")
        else:
            await interaction.response.send_message("❌ Aucun civil trouvé avec ce téléphone.", ephemeral=True)


# =========================
#   VIEW AVEC BOUTONS
# =========================
class CivilView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔎 Rechercher", style=discord.ButtonStyle.primary)
    async def search_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SearchCivilModal())

    @discord.ui.button(label="➕ Ajouter", style=discord.ButtonStyle.success)
    async def add_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AddCivilModal())

    @discord.ui.button(label="❌ Supprimer", style=discord.ButtonStyle.danger)
    async def remove_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RemoveCivilModal())


# =========================
#   COMMANDE PRINCIPALE
# =========================
@bot.tree.command(name="civils", description="Gérer les civils (rechercher, ajouter, supprimer)")
async def civils(interaction: discord.Interaction):
    embed = discord.Embed(
        title="👥 Gestion des civils",
        description=(
            "Utilise les boutons ci-dessous pour rechercher, ajouter ou supprimer des civils dans la base de données."
        ),
        color=discord.Color.blue()
    ) 
    await interaction.response.send_message(embed=embed, view=CivilView())
    logs_dc(f"Commande /civils utilisée par {interaction.user} (ID: {interaction.user.id})")




rapport_channel = 1419015970684407848  # Salon pour reports


class RapportModal(discord.ui.Modal, title="📝 - Rapport"):
    """
    Cette classe montre comment créer un modal avec des champs TextInput.
    Vous pouvez :
    - Ajouter autant de TextInput que nécessaire
    - Définir required=True/False
    - Ajouter un placeholder ou une longueur max
    """

    destinataire = discord.ui.TextInput(
        label="Destinataire",
        placeholder="Matricule ou nom de la personne concernée",
        required=True,  # Obligatoire ou non
    )

    rapport = discord.ui.TextInput(
        label="Rapport",
        placeholder="...",
        style=discord.TextStyle.paragraph,  # Champ plus grand
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        """
        Cette fonction s'exécute quand l'utilisateur valide le modal.
        Ici vous pouvez :
        - Récupérer les valeurs des champs
        - Envoyer un message ou un embed
        - Interagir avec une base de données
        """
        valeur1 = str(self.destinataire)
        valeur2 = str(self.rapport)
        channel = bot.get_channel(rapport_channel)
        

        # Exemple simple d'embed
        embed = discord.Embed(
            title="Rapport",
            description=f"Destinataire : {valeur1}\nRapport : {valeur2}",
            color=discord.Color.blue()
        )
        if channel:
            await channel.send(f"**Nouveau rapport de {interaction.user.mention}**\n\n**Destinataire :** {valeur1}\n**Rapport :** {valeur2}")
            await logs_dc(f"Rapport envoyé par {interaction.user} (ID: {interaction.user.id}) au destinataire {valeur1}")
        else:
            await logs_dc(f"Erreur : Salon de rapport introuvable pour le rapport de {interaction.user} (ID: {interaction.user.id})")
        await interaction.response.send_message("Votre rapport est envoyé.")  # ephemeral=True pour que seul l'utilisateur voie le message


# =========================
# Exemple de commande qui ouvre le modal
# =========================
@bot.tree.command(name="rapport", description="Faire un rapport auprès d'une personne (à désigner dans le questionnaire)")
async def exemple(interaction: discord.Interaction):
    """
    Cette commande ouvre le modal.
    Vous pouvez :
    - Créer différents modals selon la commande
    - Ajouter des boutons, menus déroulants, etc.
    """
    modal = RapportModal()  # On instancie le modal
    await interaction.response.send_modal(modal)
    logs_dc(f"Commande /rapport utilisée par {interaction.user} (ID: {interaction.user.id})")
































    











keep_alive()
bot.run(TOKEN)
