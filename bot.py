import discord
from discord.ext import commands
from discord import app_commands
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

EMPTY = "⬜"
X = "❌"
O = "⭕"

# ===== WIN =====
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

# ===== VIEW =====
class CaroView(discord.ui.View):
    def __init__(self, p1, p2):
        super().__init__(timeout=600)
        self.players = [p1, p2]
        self.turn = 0
        self.board = [[EMPTY]*10 for _ in range(10)]

        self.select = MoveSelect(self)
        self.add_item(self.select)

    def current_player(self):
        return self.players[self.turn]

    def board_text(self):
        text = "   " + " ".join(str(i) for i in range(10)) + "\n"
        for i, row in enumerate(self.board):
            text += f"{i}  " + " ".join(row) + "\n"
        return f"```{text}```"

# ===== SELECT =====
class MoveSelect(discord.ui.Select):
    def __init__(self, view):
        self.view_ref = view

        options = [
            discord.SelectOption(label=f"{x},{y}", value=f"{x},{y}")
            for x in range(10) for y in range(10)
        ]

        super().__init__(placeholder="Chọn vị trí đánh", options=options[:25])

    async def callback(self, interaction: discord.Interaction):
        view = self.view_ref

        if interaction.user != view.current_player():
            return await interaction.response.send_message("Không phải lượt bạn", ephemeral=True)

        x, y = map(int, self.values[0].split(","))

        if view.board[x][y] != EMPTY:
            return await interaction.response.send_message("Ô đã đánh", ephemeral=True)

        symbol = X if view.turn == 0 else O
        view.board[x][y] = symbol

        if check_win(view.board, x, y, symbol):
            view.clear_items()
            return await interaction.response.edit_message(
                content=view.board_text() + f"\n🏆 {interaction.user.mention} thắng!",
                view=view
            )

        view.turn = 1 - view.turn

        await interaction.response.edit_message(
            content=view.board_text() + f"\nLượt: {view.current_player().mention}",
            view=view
        )

# ===== READY =====
@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Ready")

# ===== COMMAND =====
@bot.tree.command(name="caro", description="Caro UI xịn")
async def caro(interaction: discord.Interaction, opponent: discord.Member):

    view = CaroView(interaction.user, opponent)

    await interaction.response.send_message(
        view.board_text() + f"\nLượt: {interaction.user.mention}",
        view=view
    )

bot.run(os.getenv("TOKEN"))