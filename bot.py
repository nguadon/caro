import discord
from discord.ext import commands
from discord import app_commands
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

EMPTY = "⬜"
X = "❌"
O = "⭕"

# ===== CHECK WIN =====
def check_win(board, x, y, symbol):
    size = len(board)

    def count(dx, dy):
        c = 0
        i, j = x + dx, y + dy
        while 0 <= i < size and 0 <= j < size and board[i][j] == symbol:
            c += 1
            i += dx
            j += dy
        return c

    for dx, dy in [(1,0),(0,1),(1,1),(1,-1)]:
        if 1 + count(dx,dy) + count(-dx,-dy) >= 5:
            return True
    return False

# ===== BUTTON =====
class CaroButton(discord.ui.Button):
    def __init__(self, x, y):
        super().__init__(label=" ", style=discord.ButtonStyle.secondary, row=x)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        view: CaroView = self.view

        if interaction.user != view.current_player():
            return await interaction.response.send_message("Không phải lượt bạn", ephemeral=True)

        if view.board[self.x][self.y] != EMPTY:
            return await interaction.response.send_message("Ô đã đánh", ephemeral=True)

        symbol = X if view.turn == 0 else O
        view.board[self.x][self.y] = symbol

        self.label = symbol
        self.disabled = True
        self.style = discord.ButtonStyle.danger if symbol == X else discord.ButtonStyle.success

        if check_win(view.board, self.x, self.y, symbol):
            view.disable_all_items()
            return await interaction.response.edit_message(
                content=f"🏆 {interaction.user.mention} thắng!",
                view=view
            )

        view.turn = 1 - view.turn

        await interaction.response.edit_message(
            content=f"Lượt: {view.current_player().mention}",
            view=view
        )

# ===== VIEW =====
class CaroView(discord.ui.View):
    def __init__(self, p1, p2):
        super().__init__(timeout=300)
        self.players = [p1, p2]
        self.turn = 0
        self.board = [[EMPTY]*5 for _ in range(5)]

        for x in range(5):
            for y in range(5):
                self.add_item(CaroButton(x, y))

    def current_player(self):
        return self.players[self.turn]

# ===== SYNC =====
@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Slash synced")

# ===== COMMAND =====
@bot.tree.command(name="caro", description="Chơi caro (click)")
async def caro(interaction: discord.Interaction, opponent: discord.Member):

    view = CaroView(interaction.user, opponent)

    await interaction.response.send_message(
        f"🎮 Caro 5x5\nLượt: {interaction.user.mention}",
        view=view
    )

bot.run(os.getenv("TOKEN"))