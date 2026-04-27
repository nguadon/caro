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
class CellButton(discord.ui.Button):
    def __init__(self, x, y):
        super().__init__(label=" ", style=discord.ButtonStyle.secondary)
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

        if check_win(view.board, self.x, self.y, symbol):
            view.disable_all_items()
            return await interaction.response.edit_message(
                content=f"🏆 {interaction.user.mention} thắng!",
                view=view
            )

        view.turn = 1 - view.turn
        view.update_buttons()

        await interaction.response.edit_message(
            content=f"Lượt: {view.current_player().mention} | Trang {view.page+1}/4",
            view=view
        )

# ===== VIEW =====
class CaroView(discord.ui.View):
    def __init__(self, p1, p2):
        super().__init__(timeout=600)
        self.players = [p1, p2]
        self.turn = 0
        self.board = [[EMPTY]*10 for _ in range(10)]
        self.page = 0

        self.update_buttons()

    def current_player(self):
        return self.players[self.turn]

    def update_buttons(self):
        self.clear_items()

        start_x = (self.page // 2) * 5
        start_y = (self.page % 2) * 5

        for i in range(5):
            for j in range(5):
                x = start_x + i
                y = start_y + j

                btn = CellButton(x, y)
                btn.row = i

                if self.board[x][y] != EMPTY:
                    btn.label = self.board[x][y]
                    btn.disabled = True
                    btn.style = discord.ButtonStyle.danger if btn.label == X else discord.ButtonStyle.success

                self.add_item(btn)

        # NAV BUTTON
        self.add_item(NavButton("⬅️", -1))
        self.add_item(NavButton("➡️", 1))

# ===== NAV =====
class NavButton(discord.ui.Button):
    def __init__(self, label, direction):
        super().__init__(label=label, style=discord.ButtonStyle.primary, row=4)
        self.direction = direction

    async def callback(self, interaction: discord.Interaction):
        view: CaroView = self.view

        view.page = (view.page + self.direction) % 4
        view.update_buttons()

        await interaction.response.edit_message(
            content=f"Lượt: {view.current_player().mention} | Trang {view.page+1}/4",
            view=view
        )

# ===== READY =====
@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Bot ready")

# ===== COMMAND =====
@bot.tree.command(name="caro", description="Caro 10x10 (Ultimate)")
async def caro(interaction: discord.Interaction, opponent: discord.Member):

    view = CaroView(interaction.user, opponent)

    await interaction.response.send_message(
        f"🎮 Caro 10x10 | Trang 1/4\nLượt: {interaction.user.mention}",
        view=view
    )

bot.run(os.getenv("TOKEN"))